import datetime
from graphQL import hexGraphQL
from decimal import Decimal


class Rapport:
    def __init__(self, address, prices):
        self.rapport = {
            "address": address
            , "dateCreated":  str(datetime.datetime.now())
            , "totalHexBuys": 0
            , "totalUsdcBuys": 0
            , "totalHexSells": 0
            , "totalUsdcSells": 0
            , "pOrL": ""  # profit or loss
            , "leftoverUsdcIfSold": 0
            # usdc value if account balance is liquidated vs the differences between buys/sells
            , "currentUsdcValue": 0  # usdc value if account balance is liquidated
            , "stakedHex": 0
            , "paidOutHex": 0
            , "paidOutUsdcCurrentWorth": 0
            , "paidOutUsdcAtEndWorth": 0
            , "interestHex": 0
            , "interestUsdcCurrentWorth": 0
            , "hexDifference": 0
            , "usdcDifference": 0
        }
        self.buys = self.build_buys(prices)  # all transfers into address
        self.sells = self.build_sells(prices)  # all transfers out of address
        self.build_stake_info(prices)  # builds stake info
        self.build_difference(prices)  # builds differences between buys sells and earned interest

    @staticmethod
    def merge(dict1, dict2):
        return dict2.update(dict1)

    @staticmethod
    def closest(lst, K):
        return lst[min(range(len(lst)), key=lambda i: abs(int(lst[i]['time']) - K))]

    def build_buys(self, uniswap_prices):
        r = self.rapport
        where = """
                   , to: "{0}"
                   
                """
        where = where.format(r['address'])
        # grab all transfers to the address
        hex_buyer_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', 1,
                                                                                where)

        for buy_transfer in hex_buyer_data_results:
            usdc = self.closest(uniswap_prices, int(buy_transfer['timestamp']))[
                'close']  # find closest uniswap data point
            usdc_value = float(usdc) * (int(buy_transfer['value']) / 100000000)
            r['totalHexBuys'] += Decimal(buy_transfer['value'])
            r['totalUsdcBuys'] += usdc_value
            closest_value = {
                "usdcPriceAt": usdc
                , "usdcValue": usdc_value
                , "transactionType": "buy"
            }
            self.merge(closest_value, buy_transfer)
            #print(buy_transfer)
        r['totalHexBuys'] = r['totalHexBuys'] / 100000000

        return hex_buyer_data_results

    def build_sells(self, uniswap_prices):
        r = self.rapport
        where = """
               , from: "{0}"
               , to_not:"0x0000000000000000000000000000000000000000"
               """
        where = where.format(r['address'])
        # grab all transfers from the address
        hex_seller_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', 1,
                                                                                 where)

        for sell_transfer in hex_seller_data_results:
            usdc = self.closest(uniswap_prices, int(sell_transfer['timestamp']))['close']  # find closest uniswap data point
            usdc_value = float(usdc) * (int(sell_transfer['value']) / 100000000)
            r['totalHexSells'] += int(sell_transfer['value'])
            r['totalUsdcSells'] += usdc_value
            closest_value = {
                "usdcPriceAt": usdc
                , "usdcValue": usdc_value
                , "transactionType": "sell"
            }
            self.merge(closest_value, sell_transfer)
            #print(sell_transfer)
        r['totalHexSells'] /= 100000000

        return hex_seller_data_results

    def build_difference(self, uniswap_prices):
        r = self.rapport
        r['hexDifference'] = r['totalHexBuys'] - Decimal(r['totalHexSells']) + Decimal(r['interestHex'])
        r['usdcDifference'] = r['totalUsdcBuys'] - r['totalUsdcSells']
        current_hex_per_usd = float(uniswap_prices[len(uniswap_prices) - 1]['close'])
        r['currentUsdcValue'] = current_hex_per_usd * float(r['hexDifference']) + r['interestUsdcCurrentWorth']
        r['leftoverUsdcIfSold'] = r['currentUsdcValue'] + r['usdcDifference']
        if r['leftoverUsdcIfSold'] > 0:
            r['pOrL'] = "PROFIT"
        else:
            r['pOrL'] = "LOSS"

    def print_me(self):
        r = self.rapport
        print("---Stakes---")
        print("Currently Staked - {:,} HEX".format(r['stakedHex']))
        print("Current Interest - {:,} HEX".format(r['interestHex']))
        print("Total Interest Paid Out - {:,} HEX".format(r['paidOutHex']))
        print("Total Interest Paid Out (current worth) - ${:,.2f}".format(r['paidOutUsdcCurrentWorth']))
        print("---Stakes---\n")

        print("---Buys/Adds---")
        print("Total Bought/Add - {:,} HEX".format(r['totalHexBuys']))
        print("Total Bought/Add - ${:,.2f}".format(r['totalUsdcBuys']))
        print("---Buys/Adds---\n")

        print("---Sells/Removes---")
        print("Total Sold/Remove - {:,} HEX".format(r['totalHexSells']))
        print("Total Sold/Remove - ${:,.2f}".format(r['totalUsdcSells']))
        print("---Sells/Removes---\n")

        print("---Difference---")
        print("{:,} HEX".format(r['hexDifference']))
        print("${:,.2f}".format(r['usdcDifference']))
        print("${:,.2f} USD is the current value".format(r['currentUsdcValue']))
        print("${:,.2f} is left if sold".format(r['leftoverUsdcIfSold']) + " (" + r['pOrL'] + ")")
        print("---Difference---\n")

    @staticmethod
    def calc_big_pay_day(stake):
        unclaimed_sats = 1786651846416372
        day_stake_shares_total = 50499329839740027369
        hearts_per_satoshi = 10000
        big_slice = unclaimed_sats * hearts_per_satoshi
        big_slice *= int(stake['stakeShares'])
        big_slice /= Decimal(day_stake_shares_total)
        return big_slice

    @staticmethod
    def calc_adopt_bonus(interest):
        claimed_btc_count = Decimal(30716)
        claimable_btc_count = Decimal(27997742)
        viral_amount = claimed_btc_count / claimable_btc_count
        viral_amount *= interest

        claimable_sats_total = Decimal(910087996911001)
        claimed_sats_total = Decimal(25673397100358)
        crit_amount = claimed_sats_total / claimable_sats_total
        crit_amount *= interest

        return crit_amount + viral_amount

    def calc_interest(self, stake, global_daily_payout):
        stake_interest = 0
        for day in global_daily_payout:
            if int(stake['endDay']) > int(day['endDay']) > int(stake['startDay']):
                payout_per_share = Decimal(day['payout']) / Decimal(day['shares'])
                stake_shares = int(stake['stakeShares'])
                payout = stake_shares * payout_per_share
                stake_interest += payout

        if int(stake['startDay']) <= 352 and int(stake['endDay']) > 352:
            stake_interest += self.calc_big_pay_day(stake)
            stake_interest += self.calc_adopt_bonus(stake_interest)
        stake_interest /= 100000000
        return Decimal(stake_interest)

    def build_stake_info(self, uniswap_prices):
        r = self.rapport
        where = """
                    , stakerAddr:"{0}"
               """
        where = where.format(r['address'])
        stakes = hexGraphQL.query_cycle_by_generic_number_field('stakeStarts', 'stakeId', 0, where)
        daily_data_results = hexGraphQL.query_cycle('dailyDataUpdates')
        current_hex_per_usd = float(uniswap_prices[len(uniswap_prices) - 1]['close'])

        for stake in stakes:
            if stake['stakeEnd'] is not None:
                payout = int(stake['stakeEnd']['payout']) - int(stake['stakeEnd']['penalty'])
                usdc = self.closest(uniswap_prices, int(stake['stakeEnd']['timestamp']))['close']
                usdc_value = float(usdc) * (payout / 100000000)
                r['paidOutHex'] += payout
                r['paidOutUsdcAtEndWorth'] += usdc_value
            else:
                r['stakedHex'] += int(stake['stakedHearts'])
                r['interestHex'] += self.calc_interest(stake, daily_data_results)
        r['paidOutHex'] /= 100000000
        r['stakedHex'] /= 100000000
        r['paidOutUsdcCurrentWorth'] = current_hex_per_usd * r['paidOutHex']
        r['interestHex'] = float(r['interestHex'])
        r['interestUsdcCurrentWorth'] = current_hex_per_usd * r['interestHex']

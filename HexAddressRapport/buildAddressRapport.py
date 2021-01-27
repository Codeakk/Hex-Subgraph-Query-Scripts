from HexAddressRapport.uniswapPricesHandler import Uniswap_handler
from graphQL import hexGraphQL
from decimal import Decimal

# 0xeBC1AD03D8ea7402692b759DEd8e8CC537884659 (79 transactions)
# 0x392b95795a73a71a4379a1920b0ae360089f1047 (rich boi)
# 0x34F48C38695EfE97f192aD8a4B3215e3544C6597 (buys then stakes)
# 0x55d5c232d921b9eaa6b37b5845e439acd04b4dba eth uniswap 2
# 0xf6dcdce0ac3001b2f67f750bc64ea5beb37b5824 usdc uniswap 2
# 0x0000000000000000000000000000000000000000

class Rapport:
    def __init__(self, address, prices):
        self.address = address
        self.total_buys = {  # collects transfer totals into address
            "totalHexBuys": 0
            , "totalUsdcBuys": 0
        }
        self.total_sells = {  # collects transfer totals out of address
            "totalHexSells": 0
            , "totalUsdcSells": 0
        }
        self.p_or_l = ""  # profit or loss
        self.leftover_usdc_if_sold = 0  # usdc value if account balance is liquidated vs the differences between buys
        # and sells
        self.current_usdc_value = 0  # usdc value if account balance is liquidated
        self.buys = self.build_buys(prices)  # all transfers into address
        self.sells = self.build_sells(prices)  # all transfers out of address
        self.stake_info = self.build_stake_info(prices)  # holds stake info
        self.differences = self.build_difference(prices)  # holds differences between buys sells and earned interest

    @staticmethod
    def merge(dict1, dict2):
        return dict2.update(dict1)

    @staticmethod
    def closest(lst, K):
        return lst[min(range(len(lst)), key=lambda i: abs(int(lst[i]['time']) - K))]

    def build_buys(self, uniswap_prices):
        where = """
                   , to: "{0}"
                   
                """
        where = where.format(self.address)
        # grab all transfers to the address
        hex_buyer_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', 1576368000,
                                                                                where)
        total_buys = {
            "totalHexBuys": 0
            , "totalUsdcBuys": 0
        }
        for item in hex_buyer_data_results:
            usdc = self.closest(uniswap_prices, int(item['timestamp']))['close']  # find closest uniswap data point
            usdc_value = float(usdc) * (int(item['value']) / 100000000)
            total_buys['totalHexBuys'] += int(item['value'])
            total_buys['totalUsdcBuys'] += usdc_value
            closest_value = {
                "usdcPriceAt": usdc
                , "usdcValue": usdc_value
                , "transactionType": "buy"
            }
            self.merge(closest_value, item)
        total_buys['totalHexBuys'] = total_buys['totalHexBuys'] / 100000000
        self.total_buys = total_buys
        return hex_buyer_data_results

    def build_sells(self, uniswap_prices):
        where = """
               , from: "{0}"
               , to_not:"0x0000000000000000000000000000000000000000"
               """
        where = where.format(self.address)
        # grab all transfers from the address
        hex_seller_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', 1576368000,
                                                                                 where)

        total_sells = {
            "totalHexSells": 0
            , "totalUsdcSells": 0
        }
        for item in hex_seller_data_results:
            usdc = self.closest(uniswap_prices, int(item['timestamp']))['close']  # find closest uniswap data point
            usdc_value = float(usdc) * (int(item['value']) / 100000000)
            total_sells['totalHexSells'] += int(item['value'])
            total_sells['totalUsdcSells'] += usdc_value
            closest_value = {
                "usdcPriceAt": usdc
                , "usdcValue": usdc_value
                , "transactionType": "sell"
            }
            self.merge(closest_value, item)
        total_sells['totalHexSells'] /= 100000000
        self.total_sells = total_sells
        return hex_seller_data_results

    def build_difference(self, uniswap_prices):
        differences = {
            "hex": self.total_buys['totalHexBuys'] - self.total_sells['totalHexSells'] + self.stake_info['interestHex']
            , "usdc": 0
        }

        if self.total_buys['totalUsdcBuys'] < self.total_sells['totalUsdcSells']:  # usdc cost of buys less than sells
            self.p_or_l = "PROFIT"
            differences['usdc'] = self.total_sells['totalUsdcSells'] - self.total_buys['totalUsdcBuys']
        else:  # usdc cost of buys more than sells
            self.p_or_l = "LOSS"
            differences['usdc'] = self.total_buys['totalUsdcBuys'] - self.total_sells['totalUsdcSells']

        current_hex_per_usd = float(uniswap_prices[len(uniswap_prices) - 1]['close'])
        self.current_usdc_value = current_hex_per_usd * float(differences['hex']) + self.stake_info['interestUsdcCurrentWorth']
        self.leftover_usdc_if_sold = self.current_usdc_value - differences['usdc']

        return differences

    def print_me(self):

        print("---Stakes---")
        print("Currently Staked - {:,} HEX".format(self.stake_info['stakedHex']))
        print("Current Interest - {:,} HEX".format(self.stake_info['interestHex']))
        print("Total Interest Paid Out - {:,} HEX".format(self.stake_info['paidOutHex']))
        print("Total Interest Paid Out (current worth) - ${:,.2f}".format(self.stake_info['paidOutUsdcCurrentWorth']))
        print("---Stakes---\n")

        print("---Buys/Adds---")
        print("Total Bought/Add - {:,} HEX".format(self.total_buys['totalHexBuys']))
        print("Total Bought/Add - ${:,.2f}".format(self.total_buys['totalUsdcBuys']))
        print("---Buys/Adds---\n")

        print("---Sells/Removes---")
        print("Total Sold/Remove - {:,} HEX".format(self.total_sells['totalHexSells']))
        print("Total Sold/Remove - ${:,.2f}".format(self.total_sells['totalUsdcSells']))
        print("---Sells/Removes---\n")

        print("---Difference---")
        print("{:,} HEX".format(self.differences['hex']))
        print("${:,.2f}".format(self.differences['usdc']) + " in " + self.p_or_l)
        print("${:,.2f} USD is the current value".format(self.current_usdc_value))
        print("${:,.2f} is left if sold".format(self.leftover_usdc_if_sold))
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
        for item in global_daily_payout:
            if int(stake['endDay']) > int(item['endDay']) > int(stake['startDay']):
                payout_per_share = Decimal(item['payout']) / Decimal(item['shares'])
                stake_shares = int(stake['stakeShares'])
                payout = stake_shares * payout_per_share
                stake_interest += payout

        if int(stake['startDay']) <= 352 and int(stake['endDay']) > 352:
            stake_interest += self.calc_big_pay_day(stake)
            stake_interest += self.calc_adopt_bonus(stake_interest)
        stake_interest /= 100000000
        return Decimal(stake_interest)

    def build_stake_info(self, uniswap_prices):
        where = """
                    , stakerAddr:"{0}"
               """
        where = where.format(self.address)
        stakes = hexGraphQL.query_cycle_by_generic_number_field('stakeStarts', 'stakeId', 0, where)
        daily_data_results = hexGraphQL.query_cycle('dailyDataUpdates')
        current_hex_per_usd = float(uniswap_prices[len(uniswap_prices) - 1]['close'])
        stake_totals = {
            "stakedHex": 0
            , "paidOutHex": 0
            , "paidOutUsdcCurrentWorth": 0
            , "paidOutUsdcAtEndWorth": 0
            , "interestHex": 0
            , "interestUsdcCurrentWorth": 0
        }
        for item in stakes:
            if item['stakeEnd'] is not None:
                payout = int(item['stakeEnd']['payout']) - int(item['stakeEnd']['penalty'])
                usdc = self.closest(uniswap_prices, int(item['stakeEnd']['timestamp']))['close']
                usdc_value = float(usdc) * (payout / 100000000)
                stake_totals['paidOutHex'] += payout
                stake_totals['paidOutUsdcAtEndWorth'] += usdc_value
            else:
                stake_totals['stakedHex'] += int(item['stakedHearts'])
                stake_totals['interestHex'] += self.calc_interest(item, daily_data_results)
        stake_totals['paidOutHex'] /= 100000000
        stake_totals['stakedHex'] /= 100000000
        stake_totals['paidOutUsdcCurrentWorth'] = current_hex_per_usd * stake_totals['paidOutHex']
        stake_totals['interestHex'] = float(stake_totals['interestHex'])
        stake_totals['interestUsdcCurrentWorth'] = current_hex_per_usd * stake_totals['interestHex']
        return stake_totals


uni_prices = Uniswap_handler().prices
addr_rap = Rapport("0x34F48C38695EfE97f192aD8a4B3215e3544C6597", uni_prices)
addr_rap.print_me()

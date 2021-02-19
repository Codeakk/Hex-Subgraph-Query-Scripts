import datetime
from graphQL import hexGraphQL
from decimal import Decimal


class Rapport:
    def __init__(self, address, prices):
        self.report = {
            "address": address
            , "pOrL": ""
            , "dateCreated": str(datetime.datetime.now())
            , "leftoverUsdcIfSold": 0
            , "currentUsdcValue": 0
            , "stakeData": {
                "startedStakedHex": 0
                , "finishedStakedHex": 0
                , "stakedHex": 0
                , "paidOutHex": 0
                , "paidOutUsdcCurrentWorth": 0
                , "paidOutUsdcAtEndWorth": 0
                , "interestHex": 0
                , "interestUsdcCurrentWorth": 0
            }
            , "totalData": {
            }
            , "differenceData": {
                "hexDifference": 0
                , "usdcDifference": 0
            }
            , "buyData": {
                "totalHex": 0
                , "totalUsdc": 0
                , "stakeEndTotal": {
                    "hex": 0
                    , "usdc": 0
                }
                , "xfLobbyExitTotal": {
                    "hex": 0
                    , "usdc": 0
                }
                , "btcAddressClaimTotal": {
                    "hex": 0
                    , "usdc": 0
                }
                , "uniswapV1": {
                    "hex": 0
                    , "usdc": 0
                }
                , "uniswapV2": {
                    "hex": 0
                    , "usdc": 0
                }
                , "unknownTotal": {
                    "hex": 0
                    ,"usdc": 0
                }
            }
            , "sellData": {
                "totalHex": 0
                , "totalUsdc": 0
                , "stakeStartTotal": {
                    "hex": 0
                    , "usdc": 0
                }
                , "uniswapV1": {
                    "hex": 0
                    , "usdc": 0
                }
                , "uniswapV2": {
                    "hex": 0
                    , "usdc": 0
                }
                , "unknownTotal": {
                    "hex": 0
                    , "usdc": 0
                }
            }
        }
        self.buys = self.build_buys(prices)  # all transfers into address
        self.sells = self.build_sells(prices)  # all transfers out of address
        self.build_stake_info(prices)  # builds stake info
        self.build_difference(prices)  # builds differences between buys sells and earned interest

    @staticmethod
    def hearts_to_hex(num):
        return num / 100000000

    @staticmethod
    def hex_to_hearts(num):
        return num * 100000000

    @staticmethod
    def merge(dict1, dict2):
        return dict2.update(dict1)

    @staticmethod
    def closest(lst, K):
        return lst[min(range(len(lst)), key=lambda i: abs(int(lst[i]['time']) - K))]

    def build_buys(self, uniswap_prices):
        r = self.report
        rbd = r['buyData']
        where = """
                    , to: "{0}"
                """
        where = where.format(r['address'])
        # grab all transfers to the address
        hex_buyer_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', 1,
                                                                                where)

        for buy_transfer in hex_buyer_data_results:
            #print(buy_transfer)
            found = False
            usdc = self.closest(uniswap_prices, int(buy_transfer['timestamp']))['close']
            if buy_transfer['methodId'] == 'stakeEnd':
                rbd['stakeEndTotal']['hex'] += Decimal(buy_transfer['value'])
                rbd['stakeEndTotal']['usdc'] += float(usdc) * (self.hearts_to_hex(int(buy_transfer['value'])))
                continue

            if buy_transfer['methodId'] == 'xfLobbyExit':
                rbd['xfLobbyExitTotal']['hex'] += Decimal(buy_transfer['value'])
                rbd['xfLobbyExitTotal']['usdc'] += float(usdc) * (self.hearts_to_hex(int(buy_transfer['value'])))
            if buy_transfer['methodId'] == 'btcAddressClaim':
                rbd['btcAddressClaimTotal']['hex'] += Decimal(buy_transfer['value'])
                rbd['btcAddressClaimTotal']['usdc'] += float(usdc) * (self.hearts_to_hex(int(buy_transfer['value'])))
            v1_contracts = ["0x05cde89ccfa0ada8c88d5a23caaa79ef129e7883"]
            if buy_transfer['from'] in v1_contracts:
                rbd['uniswapV1']['hex'] += Decimal(buy_transfer['value'])
                rbd['uniswapV1']['usdc'] += float(usdc) * (self.hearts_to_hex(int(buy_transfer['value'])))
                found = True
            v2_contracts = ["0xf6dcdce0ac3001b2f67f750bc64ea5beb37b5824", "0x55d5c232d921b9eaa6b37b5845e439acd04b4dba"]
            if buy_transfer['from'] in v2_contracts:
                rbd['uniswapV2']['hex'] += Decimal(buy_transfer['value'])
                rbd['uniswapV2']['usdc'] += float(usdc) * (self.hearts_to_hex(int(buy_transfer['value'])))
                found = True
            if buy_transfer['methodId'] is None and found is False:
                rbd["unknownTotal"]['hex'] += Decimal(buy_transfer['value'])
                rbd['unknownTotal']['usdc'] += float(usdc) * (self.hearts_to_hex(int(buy_transfer['value'])))
            usdc_value = float(usdc) * (self.hearts_to_hex(int(buy_transfer['value'])))
            rbd['totalHex'] += Decimal(buy_transfer['value'])
            rbd['totalUsdc'] += usdc_value
            closest_value = {
                "usdcPriceAt": usdc
                , "usdcValue": usdc_value
                , "transactionType": "buy"
            }
            self.merge(closest_value, buy_transfer)
        rbd["uniswapV1"]['hex'] = self.hearts_to_hex(rbd["uniswapV1"]['hex'])
        rbd["uniswapV2"]['hex'] = self.hearts_to_hex(rbd["uniswapV2"]['hex'])
        rbd["btcAddressClaimTotal"]['hex'] = self.hearts_to_hex(rbd["btcAddressClaimTotal"]['hex'])
        rbd["unknownTotal"]['hex'] = self.hearts_to_hex(rbd["unknownTotal"]['hex'])
        rbd['xfLobbyExitTotal']['hex'] = self.hearts_to_hex(rbd["xfLobbyExitTotal"]['hex'])
        rbd['stakeEndTotal']['hex'] = self.hearts_to_hex(rbd["stakeEndTotal"]['hex'])
        rbd['totalHex'] = self.hearts_to_hex(rbd["totalHex"])

        return hex_buyer_data_results

    def build_sells(self, uniswap_prices):
        r = self.report
        rsd = r['sellData']
        where = """
                , from: "{0}"
               """

        where = where.format(r['address'])
        # grab all transfers from the address
        hex_seller_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', 1,
                                                                                 where)

        for sell_transfer in hex_seller_data_results:
            print(sell_transfer)
            found = False
            usdc = self.closest(uniswap_prices, int(sell_transfer['timestamp']))['close']
            if sell_transfer['methodId'] == 'stakeStart':
                rsd['stakeStartTotal']['hex'] += Decimal(sell_transfer['value'])
                rsd['stakeStartTotal']['usdc'] += float(usdc) * (self.hearts_to_hex(int(sell_transfer['value'])))
                continue
            v1_contracts = ["0x05cde89ccfa0ada8c88d5a23caaa79ef129e7883"]
            if sell_transfer['to'] in v1_contracts:
                rsd['uniswapV1']['hex'] += Decimal(sell_transfer['value'])
                rsd['uniswapV1']['usdc'] += float(usdc) * (self.hearts_to_hex(int(sell_transfer['value'])))
                found = True
            v2_contracts = ["0xf6dcdce0ac3001b2f67f750bc64ea5beb37b5824", "0x55d5c232d921b9eaa6b37b5845e439acd04b4dba"]
            if sell_transfer['to'] in v2_contracts:
                rsd['uniswapV2']['hex'] += Decimal(sell_transfer['value'])
                rsd['uniswapV2']['usdc'] += float(usdc) * (self.hearts_to_hex(int(sell_transfer['value'])))
                found = True
            if sell_transfer['methodId'] is None and found is False:
                rsd["unknownTotal"]['hex'] += Decimal(sell_transfer['value'])
                rsd['unknownTotal']['usdc'] += float(usdc) * (self.hearts_to_hex(int(sell_transfer['value'])))
            usdc_value = float(usdc) * (self.hearts_to_hex(int(sell_transfer['value'])))
            rsd['totalHex'] += int(sell_transfer['value'])
            rsd['totalUsdc'] += usdc_value
            closest_value = {
                "usdcPriceAt": usdc
                , "usdcValue": usdc_value
                , "transactionType": "sell"
            }
            self.merge(closest_value, sell_transfer)
        rsd["uniswapV1"]['hex'] = self.hearts_to_hex(rsd["uniswapV1"]['hex'])
        rsd["uniswapV2"]['hex'] = self.hearts_to_hex(rsd["uniswapV2"]['hex'])
        rsd["unknownTotal"]['hex'] = self.hearts_to_hex(rsd["unknownTotal"]['hex'])
        rsd['stakeStartTotal']['hex'] = self.hearts_to_hex(rsd["stakeStartTotal"]['hex'])
        rsd['totalHex'] = self.hearts_to_hex(rsd["totalHex"])

        return hex_seller_data_results

    def build_difference(self, uniswap_prices):
        r = self.report
        rstd = r['stakeData']
        rbd = r['buyData']
        rsd = r['sellData']
        rdd = r['differenceData']
        rdd['hexDifference'] = Decimal(rbd['totalHex']) - Decimal(rsd['totalHex']) + Decimal(
            rstd['interestHex'])
        if rdd['hexDifference'] < 0:
            rdd['hexDifference'] = 0
        rdd['usdcDifference'] = rbd['totalUsdc'] - rsd['totalUsdc']
        if rbd['totalUsdc'] > rsd['totalUsdc']:
            rdd['usdcDifference'] *= -1
        current_hex_per_usd = float(uniswap_prices[len(uniswap_prices) - 1]['close'])
        r['currentUsdcValue'] = current_hex_per_usd * float(rdd['hexDifference'])
        r['leftoverUsdcIfSold'] = r['currentUsdcValue'] + rdd['usdcDifference']
        if r['leftoverUsdcIfSold'] > 0:
            r['pOrL'] = "PROFIT"
        else:
            r['pOrL'] = "LOSS"

    def print_me(self):
        r = self.report
        rstd = r['stakeData']
        rbd = r['buyData']
        rsd = r['sellData']
        rdd = r['differenceData']

        print("---Stakes---")
        print("Started Stakes - {:,} HEX".format(rstd['startedStakedHex']))
        print("Finished Stakes - {:,} HEX".format(rstd['finishedStakedHex']))
        print("Currently Staked - {:,} HEX".format(rstd['stakedHex']))
        print("Current Interest - {:,} HEX ".format(rstd['interestHex']) + "(${:,.2f})".format(rstd['interestUsdcCurrentWorth']))
        print("Total Interest Paid Out - {:,} HEX".format(rstd['paidOutHex']))
        print("Total Interest Paid Out (current worth) - ${:,.2f}".format(rstd['paidOutUsdcCurrentWorth']))
        print("Total Interest Paid Out (if sold at each end stake) - ${:,.2f}".format(rstd['paidOutUsdcAtEndWorth']))
        print("---Stakes---\n")

        print("---Buys/Adds---")
        print("Total stakeEnd - {:,} HEX ".format(rbd['stakeEndTotal']['hex']) + "(${:,.2f})".format(rbd['stakeEndTotal']['usdc']))
        print("Total xfLobbyExit - {:,} HEX ".format(rbd['xfLobbyExitTotal']['hex']) + "(${:,.2f})".format(rbd['xfLobbyExitTotal']['usdc']))
        print("Total btcAddressClaimTotal - {:,} HEX ".format(rbd['btcAddressClaimTotal']['hex']) + "(${:,.2f})".format(rbd['btcAddressClaimTotal']['usdc']))
        print("Total uniswapV1 - {:,} HEX ".format(rbd['uniswapV1']['hex']) + "(${:,.2f})".format(rbd['uniswapV1']['usdc']))
        print("Total uniswapV2 - {:,} HEX ".format(rbd['uniswapV2']['hex']) + "(${:,.2f})".format(rbd['uniswapV2']['usdc']))
        print("Total unknown - {:,} HEX ".format(rbd["unknownTotal"]['hex']) + "(${:,.2f})".format(rbd['unknownTotal']['usdc']))
        print("Total Bought/Add - {:,} HEX ".format(rbd['totalHex']) + "(${:,.2f})".format(rbd['totalUsdc']))
        print("---Buys/Adds---\n")

        print("---Sells/Removes---")
        print("Total stakeStart - {:,} HEX ".format(rsd['stakeStartTotal']['hex']) + "(${:,.2f})".format(rsd['stakeStartTotal']['usdc']))
        print("Total uniswapV1 - {:,} HEX ".format(rsd['uniswapV1']['hex']) + "(${:,.2f})".format(rsd['uniswapV1']['usdc']))
        print("Total uniswapV2 - {:,} HEX ".format(rsd['uniswapV2']['hex']) + "(${:,.2f})".format(rsd['uniswapV2']['usdc']))
        print("Total unknown - {:,} HEX ".format(rsd["unknownTotal"]['hex']) + "(${:,.2f})".format(rsd['unknownTotal']['usdc']))
        print("Total Sold/Remove - {:,} HEX ".format(rsd['totalHex']) + "(${:,.2f})".format(rsd['totalUsdc']))
        print("---Sells/Removes---\n")

        print("---Difference---")
        print("{:,} HEX".format(rdd['hexDifference']))
        print("${:,.2f}".format(rdd['usdcDifference']))
        print("---Difference---\n")

        print("---Result---")
        print("${:,.2f} USD is the current value".format(r['currentUsdcValue']))
        print("${:,.2f} is left if sold".format(r['leftoverUsdcIfSold']) + " (" + r['pOrL'] + ")")
        print("---Result---")

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
        stake_interest = self.hearts_to_hex(stake_interest)
        return Decimal(stake_interest)

    def build_stake_info(self, uniswap_prices):
        r = self.report
        rsd = r['stakeData']
        where = """
                    , stakerAddr:"{0}"
               """
        where = where.format(r['address'])
        stakes = hexGraphQL.query_cycle_by_generic_number_field('stakeStarts', 'stakeId', 0, where)
        daily_data_results = hexGraphQL.query_cycle('dailyDataUpdates')
        current_hex_per_usd = float(uniswap_prices[len(uniswap_prices) - 1]['close'])

        for stake in stakes:
            rsd['startedStakedHex'] += int(stake['stakedHearts'])
            if stake['stakeEnd'] is not None:
                payout = int(stake['stakeEnd']['payout']) - int(stake['stakeEnd']['penalty'])
                usdc = self.closest(uniswap_prices, int(stake['stakeEnd']['timestamp']))['close']
                rsd['paidOutHex'] += payout
                usdc_value = float(usdc) * (self.hearts_to_hex(payout))
                rsd['paidOutUsdcAtEndWorth'] += usdc_value
                rsd['finishedStakedHex'] += int(stake['stakedHearts'])
            else:
                rsd['stakedHex'] += int(stake['stakedHearts'])
                rsd['interestHex'] += self.calc_interest(stake, daily_data_results)
        rsd['paidOutHex'] = self.hearts_to_hex(rsd['paidOutHex'])
        rsd['stakedHex'] = self.hearts_to_hex(rsd['stakedHex'])
        rsd['finishedStakedHex'] = self.hearts_to_hex(rsd['finishedStakedHex'])
        rsd['startedStakedHex'] = self.hearts_to_hex(rsd['startedStakedHex'])
        rsd['paidOutUsdcCurrentWorth'] = current_hex_per_usd * rsd['paidOutHex']
        rsd['interestHex'] = float(rsd['interestHex'])
        rsd['interestUsdcCurrentWorth'] = current_hex_per_usd * rsd['interestHex']

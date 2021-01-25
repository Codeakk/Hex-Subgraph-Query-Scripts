from graphQL import hexGraphQL
from HexAddressRapport import uniswapPricesHandler
# 0xeBC1AD03D8ea7402692b759DEd8e8CC537884659 (79 transactions)
# 0x392b95795a73a71a4379a1920b0ae360089f1047
# 0x55d5c232d921b9eaa6b37b5845e439acd04b4dba eth uniswap 2
# 0xf6dcdce0ac3001b2f67f750bc64ea5beb37b5824 usdc in
# 0x0000000000000000000000000000000000000000


def merge(dict1, dict2):
    return dict2.update(dict1)


def closest(lst, K):
    return lst[min(range(len(lst)), key=lambda i: abs(int(lst[i]['time']) - K))]


uniswap_prices = uniswapPricesHandler.get_uniswap_prices()
current_hex_per_usd = float(uniswap_prices[len(uniswap_prices) - 1]['close'])
start_time = 1576368000  # oldest uniswap data starts here
address_to_build_rapport = "0x392b95795a73a71a4379a1920b0ae360089f1047"

where = """ 
           , to: "{0}"    
           , from_not:"0x0000000000000000000000000000000000000000"
        """
where = where.format(address_to_build_rapport)
hex_buyer_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', start_time, where)

total_buys = {
    "totalHexBuys": 0
    , "totalUsdcBuys": 0
}
for item in hex_buyer_data_results:
    usdc = closest(uniswap_prices, int(item['timestamp']))['close']
    usdc_value = float(usdc) * (int(item['value']) / 100000000)
    total_buys['totalHexBuys'] += int(item['value'])
    total_buys['totalUsdcBuys'] += usdc_value
    closest_value = {
        "usdcPriceAt": usdc
        , "usdcValue": usdc_value
        , "transactionType": "buy"
    }
    merge(closest_value, item)
    print(item)
print("")
total_buys['totalHexBuys'] = total_buys['totalHexBuys'] / 100000000

#exchange_pools = ["0x55d5c232d921b9eaa6b37b5845e439acd04b4dba", "0xF6DCdce0ac3001B2f67F750bc64ea5beB37B5824"]
# for item in exchange_pools:
#    break
#     where = """, from: "{0}"
#                , to: "{1}"
#             """
#     where = where.format(address_to_build_rapport, item)
#
#     hex_seller_data_results \
#         = hex_seller_data_results \
#           + hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', start_time, where)
#for item in exchange_pools:
#    hex_seller_data_results = [_item for _item in hex_seller_data_results if _item['from'] != item.lower()]

hex_seller_data_results = []

where = """
       , from: "{0}"
       , to_not:"0x0000000000000000000000000000000000000000"
       """
where = where.format(address_to_build_rapport)
hex_seller_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', start_time, where)

total_sells = {
    "totalHexSells": 0
    , "totalUsdcSells": 0
}
for item in hex_seller_data_results:
    usdc = closest(uniswap_prices, int(item['timestamp']))['close']
    usdc_value = float(usdc) * (int(item['value']) / 100000000)
    total_sells['totalHexSells'] += int(item['value'])
    total_sells['totalUsdcSells'] += usdc_value
    closest_value = {
        "usdcPriceAt": usdc
        , "usdcValue": usdc_value
        , "transactionType": "sell"
    }
    merge(closest_value, item)
    print(item)
total_sells['totalHexSells'] /= 100000000

hex_difference = total_buys['totalHexBuys'] - total_sells['totalHexSells']
profit_or_loss = ""
loss_wording = ""
if total_buys['totalUsdcBuys'] < total_sells['totalUsdcSells']:
    profit_or_loss = "PROFIT"
    loss_wording = "and"
    usdc_difference = total_sells['totalUsdcSells'] - total_buys['totalUsdcBuys']
else:
    profit_or_loss = "LOSS"
    loss_wording = "but"
    usdc_difference = total_buys['totalUsdcBuys'] - total_sells['totalUsdcSells']
current_usdc_price = current_hex_per_usd * float(hex_difference)
leftover_usdc_if_sold = current_usdc_price - usdc_difference

print("---Buys/Adds---")
print("Total Bought/Add - {:,} HEX".format(total_buys['totalHexBuys']))
print("Total Bought/Add - ${:,.2f}".format(total_buys['totalUsdcBuys']))
print("---Buys/Adds---\n")

print("---Sells/Removes---")
print("Total Sold - {:,} HEX".format(total_sells['totalHexSells']))
print("Total Sold - ${:,.2f}".format(total_sells['totalUsdcSells']))
print("---Sells/Removes---\n")

print("---Difference---")
print("{:,} HEX".format(hex_difference))
print("(" + "${:,.2f}".format(usdc_difference) + ") in " + profit_or_loss)
print(loss_wording + " current value is " + "${:,.2f}".format(current_usdc_price) + " USD")
print("which would leave ${:,.2f} if sold".format(leftover_usdc_if_sold))
print("---Difference---\n")

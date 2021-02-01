from graphQL import hexGraphQL
import time

# hour = 3600 seconds
epoch_time = int(time.time())
start_time = epoch_time - 3600 * 5

exchange_pools = ["0x55d5c232d921b9eaa6b37b5845e439acd04b4dba", "0xF6DCdce0ac3001B2f67F750bc64ea5beB37B5824"]

hex_sellers_data_results = []

for item in exchange_pools:
    where = """
                , to: "{0}"
            """
    where = where.format(item)

    hex_sellers_data_results \
        = hex_sellers_data_results \
          + hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', start_time, where)

for item in exchange_pools:
    hex_sellers_data_results = [_item for _item in hex_sellers_data_results if _item['from'] != item.lower()]

sell_value_desc = sorted(hex_sellers_data_results, key=lambda k: int(k['value']), reverse=True)
print(sell_value_desc)

done = set()
result = []
for item in hex_sellers_data_results:
    if item['from'] not in done:
        _item = {
            "address": item['from']
            , "numOfTransactions": 1
            , "averageSell": int(item['value'])
            , "sellList": ["{:,}".format(int(item['value']) / 100000000)]
            , "totalSold": int(item['value'])
        }
        done.add(item['from'])
        result.append(_item)
    else:
        for __item in result:
            if item['from'] == __item['address']:
                __item['numOfTransactions'] += 1
                __item['sellList'].append("{:,}".format(int(item['value']) / 100000000))
                __item['totalSold'] += int(item['value'])
                __item['averageSell'] = __item['totalSold'] / __item['numOfTransactions']


hex_sellers_data_results = result

total_liquid = 0
address_balances = []
for item in hex_sellers_data_results:
    where = """, where: {{ holderAddress: "{0}" }}"""
    where = where.format(item['address'])
    hex_seller_data_result = hexGraphQL.query_cycle('tokenHolders', where)
    token_balance_in_hex = int(hex_seller_data_result[0]['tokenBalance']) / 100000000
    address_balance = {
        "from": item['address']
        , "tokenBalance": token_balance_in_hex
        , "numOfTransactions": item['numOfTransactions']
        , "averageSell": item['averageSell']
        , "sellList": item['sellList']
    }
    address_balances.append(address_balance)
    total_liquid = total_liquid + int(hex_seller_data_result[0]['tokenBalance'])

address_balances = sorted(address_balances, key=lambda k: int(k['tokenBalance']), reverse=True)

for item in address_balances:
    print(item['from'] \
          + " --- ""{:,}".format(item['tokenBalance']) \
          + " HEX --- " \
          + str(item['numOfTransactions']) \
          + " transactions --- " \
          + "{:,}".format(int(item["averageSell"]) / 100000000) \
          + " average sold hex --- " \
          + str(item['sellList'])
          )

liquid_in_hex = total_liquid / 100000000
print("{:,}".format(liquid_in_hex))

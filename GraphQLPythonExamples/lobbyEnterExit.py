import csv
from graphQL import hexGraphQL


def merge(dict1, dict2):
    return dict2.update(dict1)


csv_columns = ['id', 'enterDay', 'memberAddr', 'entryId', 'rawAmount',
               'rawEthAmount', 'timestamp', 'data0', 'referrerAddr', 'hexPayoutAmount']
lobby_enter_results = hexGraphQL.query_cycle('xfLobbyEnters')
daily_data_results = hexGraphQL.query_cycle('dailyDataUpdates')
daily_data_results.append({'blockNumber': '0'
                              , 'endDay': 1
                              , 'id': '1'
                              , 'lobbyEth': '21015.13645995905'
                              , 'lobbyHexAvailable': '100000000000000000'
                              , 'lobbyHexPerEth': '47584.7493022631'
                              , 'payout': '37065630771630'
                              , 'payoutPerTShare': '0'
                              , 'sats': '0'
                              , 'shares': '0'
                              , 'timestamp': '0'
                           })

for lobby_enter_result in lobby_enter_results:
    rawEthAmount = (float(lobby_enter_result['rawAmount']) / 1000000000000000000)
    hexPayoutAmount = 0
    merger = {'rawEthAmount': rawEthAmount
              , 'hexPayoutAmount': hexPayoutAmount}
    merge(merger, lobby_enter_result)
    for daily_data_result in daily_data_results:
        if int(daily_data_result['endDay']) == int(lobby_enter_result['enterDay']):
            hexPayoutAmount = rawEthAmount * float(daily_data_result['lobbyHexPerEth'])
            lobby_enter_result['hexPayoutAmount'] = hexPayoutAmount

lobby_enter_results = [item for item in lobby_enter_results if item['hexPayoutAmount'] != 0]

csv_file = "openEnterLobbyResults.csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in lobby_enter_results:
            writer.writerow(data)
except IOError:
    print("I/O error")
    print(IOError)

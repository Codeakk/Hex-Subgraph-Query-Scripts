from graphQL import hexGraphQL
import csv


token_holders_data_results = hexGraphQL.query_cycle_by_generic_number_field('tokenHolders', 'numeralIndex', 1) #11030100

csvFileLocationName = './csvFolder/tokenBalances.csv'
csv_columns = ['numeralIndex',
               'holderAddress'
               ]
try:
    with open(csvFileLocationName, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        for item in token_holders_data_results:
            writer.writerow(item)
except IOError:
    print("I/O error")


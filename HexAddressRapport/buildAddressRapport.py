import csv
import multiprocessing
import timeit

from HexAddressRapport.uniswapPricesHandler import Uniswap_handler
from HexAddressRapport.addressRapport import Rapport
from graphQL import hexGraphQL
from os import path

uni_prices = Uniswap_handler().prices


def build_rap(x):
    print("building rapport for " + str(x))
    return Rapport(x['holderAddress'], uni_prices)


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

#0xd4a17ad38d5264d165db58e72a8cbe715d7dbcf7
#0xf3eC5e9442EC438892113F98491e0f7317c6f088
#t = Rapport("0xd4a17ad38d5264d165db58e72a8cbe715d7dbcf7", uni_prices)
#t.print_me()
#exit()
if __name__ == '__main__':
    where = """
                  , totalReceived_gt: 5000000000000000
            """
    token_holders_data_results = hexGraphQL.query_cycle_by_generic_number_field('tokenHolders', 'numeralIndex', 10,
                                                                                where)

    pool = multiprocessing.Pool()
    csvFileLocationName = 'hexAddressRapports.csv'
    csv_columns = [
        "address"
        , "dateCreated"
        , "pOrL"
        , "totalUsdcBuys"
        , "totalUsdcSells"
        , "usdcDifference"
        , "currentUsdcValue"
        , "leftoverUsdcIfSold"
        , "totalHexBuys"
        , "totalHexSells"
        , "stakedHex"
        , "paidOutHex"
        , "paidOutUsdcCurrentWorth"
        , "paidOutUsdcAtEndWorth"
        , "interestHex"
        , "interestUsdcCurrentWorth"
        , "hexDifference"
        , "startedStakedHex"
        , "finishedStakedHex"
    ]
    counter = 0

    if not path.exists(csvFileLocationName):
        try:
            with open(csvFileLocationName, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                writer.writeheader()
        except IOError:
            print(IOError)
            print("I/O error")

    start = timeit.default_timer()

    for group in chunker(token_holders_data_results, 5):
        print(str(len(token_holders_data_results) - counter) + " left")

        for item in group:
            counter += 1

        chunk = pool.map(build_rap, group)

        try:
            with open(csvFileLocationName, 'a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                for item in chunk:
                    writer.writerow(item.rapport)
        except IOError:
            print(IOError)
            print("I/O error")

    stop = timeit.default_timer()
    print('Time: ', stop - start)
    pool.terminate()

from graphQL import hexGraphQL
import csv


def convert_timestamp_to_hex_day(timestamp):
    hex_start_epoch = 1575244800
    return int((int(timestamp) - hex_start_epoch) / 86400)


def read_uniswap_prices_to_csv():
    with open('uniswapHexHourlyPrices.csv') as f:
        uniswap_hourly_prices = [{k: str(v) for k, v in row.items()}
                                for row in csv.DictReader(f, skipinitialspace=True)]
    return uniswap_hourly_prices


def write_uniswap_prices_to_csv(uniswap_list):
    csv_file_location_name = 'uniswapHexHourlyPrices.csv'
    with open(csv_file_location_name, 'a', newline='') as out_f:
        for item in uniswap_list:
            out_f.write(str(item["time"]))
            out_f.write(',')
            out_f.write(str(item["hexDay"]))
            out_f.write(',')
            out_f.write(str(item["close"]))
            out_f.write(',')
            out_f.write(str(item["open"]))
            out_f.write(',')
            out_f.write(str(item["high"]))
            out_f.write(',')
            out_f.write(str(item["low"]))
            out_f.write(',')
            out_f.write(str(item["volume"]))
            out_f.write('\n')


def get_uniswap_prices():
    uniswap_hourly_prices = read_uniswap_prices_to_csv()
    latest_data_timestamp = \
        int(uniswap_hourly_prices[len(uniswap_hourly_prices) - 1]['time']) \
        + 1  # plus 1 to get next hour

    where = """
                  , pair:"{0}"
              """
    where = where.format("0xf6dcdce0ac3001b2f67f750bc64ea5beb37b5824")

    latest_uniswap_prices = hexGraphQL.uniswap_query_cycle_by_generic_number_field('pairHourDatas', 'hourStartUnix',
                                                                                   latest_data_timestamp, where)

    uniswap_data = []
    for item in latest_uniswap_prices:
        close = float(item['reserve1']) / float(item['reserve0'])
        built_dict = {
            "time": item['hourStartUnix']
            , "hexDay": convert_timestamp_to_hex_day(item['hourStartUnix'])
            , "close": close
            , "open": close
            , "high": close
            , "low": close
            , "volume": item['hourlyVolumeUSD']
        }
        uniswap_data.append(built_dict)

    uniswap_data = sorted(uniswap_data, key=lambda k: int(k['time']), reverse=False)

    write_uniswap_prices_to_csv(uniswap_data)  # 1611212400

    uniswap_hourly_prices = read_uniswap_prices_to_csv()

    return uniswap_hourly_prices

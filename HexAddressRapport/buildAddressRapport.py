from graphQL import hexGraphQL
import time


epoch_time = int(time.time())
start_time = epoch_time - (86400 * 45)


#0xeBC1AD03D8ea7402692b759DEd8e8CC537884659 (25 transactions)
#0x55d5c232d921b9eaa6b37b5845e439acd04b4dba eth uniswap 2

where = """, from: "{0}" 
           , to: "{1}"    
        """
where = where.format("0xeBC1AD03D8ea7402692b759DEd8e8CC537884659", "0x55d5c232d921b9eaa6b37b5845e439acd04b4dba")
hex_seller_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', start_time, where)

print("---Sells---")
total_sells = 0
for item in hex_seller_data_results:
    total_sells = total_sells + int(item['value'])
    print(item)
total_sells = total_sells / 100000000
print("Sold - {:,} HEX".format(total_sells))
print("---Sells---\n")

where = """ 
           , to: "{0}"    
        """
where = where.format("0xeBC1AD03D8ea7402692b759DEd8e8CC537884659")
hex_seller_data_results = hexGraphQL.query_cycle_by_generic_number_field('transfers', 'timestamp', start_time, where)

print("---Buys/Adds---")
total_buys = 0
for item in hex_seller_data_results:
    total_buys = total_buys + int(item['value'])
    print(item)
total_buys = total_buys / 100000000
print("Bought/Add - {:,} HEX".format(total_buys))
print("---Buys/Adds---\n")


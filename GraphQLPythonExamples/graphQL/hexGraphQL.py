from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import time
from pydash import _

transport = AIOHTTPTransport(url="https://api.thegraph.com/subgraphs/name/codeakk/hex")
client = Client(transport=transport, fetch_schema_from_transport=True)


class Event:
    def __init__(self, event_name, template):
        self.event_name = event_name
        self.template = template


events = [Event('xfLobbyEnters',
                """
                  query getXfLobbyEnters {2}
                    xfLobbyEnters(first: {0}, skip: {1}
                                ,orderBy: rawAmount
                                ,orderDirection: desc
                                ,where: {2}xfLobbyExit: null {3}
                                ) {2}
                          id
                          enterDay
                          memberAddr
                          referrerAddr
                          entryId
                          rawAmount
                          timestamp
                          data0
                        {3}
                  {3}
              """
                ), Event('dailyDataUpdates',
                         """
                           query getDailyDataUpdates {2}
                             dailyDataUpdates(first: {0}, skip: {1}
                                         ,orderBy: endDay
                                         ,orderDirection: asc
                                         ) {2}
                                   id
                                   endDay
                                   payoutPerTShare
                                   payout
                                   shares
                                   sats
                                   blockNumber
                                   timestamp
                                   lobbyEth
                                   lobbyHexPerEth
                                   lobbyHexAvailable
                                 {3}
                           {3}
                       """
                         ), Event('stakeStarts',
                                  """
                                       query getDueStakes {2}
                                         stakeStarts(first: {0}, skip: {1}
                                                     ,orderBy: stakeId
                                                     ,orderDirection: asc
                                                     , where: {2} stakeEnd: null
                                                            , stakeGoodAccounting: null
                                                            ,blockNumber_gte:{4} {3}
                                                     ) {2}
                                               id
                                               stakedDays
                                               stakerAddr
                                               stakeId
                                               startDay
                                               endDay
                                               timestamp 
                                               stakeShares
                                               stakedHearts
                                               blockNumber
                                               data0 
                                             {3}
                                       {3}
                                   """
                                  )]


def query_constructor(first, skip, event_name):
    event_template = ""
    for event in events:
        if event.event_name == event_name:
            event_template = event
    template = event_template.template
    template = template.format(first, skip, "{", "}")
    query = gql(template)
    return query


def query_constructor_block_number(first, skip, event_name, block_number):
    event_template = ""
    for event in events:
        if event.event_name == event_name:
            event_template = event
    template = event_template.template
    template = template.format(first, skip, "{", "}", block_number)
    query = gql(template)
    return query


def query_cycle(event_name):
    first = 1000
    skip = 0
    query = query_constructor(first, skip, event_name)
    call_data = client.execute(query)
    result_array = call_data[event_name]
    skip = skip + first
    query = query_constructor(first, skip, event_name)
    while len(call_data[event_name]) == first and skip < 49000:
        try:
            call_data = client.execute(query)
            for event in call_data[event_name]:
                result_array.append(event)
            skip = skip + first
            print(len(result_array))
            # first = first - 1  # escape early for testing
            query = query_constructor(first, skip, event_name)
        except Exception as e:
            time.sleep(1)
    return result_array


def find_latest_block_result(array):
    highest_block_number = 0
    # array = _.sort_by(array, 'blockNumber')
    for item in array:
        if int(item['blockNumber']) > highest_block_number:
            highest_block_number = int(item['blockNumber'])
    return highest_block_number


def query_cycle_by_block_number(event_name):
    first = 1000
    skip = 0
    block_number = 9041184 #11030100
    query = query_constructor_block_number(first, skip, event_name, block_number)
    call_data = client.execute(query)
    result_array = call_data[event_name]
    latest_block = find_latest_block_result(result_array)
    print(latest_block)
    block_number = latest_block + 1
    query = query_constructor_block_number(first, skip, event_name, block_number)
    while len(call_data[event_name]) > 0:
        try:
            call_data = client.execute(query)
            for event in call_data[event_name]:
                result_array.append(event)
            latest_block = find_latest_block_result(call_data[event_name])
            block_number = latest_block + 1
            print(block_number)
            # first = first - 1  # escape early for testing
            query = query_constructor_block_number(first, skip, event_name, block_number)
        except Exception as e:
            time.sleep(1)
            print(e)
    return result_array



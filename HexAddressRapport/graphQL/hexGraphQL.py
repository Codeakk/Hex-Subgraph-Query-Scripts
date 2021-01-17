from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import time
from pydash import _

transport = AIOHTTPTransport(url="https://api.thegraph.com/subgraphs/name/codeakk/hex")
# transport = AIOHTTPTransport(url="https://api.thegraph.com/subgraphs/id/QmWcqEQm2jwQvK2TtYRhhzt2hJjnPCbQhyoxq6rADCwRWd")

client = Client(transport=transport, fetch_schema_from_transport=True)


class Event:
    def __init__(self, event_name, template):
        self.event_name = event_name
        self.template = template


events = [
    Event('xfLobbyEnters',
          """
                query getXfLobbyEnters {{
                xfLobbyEnters(first: {0}, skip: {1}
                            ,orderBy: rawAmount
                            ,orderDirection: desc
                            ,where: {{
                                xfLobbyExit: null 
                            }}
                            ) {{
                      id
                      enterDay
                      memberAddr
                      referrerAddr
                      entryId
                      rawAmount
                      timestamp
                      data0
                    }}
                }}
            """
          ),
    Event('dailyDataUpdates',
          """
                query getDailyDataUpdates {{
                 dailyDataUpdates(first: {0}, skip: {1}
                             ,orderBy: endDay
                             ,orderDirection: asc
                             ) {{
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
                     }}
                }}
            """
          ),
    Event('tokenHolders',
          """
               query getTokenHolders {{
                tokenHolders(
                    first: {0}, skip: {1} 
                    {2} 
                ) 
                {{
                    tokenBalance
                 }}
               }}
            """
          )
]
events_by_generic_number = [
    Event('transfers',
        """
                query getTransfers {{
                transfers(
                    first: {0}, skip: {1}
                    ,orderBy:timestamp
                    ,orderDirection:asc
                    ,where: {{ 
                        {3}_gte:{2} 
                    {4}
                    }}
                ) 
                    {{
                        from
                        to
                        timestamp
                        value
                    }}
                }}
            """
          ),
    Event('tokenHolders',
          """
                   query getTokenHolders {{
                     tokenHolders(first: {0}, skip: {1}
                                 ,orderBy:numeralIndex
                                 ,orderDirection: asc
                                 ,where: {{
                                    {3}_gte:{2}
                                 }}
                                 ) 
                         {{
                            numeralIndex
                            holderAddress
                         }}
                   }}
               """
          ),
    Event('stakeStarts',
          """
                   query getDueStakes {{
                     stakeStarts(first: {0}, skip: {1}
                                 ,orderBy: stakeId
                                 ,orderDirection: asc
                                 , where: {{ 
                                        stakeEnd: null
                                        ,stakeGoodAccounting: null
                                        ,{3}_gte:{2} 
                                    }}
                                 ) 
                                {{
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
                                 }}
                           }}
               """
          )
]


def query_constructor(first, skip, event_name, custom_where):
    event_template = ""
    for event in events:
        if event.event_name == event_name:
            event_template = event
    template = event_template.template
    template = template.format(first, skip, custom_where)
    query = gql(template)
    return query


def query_constructor_generic_number(first, skip, event_name, generic_number, field, custom_where_field):
    event_template = ""
    for event in events_by_generic_number:
        if event.event_name == event_name:
            event_template = event
    template = event_template.template
    template = template.format(first, skip, generic_number, field, custom_where_field)
    query = gql(template)
    return query


def query_cycle(event_name, custom_where=""):
    first = 1000
    skip = 0
    query = query_constructor(first, skip, event_name, custom_where)
    call_data = client.execute(query)
    result_array = call_data[event_name]
    skip = skip + first
    query = query_constructor(first, skip, event_name, custom_where)
    while len(call_data[event_name]) == first and skip < 49000:
        try:
            call_data = client.execute(query)
            for event in call_data[event_name]:
                result_array.append(event)
            skip = skip + first
            # print(len(result_array))
            # first = first - 1  # escape early for testing
            query = query_constructor(first, skip, event_name, custom_where)
        except Exception as e:
            time.sleep(1)
    return result_array


def find_latest_generic_result(array, field):
    highest_generic_number = 0
    for item in array:
        if int(item[field]) > highest_generic_number:
            highest_generic_number = int(item[field])
    return highest_generic_number


def query_cycle_by_generic_number_field(event_name, field, generic_number_start, custom_where_field=""):
    first = 1000
    skip = 0
    generic_number = generic_number_start
    query = query_constructor_generic_number(first, skip, event_name, generic_number, field, custom_where_field)
    call_data = client.execute(query)
    result_array = call_data[event_name]
    latest_generic_number = find_latest_generic_result(result_array, field)
    #print(result_array)
    generic_number = latest_generic_number + 1
    query = query_constructor_generic_number(first, skip, event_name, generic_number, field, custom_where_field)
    while len(call_data[event_name]) > 0:
        try:
            call_data = client.execute(query)
            for event in call_data[event_name]:
                #print(event)
                result_array.append(event)
            latest_generic_number = find_latest_generic_result(call_data[event_name], field)
            generic_number = latest_generic_number + 1
            # print(generic_number)
            query = query_constructor_generic_number(first, skip, event_name, generic_number, field, custom_where_field)
        except Exception as e:
            time.sleep(1)
            print(e)
    return result_array

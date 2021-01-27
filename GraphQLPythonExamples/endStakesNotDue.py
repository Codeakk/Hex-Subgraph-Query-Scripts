from graphQL import hexGraphQL
from datetime import date
from pydash import _
import datetime
import math
import time


class day_shell:
    def __init__(self, _epochDay, _epochDayInSeconds, _stakes):
        self.epochDay = _epochDay
        self.epochDayInSeconds = _epochDayInSeconds
        self.stakes = _stakes


class Data0_Shell:
    def __init__(self, _timeStamp, _stakedHearts, _stakedShares, _stakedDays, _isAutoStake):
        self.timeStamp = _timeStamp
        self.stakedHearts = _stakedHearts
        self.stakedShares = _stakedShares
        self.stakedDays = _stakedDays
        self.isAutoStake = _isAutoStake


class Json_Shell:
    def __init__(self, _event, _stakeId, _stakerAddr, _logIndex, _transactionIndex, _transactionHash, _address,
                 _blockHash, _blockNumber, _parsedData0):
        self.event = _event
        self.stakeId = _stakeId
        self.stakerAddr = _stakerAddr
        self.logIndex = _logIndex
        self.transactionIndex = _transactionIndex
        self.transactionHash = _transactionHash
        self.address = _address
        self.blockHash = _blockHash
        self.blockNumber = _blockNumber
        self.parsedData0 = _parsedData0


def pair_stakes_to_epoch_days(stakes):
    global masterStakeByDays
    _.for_each(stakes, create_array_of_start_stake_by_date)
    seconds_in_day = 86400
    for y in masterStakeByDays:
        currentTimeInSeconds = time.time()
        current_epoch_day = math.trunc(currentTimeInSeconds / seconds_in_day)
        if y['epochDay'] > current_epoch_day:
            print(y)
            empty_stake = {
                    "stakeId": 0,
                    "stakeEndInSeconds": y['epochDayInSeconds'],
                    "stakedHearts": 0
                }
            y['stakes'].append(empty_stake)
            print(y)
    print("almost done")
    str_master_stake_by_days = "{ \"result\":" + str(masterStakeByDays).replace('\'', "\"") + "}"
    with open(discoveredStakesPath + '1.json', 'w') as f:
        f.write(str(str_master_stake_by_days))  # json.dump(arrayToWriteToFile, f)
    #with open(discoveredStakesPath2 + '1.json', 'w') as f:
    #    f.write(str(str_master_stake_by_days))  # json.dump(arrayToWriteToFile, f)


def create_array_of_start_stake_by_date(x):
    #print(x)
    del x["data0"]
    del x["endDay"]
    del x["id"]
    del x["stakeShares"]
    del x["stakedDays"]
    del x["stakerAddr"]
    del x["startDay"]
    del x["timestamp"]
    del x["expirationDate"]
    del x["blockNumber"]
    x["stakedHearts"] = x["parsedData0"]["stakedHearts"]
    del x["parsedData0"]
    global masterStakeByDays
    seconds_in_day = 86400
    epoch_day = math.trunc(x['stakeEndInSeconds'] / seconds_in_day)
    for y in masterStakeByDays:
        if epoch_day == y['epochDay']:
            y['stakes'].append(x)


discoveredStakesPath = 'endStakesNotDue' #'C:\\web\\endStakesNotDue'  # 'C:\\web\\endStakesNotDue'
discoveredStakesPath2 = 'C:\\webPRELIM\\endStakesNotDue'
masterStakeByDays = []
secondsInDay = 86400
startDayInSeconds = 1575417600
tenYearsInSeconds = 3650 * secondsInDay
fifteenYearsInSeconds = 5555 * secondsInDay
currentTimeInSeconds = time.time()
timePassedInSeconds = currentTimeInSeconds - startDayInSeconds
timeToPassInSeconds = (currentTimeInSeconds + fifteenYearsInSeconds) - startDayInSeconds
totalTimeInSecondsToIterate = timePassedInSeconds + timeToPassInSeconds
daysToIterate = round(totalTimeInSecondsToIterate / secondsInDay)
daysToIterate = daysToIterate + 20
for x in range(daysToIterate):
    # x = x + 1
    DayInSeconds = (x * secondsInDay) + startDayInSeconds
    epochDay = DayInSeconds / secondsInDay
    _dayShell = day_shell(epochDay, DayInSeconds, []).__dict__
    # print(_dayShell)
    masterStakeByDays.append(_dayShell)

csv_columns = ['id',
               'endDay',
               'payoutPerTShare',
               'payout',
               'shares',
               'sats',
               'blockNumber',
               'timestamp',
               'lobbyEth',
               'lobbyHexPerEth',
               'lobbyHexAvailable'
               ]
where = """
             stakeEnd: null
            ,stakeGoodAccounting: null
        """
where = where.format()
start_stake_data_results = hexGraphQL.query_cycle_by_generic_number_field('stakeStarts', 'blockNumber', 9041184, where)
print(len(start_stake_data_results))
arrayOfStartStakesNotDue = []
for stake in start_stake_data_results:
    stake['stakedHearts'] = int(stake['stakedHearts'])
    stake['timestamp'] = int(stake['timestamp'])
    stake['stakeShares'] = int(stake['stakeShares'])
    stake['stakedDays'] = int(stake['stakedDays'])
    readable = datetime.datetime.fromtimestamp(stake['timestamp'])
    daysStaked = stake['stakedDays']
    expirationDate = readable + datetime.timedelta(days=daysStaked)
    currentDate = date.today()
    currentDate = datetime.datetime.combine(currentDate, datetime.time(0, 0))
    days_Expired = (expirationDate - currentDate).days * -1
    if expirationDate > currentDate:
        stake['expirationDate'] = (expirationDate - currentDate).days
        shell = Data0_Shell(stake['timestamp']
                            , stake['stakedHearts']
                            , stake['stakeShares']
                            , stake['stakedDays']
                            , 0)
        stake['parsedData0'] = shell.__dict__
        stakeEndDate = stake['parsedData0']['timeStamp'] + (86400 * stake['parsedData0']['stakedDays'])
        stake['stakeEndInSeconds'] = stakeEndDate
        arrayOfStartStakesNotDue.append(stake)
print(len(arrayOfStartStakesNotDue))
try:
    arrayOfStartStakesNotDue = _.sort_by(arrayOfStartStakesNotDue, 'expirationDate')
    arrayOfStartStakesNotDue = _.uniq_by(arrayOfStartStakesNotDue, ['stakeId'])
    #arrayOfStartStakesNotDue = str(arrayOfStartStakesNotDue).replace('\'', "\"")
    #arrayOfStartStakesNotDue = "{ \"result\":" + arrayOfStartStakesNotDue + "}"
    pair_stakes_to_epoch_days(arrayOfStartStakesNotDue)
except IOError:
    print("I/O error")
    print(IOError)

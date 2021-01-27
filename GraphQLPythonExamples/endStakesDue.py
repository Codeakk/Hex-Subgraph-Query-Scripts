import csv
from graphQL import hexGraphQL
from datetime import date
from pydash import _
import datetime

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
start_stake_data_results = hexGraphQL.query_cycle_by_generic_number_field('stakeStarts', 'blockNumber', 9041184, where) #11030100
print(len(start_stake_data_results))
arrayOfExpiringStartStakes = []
for stake in start_stake_data_results:
    # print("debug2")
    stake['stakedHearts'] = int(stake['stakedHearts'])
    stake['timestamp'] = int(stake['timestamp'])
    stake['stakeShares'] = int(stake['stakeShares'])
    stake['stakedDays'] = int(stake['stakedDays'])
    stake['stakeId'] = int(stake['stakeId'])

    readable = datetime.datetime.fromtimestamp(stake['timestamp'])
    daysStaked = stake['stakedDays']

    expirationDate = readable + datetime.timedelta(days=daysStaked)
    currentDate = date.today()
    currentDate = datetime.datetime.combine(currentDate, datetime.time(0, 0))
    days_Expired = (expirationDate - currentDate).days * -1
    if expirationDate <= currentDate:
        if days_Expired >= 14:
            stake['expirationDate'] = (expirationDate - currentDate).days
            shell = Data0_Shell(stake['timestamp']
                               ,stake['stakedHearts']
                               ,stake['stakeShares']
                               ,stake['stakedDays']
                               ,0)
            stake['parsedData0'] = shell.__dict__
            arrayOfExpiringStartStakes.append(stake)
print(len(arrayOfExpiringStartStakes))
try:
    arrayOfExpiringStartStakes = _.sort_by(arrayOfExpiringStartStakes, 'expirationDate')
    arrayOfExpiringStartStakes = _.uniq_by(arrayOfExpiringStartStakes, ['stakeId'])
    arrayOfExpiringStartStakes = str(arrayOfExpiringStartStakes).replace('\'', "\"")
    arrayOfExpiringStartStakes = "{ \"result\":" + arrayOfExpiringStartStakes + "}"
    with open('C:\\web\\endStakesDue1.json', 'w') as f:
        f.write(str(arrayOfExpiringStartStakes))  # json.dump(arrayToWriteToFile, f)
    with open('C:\\webPRELIM\\endStakesDue1.json', 'w') as f:
        f.write(str(arrayOfExpiringStartStakes))  # json.dump(arrayToWriteToFile, f)discoveredStakesPath2
except IOError:
    print("I/O error, printing to relative folder")
    with open('endStakesDue1.json', 'w') as f:
        f.write(str(arrayOfExpiringStartStakes))  # json.dump(arrayToWriteToFile, f)
    with open('endStakesDue1.json', 'w') as f:
        f.write(str(arrayOfExpiringStartStakes))  # json.dump(arrayToWriteToFile, f)discoveredStakesPath2

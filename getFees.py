# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz
import pyprind

import arky.rest as arkApi

def getSelfTransaction(delegate='ravelou'):
    selfTransactions = []
    sum=0
    arkApi.use('ark')       #API initialization

    delegateAddress = arkApi.GET.api.delegates.get(username=delegate)['delegate']['address']
    while True:
        Transactions = arkApi.GET.api.transactions(recipientId=delegateAddress)
        if Transactions["success"]:
            receivedTransactions = Transactions['transactions']
            break
        
    for elt in receivedTransactions:
        if elt['senderId'] == delegateAddress and elt['type'] == 0:
            selfTransactions.append(elt['amount']/100000000)
    for elt in selfTransactions:
        sum+=elt
    print(sum)

def containsAValueAfterDateTime(forgedBlocksRequested, beginDatetime, endDatetime):
    """
    to be used, the arky.rest API has to be initialized
    forgedBlocksRequested : list containing the transactions asked from arky.rest API
    beginDatetime : Datetime containing the time of the last transaction you want
    """
    try:
        if arkApi.slots.getRealTime(forgedBlocksRequested[0]['timestamp']) >= beginDatetime:
            return True
        else: return False
    except IndexError:
        return True

def getBlocksBetweenDates(beginDatetime, endDatetime=datetime.now(pytz.UTC), delegate='ravelou'):
    """
    beginDatetime : the Datetime from where you want to start the counting fees 
    beginTimetime : not use
    delegate : delegate name
    """
    limitRecord = 100       #100 : max record you can ask to ark api
    offset_rqst = 0         #index used to get more than limit_Record blocks from the ARK API
    forgedBlocks = []       #forged blocks before now and after beginDatetime

    arkApi.use('ark')       #API initialization

    delegatePublicKey = arkApi.GET.api.delegates.get(username=delegate)['delegate']['publicKey']

    forgedBlocksRequested = []
    while containsAValueAfterDateTime(forgedBlocksRequested,beginDatetime,endDatetime):
         
        blocksRequest = {}
        while not blocksRequest.get("success", False):
            blocksRequest = arkApi.GET.api.blocks(limit=limitRecord, generatorPublicKey=delegatePublicKey, offset=offset_rqst)
        
        forgedBlocksRequested = blocksRequest['blocks']
        if  (arkApi.slots.getRealTime(forgedBlocksRequested[-1]['timestamp']) <= endDatetime 
            or arkApi.slots.getRealTime(forgedBlocksRequested[0]['timestamp']) >= beginDatetime):
            for i, elt in enumerate(forgedBlocksRequested):
                if (arkApi.slots.getRealTime(elt['timestamp']) >= beginDatetime 
                    and arkApi.slots.getRealTime(elt['timestamp']) <= endDatetime) :
                        forgedBlocks.append(elt)
        elif (arkApi.slots.getRealTime(forgedBlocksRequested[0]['timestamp']) <= endDatetime 
            and arkApi.slots.getRealTime(forgedBlocksRequested[-1]['timestamp']) >= beginDatetime):
            forgedBlocks += forgedBlocksRequested
        offset_rqst += limitRecord + 1
    return forgedBlocks

"""
    =============
    |MainProgram|
    =============
"""
DateInputStart = '18/02/2018'#input('Date de début (jj/mm/aaaa) : ')
TimeInputStart = '23:59'#input('Heure de début (hh:mm) : ')
DateInputEnd = '26/02/2018'
TimeInputEnd = '7:55'

dateSplitStart = DateInputStart.split("/")
timeSplitStart = TimeInputStart.split(":")
dateSplitEnd = DateInputEnd.split("/")
timeSplitEnd = TimeInputEnd.split(":")

beginTime = datetime(int(dateSplitStart[2]),int(dateSplitStart[1]),int(dateSplitStart[0]),int(timeSplitStart[0]),int(timeSplitStart[1]),0,0,tzinfo=pytz.UTC)
endTime = datetime(int(dateSplitEnd[2]),int(dateSplitEnd[1]),int(dateSplitEnd[0]),int(timeSplitEnd[0]),int(timeSplitEnd[1]),0,0,tzinfo=pytz.UTC)
fees = 0
rewards = 0
selectedBlocks = getBlocksBetweenDates(beginTime,endTime)
for i, elt in enumerate(selectedBlocks):
    fees += elt['totalFee']
    rewards += elt['reward']
    

print(arkApi.slots.getRealTime(selectedBlocks[-1]['timestamp']))
print(arkApi.slots.getRealTime(selectedBlocks[0]['timestamp']))

print("Nombre d'arks forgés en frais entre le {0} et le {1} : {2}".format(beginTime, datetime.now(pytz.UTC),fees/100000000))
print("Nombre d'arks forgés entre le {0} et le {1} : {2}".format(beginTime, datetime.now(pytz.UTC),rewards/100000000))

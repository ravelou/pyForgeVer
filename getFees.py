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

def getFeesBetweenDates(beginDatetime, endDatetime=datetime.now(pytz.UTC), delegate='ravelou'):
    """
    beginDatetime : the Datetime from where you want to start the counting fees 
    beginTimetime : not use
    delegate : delegate name
    """
    limitRecord = 100       #100 : max record you can ask to ark api
    sumFees = 0             #fees from transaction forging
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

    for i, elt in enumerate(forgedBlocks):
        sumFees += elt['totalFee']#elt['reward']
    return sumFees


"""
    =============
    |MainProgram|
    =============
"""
dateInput = '04/02/2018'#input('Date de début (jj/mm/aaaa) : ')
timeInput = '22:09'#input('Heure de début (hh:mm) : ')

dateSplit = dateInput.split("/")
timeSplit = timeInput.split(":")

beginTime = datetime(int(dateSplit[2]),int(dateSplit[1]),int(dateSplit[0]),int(timeSplit[0]),int(timeSplit[1]),0,0,tzinfo=pytz.UTC)

fees = getFeesBetweenDates(beginTime, delegate='ravelou')

print("Nombre d'arks forgés en frais entre le {0} et le {1} : {2}".format(beginTime, datetime.now(pytz.UTC),fees/100000000))
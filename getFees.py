# -*- coding: utf-8 -*-
"""Application to run on server so that it forges forever"""
from datetime import datetime, timedelta
import pytz

import arky.rest as arkApi

def getFeesBetweenDates(beginDatetime, endDatetime=datetime.now(pytz.UTC), delegate='ravelou'):

    dateDebut = endDatetime - timedelta(hours=7)

    limitRecord = 100       #100 : max record you can ask to ark api
    sumFees = 0             #fees from transaction forging
    offset_rqst = 0         #index used to get more than limit_Record blocks from the ARK API
    forgedBlocks = []       #forged blocks before now and after dateDebut

    arkApi.use('ark')       #API initialization

    delegatePublicKey = arkApi.GET.api.delegates.get(username=delegate)['delegate']['publicKey']

    while True:
        while True:
            blocksRequest = arkApi.GET.api.blocks(limit=limitRecord, generatorPublicKey=delegatePublicKey, offset=offset_rqst)
            if blocksRequest['success']:
                forgedBlocksRequested = blocksRequest['blocks']
                break
        if arkApi.slots.getRealTime(forgedBlocksRequested[limitRecord-1]['timestamp']) < dateDebut:
            for i, elt in enumerate(forgedBlocksRequested):
                if arkApi.slots.getRealTime(elt['timestamp']) >= dateDebut:
                    forgedBlocks.append(elt)
            break
        else:
            forgedBlocks += forgedBlocksRequested
            offset_rqst += limitRecord + 1

    for i, elt in enumerate(forgedBlocks):
        sumFees += elt['totalFee']
        #print("{0} : {1} ark".format(arkApi.slots.getRealTime(elt['timestamp']), elt['totalFee']/100000000))
    return sumFees


fees = getFeesBetweenDates(datetime.now(pytz.UTC) - timedelta(hours=7))

print("Nombre d'arks forgés en frais : {0}".format(fees/100000000))

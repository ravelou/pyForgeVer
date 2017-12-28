# -*- coding: utf-8 -*-
"""Application to run on server so that it forges forever"""
from datetime import datetime, timedelta
import pytz

import arky.rest as arkApi
dateDebut = datetime.now(pytz.UTC) - timedelta(days=0.5)

limitRecord = 100
sumFees = 0
offset_rqst = 0
forgedBlocks = []
arkApi.use('ark')
print(arkApi.cfg.begintime)
delegatePublicKey = arkApi.GET.api.accounts.getPublicKey(address='AXvBF7JoNyM6ztMrgr45KrqQf7LA7RgZhf')['publicKey']
print(delegatePublicKey)
print(arkApi.GET.api.delegates.forging.getForgedByAccount(generatorPublicKey=delegatePublicKey))

while True:
    while True:
        blocksRequest = arkApi.GET.api.blocks(limit=limitRecord, generatorPublicKey=delegatePublicKey, offset=offset_rqst)
        if blocksRequest['success']:
            forgedBlocksRequested = blocksRequest['blocks']
            break
    if arkApi.slots.getRealTime(forgedBlocksRequested[limitRecord-1]['timestamp']) < dateDebut:
        for i, elt in enumerate(forgedBlocksRequested):
            if arkApi.slots.getRealTime(elt['timestamp']) < dateDebut:
                forgedBlocksRequested.remove(elt)
        forgedBlocks += forgedBlocksRequested
        break
    else:
        forgedBlocks += forgedBlocksRequested
        offset_rqst += limitRecord + 1


print(forgedBlocks)
for i, elt in enumerate(forgedBlocks):
    sumFees += elt['totalFee']
    print("{0} : {1} ark".format(arkApi.slots.getRealTime(elt['timestamp']),elt['totalFee']/100000000))

print("Nombre d'arks forgés en frais de forgedBlocksRequested : {0}".format(sumFees/100000000))

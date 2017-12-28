# -*- coding: utf-8 -*-
"""Application to run on server so that it forges forever"""
from datetime import datetime, timedelta
import pytz

import arky.rest as arkApi
dateDebut = datetime.now(pytz.UTC) - timedelta(days=1)

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
        TRANSACTION = arkApi.GET.api.blocks(limit=limitRecord, generatorPublicKey=delegatePublicKey, offset=offset_rqst)
        if TRANSACTION['success']:
            break
    if arkApi.slots.getRealTime(TRANSACTION['blocks'][limitRecord-1]['timestamp']) < dateDebut:
        for i, elt in enumerate(TRANSACTION['blocks']):
            if arkApi.slots.getRealTime(elt['timestamp']) < dateDebut:
                TRANSACTION['blocks'].remove(elt)
        forgedBlocks += TRANSACTION['blocks']
        break
    else:
        forgedBlocks += TRANSACTION['blocks']
        offset_rqst += limitRecord + 1


print(forgedBlocks)
for i, elt in enumerate(forgedBlocks):
    sumFees += elt['totalFee']
    print("{0} : {1} ark".format(arkApi.slots.getRealTime(elt['timestamp']),elt['totalFee']/100000000))

print("Nombre d'arks forgés en frais de transaction : {0}".format(sumFees/100000000))

# -*- coding: utf-8 -*-
"""Application to run on server so that it forges forever"""


import arky.rest as arkApi

arkApi.use('ark')
delegatePublicKey = arkApi.GET.api.accounts.getPublicKey(address='AXvBF7JoNyM6ztMrgr45KrqQf7LA7RgZhf')['publicKey']
print(delegatePublicKey)
arkApi.GET.api.delegates.forging.getForgedByAccount(generatorPublicKey=delegatePublicKey)

# -*- coding: utf-8 -*-
"""Application to run on server so that it forges forever"""

from arky import api
API_PORT = 4002		#4001 for mainnet, 4002 for devnet
if API_PORT == 4001:
    SERVER_NETWORK = "ark"
elif API_PORT == 4002:
    SERVER_NETWORK = "dark"


class Server():
    """
    Server class\n
    param: server_ip just the ip of the server\n
    param name :  _[optional]_ Name given to the server\n
    param server_port:  [optional] The port from the API server\n
    type server_ip: str\n
    type name: str\n
    type server_port: str\n
    return:\n
    rtype: so\n

    server_seed : seed address of the server (http://XX.XX.XX.XX:YYYY)\n
    server_blockchain_height : the blockchain height seen by the server
    """

    global API_PORT, SERVER_NETWORK

    def __init__(self, server_ip, server_name=None, server_port=API_PORT):
        if not server_name:
            self.server_name = server_ip
        else: self.server_name = server_name
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_seed = 'http://'+str(self.server_ip)+':'+str(self.server_port)
        try:
            api.use(SERVER_NETWORK, custom_seed=self.server_seed)
            self.server_blockchain_height = api.Block.getBlockchainHeight()['height']
        except:
            pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str({'Name': self.server_name, 'ServerSeed': self.server_seed, \
            'serverBlockchainHeight': self.server_blockchain_height})

    def update_server_blockchain_height(self):
        """update the server blockchain height\n
        :return:    server_blockchain_height\n
        :rtype:    int\n"""
        if api.cfg.__URL_BASE__ == self.server_seed:
            self.server_blockchain_height = api.Block.getBlockchainHeight()['height']
        else:
            api.use(SERVER_NETWORK, custom_seed=self.server_seed)
            self.server_blockchain_height = api.Block.getBlockchainHeight()['height']
        return int(self.server_blockchain_height)

    def check_other_server_height(self, other_server):
        """To check the height of another server on the same port
        rtype: int"""
        if isinstance(other_server, Server):
            api.use(SERVER_NETWORK, custom_seed=other_server.server_seed)
            other_server.update_server_blockchain_height()
            return other_server
        return 0

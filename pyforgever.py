# -*- coding: utf-8 -*-
"""Application to run on server so that it forges forever"""
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
import json
from arky import api

API_PORT = 4002  # 4001 for mainnet, 4002 for devnet
if API_PORT == 4001:
    SERVER_NETWORK = "ark"
elif API_PORT == 4002:
    SERVER_NETWORK = "dark"


class Server():
    """
    Server class
    server_ip: just the ip of the server
    server_name: Name given to the server
    server_port: The port from the API server
    server_seed: seed address of the server (http\\ //XX.XX.XX.XXYYYY)
    server_blockchain_height: the blockchain height seen by the server
    return: hey\n
    rtype: so\n
"""

    global API_PORT, SERVER_NETWORK

    def __init__(self, server_ip, server_name=None, server_port=API_PORT):
        if not server_name:
            self.server_name = server_ip
        else:
            self.server_name = server_name
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_seed = 'http://' + \
            str(self.server_ip) + ':' + str(self.server_port)
        try:
            api.use(SERVER_NETWORK, custom_seed=self.server_seed)
            self.server_blockchain_height = api.Block.getBlockchainHeight()[
                'height']
        except:
            print("There was an error loading the server")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return json.dumps({'Name': self.server_name, 'ServerSeed': self.server_seed,
                           'serverBlockchainHeight': self.server_blockchain_height},
                          sort_keys=True, indent=2)
        # return str({'Name': self.server_name, 'ServerSeed': self.server_seed,
        #            'serverBlockchainHeight': self.server_blockchain_height})

    def update_server_blockchain_height(self):
        """update the server blockchain height\n
        return:    server_blockchain_height\n
        rtype:    int\n"""
        if api.cfg.__URL_BASE__ == self.server_seed:
            self.server_blockchain_height = api.Block.getBlockchainHeight()[
                'height']
        else:
            api.use(SERVER_NETWORK, custom_seed=self.server_seed)
            self.server_blockchain_height = api.Block.getBlockchainHeight()[
                'height']
        return int(self.server_blockchain_height)

    def check_other_server_height(self, other_server):
        """To check the height of another server on the same port
        rtype: int"""
        if isinstance(other_server, Server):
            api.use(SERVER_NETWORK, custom_seed=other_server.server_seed)
            other_server.update_server_blockchain_height()
            return other_server
        return 0

    def get_delegate_passphrase(self, config_file):
        """Delegate function to get the delegate passphrase
        config_file: the path to the configuration file where you get your passphrase"""
        r_config_file = open(config_file, "r")
        config_json = api.ArkyDict = json.loads(r_config_file.read())
        return config_json['forging']['secret'][0]

    def change_config_file(self, config_file, passphrase=''):
        """Function to put the passphrase into the main config file. Usually config.mainnet.json
        config_file: main config file
        passphrase: the passphrase you want to write into config_file"""
        r_config_file = open(config_file, "r")
        config_json = api.ArkyDict = json.loads(r_config_file.read())
        config_json['forging']['secret'][0] = passphrase
        with io.open('data.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(config_json,
                      indent=2,
                      separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))


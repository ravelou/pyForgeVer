# -*- coding: utf-8 -*-
"""Application to run on server so that it forges forever"""

import json
import os
import subprocess
import logging

from arky import rest
logging.basicConfig(
    filename='{0}/test_log.log'.format(os.getenv('HOME')), level=logging.DEBUG)
# logging = logging.getlogging()
# logging.basicConfig(filename='{0}/test_log.log'.format(os.getenv('HOME')), level=logging.DEBUG)


class Server(object):
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
    networks = {
        'ark': {
            'port': 4001,
            'file_suffix': 'mainnet'
        },
        'dark': {
            'port': 4002,
            'file_suffix': 'devnet'
        }
    }

    network = 'dark'
    port = 4002
    file_suffix = 'devnet'

    @classmethod
    def get_network(cls, server_port):
        """Initialize global variable for the class"""
        for (name, config) in cls.networks.items():
            if server_port == config['port']:
                cls.port = config['port']
                cls.file_suffix = config['file_suffix']
                cls.network = name
        logging.info("class port : %s, class file_suffix = %s, class network = %s",
                     cls.port, cls.file_suffix, cls.network)

    def __init__(self, server_ip, server_port, server_name=None):
        if not server_name:
            self.server_name = server_ip
        else:
            self.server_name = server_name
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_seed = 'http://' + \
            str(self.server_ip) + ':' + str(self.server_port)
        self.__class__.get_network(server_port)
        try:
            rest.use(self.__class__.network, custom_seed=self.server_seed)
            self.server_blockchain_height = rest.GET.api.blocks.getHeight()[
                'height']
        # except rest.cfg..NetworkError:
        #    print("There was an error loading the server")
        # logging.info(self.__repr__())
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return json.dumps({'Name': self.server_name, 'ServerSeed': self.server_seed,
                           'serverBlockchainHeight': self.server_blockchain_height},
                          sort_keys=True, indent=2)

    def update_server_blockchain_height(self):
        """update the server blockchain height\n
        return:    server_blockchain_height\n
        rtype:    int\n"""
        if rest.cfg.__URL_BASE__ != self.server_seed:
            rest.use(self.__class__.network, custom_seed=self.server_seed)
        self.server_blockchain_height = rest.GET.api.blocks.getHeight()[
            'height']

        return int(self.server_blockchain_height)

    def check_other_server_height(self, other_server):
        """To check the height of another server on the same port
        rtype: int"""
        if isinstance(other_server, Server):
            rest.use(self.__class__.network,
                     custom_seed=other_server.server_seed)
            other_server.update_server_blockchain_height()
            return other_server
        return 0

    @staticmethod
    def get_delegate_passphrase(config_file):
        """Delegate function to get the delegate passphrase
        config_file: the path to the configuration file where you get your passphrase
        """

        r_config_file = open(config_file, "r")
        config_json = json.loads(r_config_file.read())
        return config_json['forging']['secret']

    @staticmethod
    def change_config_file(config_file,
                           new_config_file,
                           passphrase=''):
        """Function to put the passphrase into the main config file. Usually config.mainnet.json
        config_file: main config file to be change
        new_config_file: main config file changed with the new passphrase
        passphrase: the passphrase you want to write into config_file
        """

        r_config_file = open(config_file, "r")
        config_json = json.loads(r_config_file.read())
        config_json['forging']['secret'] = passphrase
        with open(new_config_file, 'w', encoding='utf8') as outfile:
            json.dump(config_json, outfile, indent=2)
            # str_ = json.dumps(config_json,
            #                   indent=2,
            #                   separators=(',', ': '), ensure_ascii=False)
            # outfile.write(str_)

    @classmethod
    def restart_server_node(cls, config_filename, arknode_dir_path="{0}/ark-node".format(os.getenv('HOME'))):
        """method to restart the node from the current server
        config_filename:the name of the config file you want to use to start the node\
                        usually config.[mainnet/devnet].json
        arknode_dir_path: the path where your app.js, config json file are
        """
        subprocess.run(["forever", "stop", "{0}/app.js".format(arknode_dir_path)],
                       stdout=subprocess.PIPE, check=False)
        os.chdir(arknode_dir_path)
        r = subprocess.run(['forever', 'start', 'app.js', '--config', config_filename,
                            '--genesis', 'genesisBlock.{0}.json'.format(cls.file_suffix)],
                           stdout=subprocess.PIPE)
        logging.debug(r.stdout)

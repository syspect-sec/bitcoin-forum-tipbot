# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: RPC Abstraction Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package abstracts the web API connection details.  Profiles for connecting to sources can be created here. 
# The profile name is passed into the object upon creation. 

# Import Basic Modules

import bitcoinrpc.authproxy

class BitcoinRpc:
    def __init__(self, profile):
        # bland.is profile
        if profile == "auroracoind":
            BITCOINRPC = 'http://bitcoinrpc:BPyWbzgFyi8tTjQ3RyTdCx27ANq4R3PTRhwoKEDVKDqo@localhost:12341/'
            self.bitcoin = bitcoinrpc.authproxy.AuthServiceProxy(BITCOINRPC)
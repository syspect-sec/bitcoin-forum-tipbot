# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: Main Bank Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package is monitoring public addresses for user deposits and modifying database balance amounts.
# Components such as SQL, RPC, and forum API are abstracted with concerns for modularity. The original version is written with postresql
# and bitcoind v 0.7.

# Import Basic Modules
import requests
import bitcoinrpc
import logging
import sys

# Import tip-bot Modules
import bank
import messaging

# Import abstraction Modules
import rpc_abstraction
import sql_abstraction
import api_abstraction

# Logging Configuration
logger = logging.getLogger('__Aurtip-Bank__')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh_debug = logging.FileHandler('bank-debug.log')
fh_debug.setLevel(logging.DEBUG)
# create file handler which logs only critical messages
fh_crit = logging.FileHandler('bank-critical.log')
fh_crit.setLevel(logging.CRITICAL)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh_crit.setFormatter(formatter)
fh_debug.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(fh_debug)
logger.addHandler(fh_crit)
logger.addHandler(ch)

# Main Function #
#               #

# define connection settings
DB_PROFILE = "mysql" 
RPC_PROFILE = "auroracoind"
API_PROFILE = "bland"

# Create objects for abstracted connections: restFulGET, postgresql, bitcoinrpc
api = api_abstraction.ApiConnection(API_PROFILE)
db = sql_abstraction.SqlConnection(DB_PROFILE)
rpc = rpc_abstraction.BitcoinRpc(RPC_PROFILE)

# Check all user addresses for deposits
#bankPayload = bank.BankPayload("bank", api, db)
#inboxPayload = payload.Payload("inbox", api, db)
bankPayload = bank.BankPayload("test", db, rpc)

# Process and message

logger.debug("Bank Script Completed")





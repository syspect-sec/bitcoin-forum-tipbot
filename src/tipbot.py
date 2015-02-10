# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: Main Tipbot Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package is for parsing a forum for command calls and processing payment function through Auroracoin or another crypto-currency.
# Components such as SQL, RPC, and forum API are abstracted with concerns for modularity. The original version is written with postresql
# and bitcoind v 0.7.

# Import Basic Modules
import requests
import bitcoinrpc
import logging
import sys

# Import tip-bot Modules
import payload
import payloadProcessor
import messenger

# Import abstraction Modules
import rpc_abstraction
import sql_abstraction
import api_abstraction

# Logging Configuration
logger = logging.getLogger('__Aurtip__')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh_debug = logging.FileHandler('debug.log')
fh_debug.setLevel(logging.DEBUG)
# create file handler which logs only critical messages
fh_crit = logging.FileHandler('critical.log')
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

# Build payload from an API source
#forumPayload = payload.Payload("forum", api, db)
#inboxPayload = payload.Payload("inbox", api, db)
testPayload = payload.Payload("test", api, db)

# Process the payload into command calls and return messages to users
#forumProcessList = payloadProcessor.PayloadProcessor(forumPayload.payload, db, rpc)
#inboxProcessList = payloadProcessor.PayloadPrcessor(inboxPayload.paylaod, db, rpc)
testProcessList = payloadProcessor.PayloadProcessor(testPayload.payload, db, rpc)


# Outputing messages
for message in testProcessList.messages:
    print message
# Process and message

# Process messages into forum posts and emails
report = messenger.Messenger(testProcessList, api)

logger.debug("Script Completed")





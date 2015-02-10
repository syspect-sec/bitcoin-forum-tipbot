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

import decimal
import logging

class BankPayload:
    def __init__(self, type, db, rpc):
        self.log = logging.getLogger('__Aurtip-Bank__')
        self.log.debug("---Deposit Processor Started---")
        total_balance = 0
        balance_found = False
        deposits = []
        if type == 'bank':
            pass
        elif type == 'test':
            address_list = db.get_deposit_address_list()
            for address in address_list:
                self.log.debug("Inspecting address: %s", address['deposit_pubkey'])
                # rpc call to check balance
                balance = decimal.Decimal(rpc.bitcoin.getreceivedbyaddress(address['deposit_pubkey']))
                balance_string = str('%.10g' % balance).strip() 
                self.log.debug ("Balance: %s", (str(balance_string)))
                total_balance += balance
                if balance > 0:
                    balance_found = True
                    deposits.append(address['deposit_pubkey'])
                    # modify user balance in database
                    db.deposit_to_user(address['username'], balance)
                    self.log.debug("Deposits found for user %s in address %s" % (address['username'], address['deposit_pubkey']))
                    rpc.bitcoin.setaccount(address['deposit_pubkey'], "deposit_pool")
            if balance_found == False:
                self.log.debug("Deposits are being moved to a pool")
                # get address for back pooling of currency
                new_address = rpc.bitcoin.getnewaddress("back_pool")
                self.log.critical("New Address created: %s" % (new_address))
                # send whole found amount from the deposit pool account to 
                balance = rpc.bitcoin.getbalance("deposit_pool", 1)
                balance_string = str('%.10g' % balance).strip()
                print balance_string
                rpc.bitcoin.sendfrom("deposit_pool", new_address, balance_string)
                new_balance = rpc.bitcoin.getbalance("deposit_pool")
                # move all balance to new address
                self.log.critical("New deposit pool balance: %s" % (new_balance))
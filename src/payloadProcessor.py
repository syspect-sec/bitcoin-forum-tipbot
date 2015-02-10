# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: Payload Handler Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package processes the payloads build from API calls.  Each command call has a function which handles the storing of data, 
# RPC calls to the bitcoind core software, transferring funds, and messages the users.

# Import Basic Modules
import re
import bitcoinrpc
import logging
import dictionary
from decimal import Decimal

COMMAND_LIST = ["history", "tip", "info", "accept", "reject", "withdraw", "balance", "pool", "autoaccept", "autowithdraw", "thank", "block", "unblock", "unregister"]

class PayloadProcessor:
    def __init__(self, payload, db, rpc):
        self.messages = []
        self.rpc = rpc
        self.log = logging.getLogger('__Aurtip__')
        if len(payload) > 0:
            self.log.debug("---Payload has commands in it---")
            self.payloadProcessor(payload, db, rpc)
    
    def payloadProcessor(self, payload, db, rpc):
        self.log.debug("---Payload Processor Starting---") 
        for item in payload:
            self.registrationCheck("user", item, db, rpc)
            if len(item['commands']) > 0:
                self.log.debug("Parsing payload commands from post %s" % item['thread_id'])
                # process all explicit commands in payload
                for command in item['commands']:
                    if command in COMMAND_LIST:
                        if command == 'info':
                            self.log.debug("User info command request from user %s in post %s" % (item['username'], item['thread_id']))
                            # get user info from database                            
                            info = db.get_user_info(item['username'])
                            self.buildMessage("info", item['thread_id'], item['username'], info)
                        elif command == 'history':
                            self.log.debug("User history command request from user %s in post %s" % (item['username'], item['thread_id']))
                            #get user account transaction history and send to user inbox
                            history_object = db.get_user_history(item["username"])
                            self.buildMessage("history", item['thread_id'], history_object)
                        elif command == 'tip':
                            self.log.debug("Tip command request from user %s in post %s" % (item['username'], item['thread_id']))
                            self.payloadTip(item, db, rpc)
                        elif command == 'accept':
                            amount = self.payloadAccept(item['username'], db, item['tip_id'])
                            if amount is None:
                                self.buildMessage("error", item['thread_id'], item['username'], "Your tip was already accepted.")
                            else:     
                                self.buildMessage("accept", item['thread_id'], item['username'], amount)
                        elif command == 'reject':
                            self.payloadReject(item['username'], item['tip_id'])
                            self.buildMessage("reject", item['thread_id'], item['tip_id'])
                        elif command == 'withdraw':
                            self.log.debug("Withdraw command request from user %s in post %s" % (item['username'], item['thread_id'])) 
                            self.payloadWithdraw(item, db, rpc)
                        elif command == 'balance':
                            self.log.debug("Balance command request from user %s in post %s" % (item['username'], item['thread_id']))
                            self.buildMessage("balance", item['thread_id'], item['username'], db.get_balance(item['username']))
                        elif command == 'pool':
                            self.log.debug("Preference change request found: 'pool' for user %s in post %s" % (item['username'], item['thread_id']))
                            # change user preference to pool funds and not send tip right away
                            db.change_user_preference(item['username'], "pool", 1)
                            self.buildMessage("preference", item['thread_id'], item['username'], "Now pooling tips")
                        elif command == 'autowithdraw':
                            self.log.debug("Preference change request found: 'autowithdraw' for user %s in post %s" % (item['username'], item['thread_id']))
                            # change user preference to automatically transfer tip funds to pubkey address
                            if db.change_user_preference(item['username'], "pool", 0) == True:
                                self.buildMessage("preference", item['thread_id'], item['username'], "Now automatically withdrawing tips")
                            else: 
                                self.buildMessage("autowd-no-address-error", item['thread_id'], item['username'], "You must have a receive address onfile for automatic withdrawl. Please send us an Auroracoin public address.")
                        elif command == 'autoaccept':
                            self.log.debug("Preference change request found: 'autoaccept' for user %s in post %s" % (item['username'], item['thread_id']))
                            # change user preference to automaticall accept the funds
                            db.change_user_preference(item['username'], "auto_accept", 1)
                            self.buildMessage("preference", item['thread_id'], item['username'], "Now automcaticaly accepting tips")
                        elif command == 'unregister':
                            db.unregister_user(item['username'], item['datetime'], item['thread_id'])
                            self.buildMessage("unregister", item['thread_id'], item['username'])
                    else:
                        pass
                        #raise error
                        self.log.debug("Invalid command: '%s' included in post from user %s in post %s" % (command, item['username'], item['thread_id']))
                        #self.buildMessage("error", item['username'], command)
            elif len(item['recipient']) > 0 and len(item['amount']) > 0:
                self.payloadTip(item, db, rpc)
            elif "address" in item:
                self.log.debug("Change of public receive address requested for %s in post %s" % (item['username'], item['thread_id']))
                db.change_user_receive_address(item["username"], item['address'])
                self.buildMessage("address-change", item['thread_id'], item['username'], item['address'])
            elif "email" in item:
                self.log.debug("Change of email address requested for %s in post %s" % (item['username'], item['thread_id']))
                db.change_user_email_address(item["username"], item['email'])
                self.buildMessage("email-change", item['thread_id'], item['username'], item['email'])
            
    def buildMessage(self, type, thread_id, recipient, data=None):
        # array to hold all messages
        import dictionary
        #print data
        dictionary = dictionary.Dictionary("english")
        if type == "info":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " +  dictionary.MESSAGES_INFO))
            self.messages.append((thread_id, recipient, "Balance: " + data[2] + " AUR"))
            self.messages.append((thread_id, recipient, "Registration Date: " + str(data[1])))
            if data[3] is None:
                self.messages.append((thread_id, recipient, "Onfile Auroracoin Public Address: None"))
            else:
                self.messages.append((thread_id, recipient, "Online Auroracoin Public Address: " + data[3]))
                if data[4] == True:
                    self.messages.append((thread_id, recipient, "Auto Withdraw: True"))
                else:
                    self.messages.append((thread_id, recipient, "Auto Withdraw: False"))
            if data[5] == True:
                self.messages.append((thread_id, recipient, "Auto Accept: True"))
            else:
                self.messages.append((thread_id, recipient, "Auto Accept: False"))
        if type == "balance":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_BALANCE + data + " AUR"))
        if type == "history":
            if data is None:
                self.messages.append((thread_id, recipient, "Here is your account history"))
            else:
                self.messages.append((thread_id, recipient, "Here is your account hisotry"))
                self.messages.append((thread_id, recipient, "Account withdraw history: "))
                for item in data[0]:
                    print "transaction"
                    self.messages.append((thread_id, recipient, "Transaction"))
                self.messages.append((thread_id, recipient, "Account deposit history: "))
                for item in data[1]:
                    print "transaction"
                    self.messages.append((thread_id, recipient, "Transaction"))
                self.messages.append((thread_id, recipient, "Tips recieved history: "))
                for item in data[2]:
                    self.messages.append((thread_id, recipient, "Transaction"))
                    print "transaction"
                self.messages.append((thread_id, recipient, "Tips given history: "))
                for item in data[3]:
                    self.messages.append((thread_id, recipient, "Transaction"))
                    print "transaction"
        if type == "tip-sender":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_TIP_SENDER + data[1]))
            self.messages.append((thread_id, recipient, "Amount: " + str(data[2]) + " AUR"))
        if type == "tip-sender-autoac":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_TIP_SENDER_AUTOAC + data[1]))
            self.messages.append((thread_id, recipient, "Amount: " + str(data[2]) + " AUR"))
        if type == "tip-recipient":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_TIP_RECIPIENT + data[0]))
            self.messages.append((thread_id, recipient, "Amount: " + str(data[2]) + " AUR"))
            self.messages.append((thread_id, recipient, "Tip ID: " + data[5]))
        if type == "tip-recipient-autowd":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_TIP_RECIPIENT_AUTOWD))
            self.messages.append((thread_id, recipient, "Amount: " + str(data[2]) + " AUR"))
        if type == "tip-recipient-autoac":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_TIP_RECIPIENT_AUTOAC + data[0]))
            self.messages.append((thread_id, recipient, "Amount: " + str(data[2]) + " AUR"))
            self.messages.append((thread_id, recipient, "Tip ID: " + data[5]))
        if type == "reject":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_TIP_REJECT))
        if type == "accept":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_ACCEPT))
            self.messages.append((thread_id, recipient, "Amount: " + str(data) + " AUR"))
        if type == "withdraw":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_WITHDRAW))
        if type == "preference":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_PREFERENCE + data))
        if type == "error":
            self.messages.append((thread_id, recipient, "Dear " + recipient + ", " + dictionary.MESSAGES_ERROR + data))
        if type == "insufficient-tip":
            self.messages.append((thread_id, recipient, dictionary.MESSAGES_INSUFFICIENT_TIP + str(data[0])))
            self.messages.append((thread_id, recipient, dictionary.MESSAGES_INSUFFICIENT_BALANCE + str(data[1]) + " AUR"))
        if type == "insufficient-withdraw":
            self.messages.append((thread_id, recipient, dictionary.MESSAGES_INSUFFICIENT_WITHDRAW + str(data[0])))
            self.messages.append((thread_id, recipient, dictionary.MESSAGES_INSUFFICIENT_BALANCE + str(data[1]) + " AUR"))
        if type == 'email-change':
            self.messages.append((thread_id, recipient, dictionary.MESSAGES_EMAIL_CHANGE + data))
        if type == 'address-change':
            self.messages.append((thread_id, recipient, dictionary.MESSAGES_ADDRESS_CHANGE + data))
        if type == 'autowd-no-address-error':
            self.messages.append((thread_id, recipient, dictionary.MESSAGES_PREFERENCES_CHANGE_ERROR + data))
        
    def payloadWithdraw(self, item, db, rpc, address=None):
        withdraw_error = False
        # check that the amount is included
        if 'amount' in item:
            balance = db.get_balance(item['username'])
            if item['amount'] > balance :
                self.log.debug("Insufficient Funds for withdrawl in post %s" % (item['thread_id']))
                data = (item['amount'], balance)
                self.buildMessage("insufficient-withdraw", item['thread_id'], item['username'], data)
                withdraw_error = True
        else:
            self.log.debug("No amount included in withdraw command from user %s in post %s" % (item['username'], item['thread_id']))
            withdraw_error = True
        # check that address is included
        if 'address' in item is None: 
            address = db.get_user_receive_address(item['username'])
            if address is None:
                self.buildMessage("no address", item['thread_id'], item['username'])
                self.log.debug("No address is available for user %s" % (item['username']))
                withdraw_error = True
        else:
            address = item['address']
        # TODO: need a better address validation at this point
        #if re.match(r"^[aA][a-km-zA-HJ-NP-Z0-9]{26,33}$", address):
            
        #else: 
            #withdraw_error = True
        #do transaction or create error message
        if withdraw_error == False:
            print "Address: " + address
            #rpc call to AuroraCoind to send to that address
            #response = rpc.bitcoin.sendtoaddress(address, item['amount'])
                
        
    def payloadAutoWithdraw(self, item):
        pass
    
    def payloadReject(self, username, unique_id=None):
        if unique_id is None:
            self.log.debug("No Tip ID available in reject request for %s" % username)
        else:
            self.log.debug("Processing a reject payment for %s and unique_id: %s" % (username, unique_id))
            if db.check_tip_status(username, unique_id) == True:
                # mark tip as rejected
                db.reject_tip(unique_id)
                self.log.debug("Tip %s rejected  for %s", (unique_id, username))
            else:
                self.log.debug("Tip %s has already been accepted, rejected, or withdrawn for %s" % (unique_id, username))
    
    def payloadAccept(self, username, db, unique_id=None):
        if unique_id is None:
            # raise error for lack of tip ID
            self.log.debug("No Tip ID available in accept request for %s" % username)
        else:
            self.log.debug("Processing an accept for %s unique_id: %s" % (username, unique_id))
            # check if tip is accepted or rejected already
            if db.check_tip_status(username, unique_id) == True:
                # mark tip as accepted
                amount = db.accept_tip(unique_id)
                self.log.debug("Tip %s accepted and balance transfered for %s" % (unique_id, username))
                return amount
            else:
                self.log.debug("Tip %s has already been accepted, rejected, or withdrawn for %s" % (unique_id, username))
            
    def payloadTip(self, item, db, rpc):
        if len(item['recipient']) != len(item['amount']) or len(item['recipient']) != 1 or len(item['amount']) != 1:
            self.log.debug("Wrong number of recipients or amounts in post %s" % item['thread_id'])
            #append info to error message
            self.buildMessage("error", item['thread_id'], item['username'], "You can only use one recipeint and one balance in a command")
        else:
            self.log.debug("Recipient and amount are OK in post %s" % item['thread_id'])
            recipient =  item['recipient'][0].replace("@", "")
            self.registrationCheck("recipient", item, db, rpc, recipient)
            # check balance is available for tip
            balance = db.get_balance(item['username'])
            balance_decimal = Decimal(balance)
            amount = Decimal(item['amount'][0])
            if balance_decimal < amount :
                self.log.debug("User balance %s insufficient for tip amount %s in post %s" % (balance, item['amount'][0], item['thread_id']))
                self.buildMessage("insufficient-tip", item['thread_id'], item['username'], (item['amount'][0], balance))
            else:
                # build a tip object
                tip = [item['username'], recipient, item['amount'][0], item['thread_id'], item['datetime']]
                # remove amount from sender balance
                db.adjust_sender_balance(item['username'], item['amount'][0])
                # get user tip preferences from database
                tip_preferences = db.get_user_tip_preferences(recipient)
                # if auto withdraw is user pref
                if tip_preferences[0] == False:
                    tip.append(str(db.store_tip("withdrawn", tip)) + "_A")
                    self.payloadAutoWithdraw(recipient, db, tip[5])
                    self.log.debug("Tip %s has been autowithdrawn in post %s" % (tip[5], item['thread_id']))
                    # withdraw to public address of user
                    # build messages
                    self.buildMessage("tip-sender-autoac", item['thread_id'], item['username'], tip)
                    self.buildMessage("tip-recipient-autowd", item['thread_id'], recipient , tip)
                # if auto accept is user pref
                elif tip_preferences[1] == True:
                    # for automatically accepted tips
                    tip.append(str(db.store_tip("accepted", tip)) + "_A")
                    self.payloadAccept(recipient, db, tip[5])
                    self.log.debug("Tip %s accepted and stored in database for post %s" % (tip[5], item['thread_id']))
                    # build messages
                    self.buildMessage("tip-sender-autoac", item['thread_id'], item['username'], tip)
                    self.buildMessage("tip-recipient-autoac", item['thread_id'], recipient, tip)
                # if user pref is pool and manual accept
                else:
                    tip.append(str(db.store_tip("none", tip)) + "_A")
                    self.log.debug("Tip %s stored in database, waiting for accept for post %s" % (tip[5], item['thread_id']))
                    # build messages
                    self.buildMessage("tip-sender", item['thread_id'], item['username'], tip)
                    self.buildMessage("tip-recipient", item['thread_id'], recipient, tip)
    
    def registrationCheck(self, type, item, db, rpc, recipient=None):
        if type == "user":
            if int(db.check_user_registration_status(item['username'])["registered"]) == False:
                    db.register_new_user("user", item)
                    deposit_address = rpc.bitcoin.getnewaddress()
                    db.store_new_deposit_address(item['username'], deposit_address)
                    self.log.debug("New user registered: '%s'" % item['username'])
        if type == "recipient":
            if int(db.check_user_registration_status(recipient)["registered"]) == False:
                    db.register_new_user("recipient", item, recipient)
                    self.log.debug("Recipient Registered '%s'" % recipient)
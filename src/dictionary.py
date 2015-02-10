# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: SQL Abstraction Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package abstracts the web API connection details.  Profiles for connecting to sources can be created here. 
# The profile name is passed into the object upon creation. 

class Dictionary:
    def __init__(self, language):
        if language == "english":
            self.MESSAGES_INFO = "AURtip Account Info: "
            self.MESSAGES_HISTORY = "AURtip Account History: "
            self.MESSAGES_BALANCE = "AURtip Account Balance: "
            self.MESSAGES_TIP_SENDER = "AURtip You sent a tip to "
            self.MESSAGES_TIP_SENDER_AUTOAC = "AURtip Your tip was accepted by "
            self.MESSAGES_TIP_RECIPIENT = "AURtip You got a tip from "
            self.MESSAGES_TIP_RECIPIENT_AUTOWD = "AURtip Tip sent to your Auroracoin address. "
            self.MESSAGES_TIP_RECIPIENT_AUTOAC = "AURtip You accepted a tip from "
            self.MESSAGES_REJECT = "AURtip You rejected a tip from "
            self.MESSAGES_ACCEPT = "AURtip You've accepted a tip from "
            self.MESSAGES_WITHDRAW = "AURtip Withdraw Complete.  Your account balance is: "
            self.MESSAGES_PREFERENCE = "AURtip You have changed your Aurtip preferences: "
            self.MESSAGES_ERROR = "AURtip There was an error with your Aurtip command request. "
            self.MESSAGES_INSUFFICIENT_TIP = "AURtip You requested to tip "
            self.MESSAGES_INSUFFICIENT_WITHDRAW = "AURtip You requested to withdraw "
            self.MESSAGES_INSUFFICIENT_BALANCE = "Your balance is "
            self.MESSAGES_EMAIL_CHANGE = "You've changed your account email to "
            self.MESSAGES_ADDRESS_CHANGE = "You've changed your account recieving address to "
            self.MESSAGES_BOTTOM_LINER = "Instructions for AURtip can be found http://104.236.66.174/aurtip.html"
            self.MESSAGES_PREFERENCES_CHANGE_ERROR = "There was an error with your request. "
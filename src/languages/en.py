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

class MessageDictionary():
    def __init__(self, language):
        if language == "english":
            self.MESSAGES_INFO = "Here is your requested account information: %s "
            self.MESSAGES_HISTORY = "Here is your requested transaction history: %s"
            self.MESSAGES_BALANCE = "You requested the blance of your account.  Here is the balance of your account: %s"
            self.MESSAGES_

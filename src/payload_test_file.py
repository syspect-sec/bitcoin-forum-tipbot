# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: Get Payload Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package collects payloads from the web-API.  The payloads are a list in the class containing command information 
# The original class parses forum threads and inbox messages to our account.  The abstracted API is used to get the url.

# Import Basic Modules
import datetime
import logging
import requests
import re
import json

class Payload:
    def __init__(self, payload_type, api, db):
        self.payload = []
        self.log = logging.getLogger(__name__)
        if payload_type == "forum":
            # create a list of payload information
            self.getForumPayload(api, db)
        if payload_type == "inbox":
            # create a list of payload information
            self.getMessagePayload(api, db)
        
    def getForumPayload(self, api, db):
        #open test text file
        test_file = open('regextest.txt', 'r')
        #read line by line
        for line in test_file:
            parseText(line) 
        
    def getMessagePayload(self, api, db):
        # API call to get web-app messages
        info_response = requests.get(api.info_url)
        if info_response.status_code == 200:
            info = json.loads(info_response.content)
            print "New Messages: " + str(info["new_messages_count"])
            if info['new_messages_count'] > 0:
                inbox_response = requests.get(api.inbox_url + "3")
                if inbox_response.status_code == 200:
                    print "Inbox Retreived"
                    inbox = json.loads(inbox_response.content)
                    print inbox['count'] + " messages in inbox" 
                    print inbox
                    # self.parseTextToPayload(text)
    
    def parseTextToPayload(self, post, post_datetime):
        command_found = False
        command_valid = False
        # look for REGEX for +AURtip and take it plus next three expressions.
        if re.findall(r"(^|\s)[\+][aA][uU][rR][tT][iI][pP](\s|$)", post['text']):
            print "AURtip Command Found in post: '" + post['text'] + "'"
            #check if user is registered and if not, then register them.
            # Make a list of strings to be used in the command parse.  Maybe more than one command per post.
            regex_commands = re.findall(r"([\+][aA][uU][rR][tT][iI][pP]($|[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}|[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}|[\s][0-9a-zA-Z\.]{1,}|[\s]))", post['text'])
            #print regex_commands
            for command in regex_commands:
                payload_item = {}
                command_elements = command[0].split(" ", 4)
                print command_elements
                command_list = []
                for element in command_elements:
                    element = element.strip(".")
                    # if it's only a word it's a command
                    if re.findall(r"^[a-zA-Z]{1,10}$", element):
                        command = re.findall(r"^[a-zA-Z]{1,10}$", element)
                        print "Command: " + command[0]
                        command_list.append(command[0])
                    # if it has only numbers, or numbers and decimal
                    if re.findall(r"^[0-9]{1,6}\.?[0-9]{1,8}$", element):
                        amount = re.findall(r"^[0-9]{1,6}\.?[0-9]{1,8}$", element)
                        print "Amount: " + amount[0]
                        payload_item['amount'] = amount[0] 
                    # if it has '@' it is a username
                    if re.findall(r"^[\@][0-9a-zA-Z]{1,}$", element):
                        username = re.findall(r"^[\@][0-9a-zA-Z]{1,}$", element)
                        print "Username: " + username[0]
                        payload_item['recipient'] = username[0]
                    # if it's a AuroraCoin address
                    if re.findall(r"^[aA][0-9a-zA-Z]{24,36}$", element):
                        address = re.findall(r"^[aA][0-9a-zA-Z]{24,36}$", element)
                        print "Address: " + address[0]
                        payload_item['address'] = address[0]

                    print "-------------------------------------"
                payload_item['commands'] = command_list
                payload_item['username'] = post['username']
                payload_item['post_id'] = post['id']
                payload_item['datetime'] = post_datetime
                self.payload.append(payload_item)
            print "========================================="
        else:
            print "No command found in this post: '" + post['text'] + "'"
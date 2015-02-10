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
import bitcoinaddress

COMMAND_LIST = ["history", "tip", "info", "accept", "reject", "withdraw", "balance", "pool", "autoaccept", "autowithdraw", "thank", "block", "unblock", "unregister"]

class Payload:
    def __init__(self, payload_type, api, db):
        self.payload = []
        self.log = logging.getLogger('__Aurtip__')
        
        # Payload abstraction
        # you can define a payload type here. 
        # If can parse any API accessible text.
        # The text can be in json or text file.
        
        if payload_type == "forum":
            # create a list of payload information
            self.getForumPayload(api, db)
        if payload_type == "inbox":
            # create a list of payload information
            self.getMessagePayload(api, db)
        if payload_type == "test":
            self.getTestPayload(api, db)
        self.log.debug("---Payload creation process completed successfully---")
        
    def getForumPayload(self, api, db):
        # Paging constants
        LIMIT = 30
        offset = 0
        # TODO: WRAPPER to get previous paging if the last post is not on the page
        # API call to get the web-app forum
        category_response = requests.get(api.categories_url)
        if category_response.status_code == 200:
            self.log.debug("%s - categories Received" % str(datetime.datetime.now()))
            for item in json.loads(category_response.content):
                offset = 0
                last_post_found = False
                first_new_post = True
                # get the last date from database
                try:    
                    last_post = db.get_last_post(item["category_id"])
                except Exception as e:
                    # initialize last_post to unmatchable
                    last_post = db.get_last_post(21)
                last_post_datetime = datetime.datetime.strptime(str(last_post[3]), "%Y-%m-%d %H:%M:%S")
                self.log.debug("Category: %s - Last post [ID]: %s : %s"% (str(item["category_id"]), str(last_post[2]), str(last_post_datetime)))
                # While last post not found
                while last_post_found == False:
                    threads_update_response = requests.get(api.threads_url + str(item["category_id"]) + "&limit=" + str(LIMIT) + "&offset=" + str(offset))
                    if threads_update_response.status_code == 200:
                        threads = json.loads(threads_update_response.content)
                        for post in threads["data"]:
                            # Get time from post object
                            post_updated_time_raw = post["updated_time"].split()
                            post_date_list = post_updated_time_raw[0].split(".", 3)
                            post_time_list = post_updated_time_raw[1].split(":", 3)
                            post_datetime = datetime.datetime(int(post_date_list[2]), int(post_date_list[1]), int(post_date_list[0]), int(post_time_list[0]), int(post_time_list[1]), int(post_time_list[2])) 
                                
                            
                            if last_post[2] != post["id"] and last_post_datetime <= post_datetime:
                                # insert first post into database as last_post
                                if first_new_post == True:
                                    self.log.debug("New Last Post Inserted to database: %s", (post['id']))
                                    db.insert_new_last_post(item['category_id'], post['id'], post_datetime)
                                    first_new_post = False
                                self.log.debug("Parsing new post: %s Posted at: %s  Page: %s"% (post["id"], str(post_datetime), str(offset)))
                                # parse each thread for commands
                                self.parseTextToPayload(post, str(post_datetime))
                            elif last_post[2] == post["id"]:
                                last_post_found = True
                                self.log.debug("Last post found: %s"% (str(last_post[2])))
                        if last_post_found == False:
                                #increment the page variable.
                                offset += 1
        
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
            self.log.debug("AURtip Command Found in post: %s %s"% (post['id'], post['from']['name']))
            # Make a list of strings to be used in the command parse.  Maybe more than one command per post.
            regex_commands = re.findall(r"([\+][aA][uU][rR][tT][iI][pP]($|[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}|[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}|[\s][0-9a-zA-Z\.\@\_]{1,}|[\s]))", post['text'])
            for command in regex_commands:
                payload_item = {}
                command_elements = command[0].split(" ", 4)
                self.log.debug(command_elements)
                command_list = []
                amount_list = []
                recipient_list = []
                for element in command_elements:
                    element = element.strip(".")
                    # if it's only a word it's a command
                    if re.findall(r"^[a-zA-Z]{1,12}$", element):
                        command = re.findall(r"^[a-zA-Z]{1,12}$", element)
                        if command[0] in COMMAND_LIST:
                            #print "Command: " + command[0]
                            command_list.append(command[0])
                    # if it has only numbers, or numbers and decimal
                    if re.findall(r"^[0-9]{1,6}\_[A]$", element):
                        tip_id = re.findall(r"^[0-9]{1,}\_[A]$", element)
                        print "Tip ID: " + tip_id[0]
                        payload_item['tip_id'] = tip_id[0]
                    if re.findall(r"^[0-9]{1,6}\.?[0-9]{1,8}$", element):
                        amount = re.findall(r"^[0-9]{1,6}\.?[0-9]{1,8}$", element)
                        #print "Amount: " + amount[0]
                        amount_list.append(amount[0])
                    # if it has '@' it is a username
                    if re.findall(r"[\@][0-9a-zA-Z]{1,}$", element):
                        username = re.findall(r"^[\@][0-9a-zA-Z]{1,}$", element)
                        #print "Username: " + username[0]
                        recipient_list.append(username[0])
                    # if it's a AuroraCoin address
                    if re.findall(r"^[Aa][1-9A-HJ-NP-Za-km-z]{26,34}$", element):
                        address = re.findall(r"^[Aa][1-9A-HJ-NP-Za-km-z]{26,34}$", element)
                        #print "Address: " + address[0]
                        payload_item['address'] = address[0]
                    if re.findall(r"^[a-zA-Z0-9._]{1,}[\@][a-zA-Z0-9._]{1,}[\.][a-zA-Z]{3,}$", element):
                        email = re.findall(r"^[a-zA-Z0-9._]{1,}[\@][a-zA-Z0-9._]{1,}[\.][a-zA-Z]{3,}$", element)
                        #print "Email: " + email[0]
                        payload_item['email'] = email[0]
                payload_item['commands'] = command_list
                payload_item['recipient'] = recipient_list
                payload_item['amount'] = amount_list
                payload_item['username'] = post['from']['name']
                payload_item['thread_id'] = post['id']
                payload_item['datetime'] = post_datetime
                self.payload.append(payload_item)
                self.log.debug("Payload item created successfully: %s"%(post['id']))
        else:
            self.log.debug("No command found in this post: %s %s"%(post['id'], post['from']))
        
            
    def getTestPayload(self, api, db):
        # open test text file
        # json_data = open('test_json.txt', 'r')
        # test_data = json.loads(json_data)
        with open ("test_json.txt", "r") as myfile:
            data = myfile.read().replace('\n', '')
        self.log.debug("Json Data Received from file" )
        posts = json.loads(data)
        for post in posts['data']:
            # Get time from post object
            post_updated_time_raw = post["updated_time"].split()
            post_date_list = post_updated_time_raw[0].split(".", 3)
            post_time_list = post_updated_time_raw[1].split(":", 3)
            post_datetime = datetime.datetime(int(post_date_list[2]), int(post_date_list[1]), int(post_date_list[0]), int(post_time_list[0]), int(post_time_list[1]), int(post_time_list[2])) 
            self.parseTextToPayload(post, str(post_datetime))
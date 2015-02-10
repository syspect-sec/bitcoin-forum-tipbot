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
        self.log = logging.getLogger('__Aurtip__')
        if payload_type == "forum":
            # create a list of payload information
            self.getForumPayload(api, db)
        if payload_type == "inbox":
            # create a list of payload information
            self.getMessagePayload(api, db)
        
    def getForumPayload(self, api, db):
        # Paging constants
        LIMIT = 30
        offset = 0
        # TODO: WRAPPER to get previous paging if the last post is not on the page
        # API call to get the web-app forum
        category_response = requests.get(api.categories_url)
        if category_response.status_code == 200:
            self.log.info("%s - categories Received" % str(datetime.datetime.now()))
            for item in json.loads(category_response.content):
                offset = 0
                last_post_found = False
                # get the last date from database
                try:    
                    last_post = db.get_last_post(item["category_id"])
                except Exception as e:
                    # initialize last_post to unmatchable
                    last_post = db.get_last_post(21)
                last_post_datetime = datetime.datetime.strptime(str(last_post[3]), "%Y-%m-%d %H:%M:%S")
                self.log.info("Category: %s - Last post [ID]: %s : %s"% (str(item["category_id"]), str(last_post[2]), str(last_post_datetime)))
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
                            # Insert the record of parsing the post into database
                            if last_post[2] != post["id"] and last_post_datetime <= post_datetime:
                                self.log.info("Parsing new post: %s Posted at: %s  Page: %s"% (post["id"], str(post_datetime), str(offset)))
                                # parse each thread for commands
                                self.parseTextToPayload(post, str(post_datetime))
                            elif last_post[2] == post["id"]:
                                last_post_found = True
                                self.log.info("Last post found: %s"% (str(last_post[2])))
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
            self.log.critical ("AURtip Command Found in post: %s"% (post['id']))
            #check if user is registered and if not, then register them.
            # Make a list of strings to be used in the command parse.  Maybe more than one command per post.
            regex_commands = re.findall(r"([\+][aA][uU][rR][tT][iI][pP]($|[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}|[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}|[\s][0-9a-zA-Z\.]{1,}|[\s]))", post['text'])
            #print regex_commands
            for command in regex_commands:
                payload_item = {}
                command_elements = command[0].split(" ", 4)
                self.log.debug(command_elements)
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
                    if re.findall(r"^[Aa][1-9A-HJ-NP-Za-km-z]{26,34}$", element):
                        address = re.findall(r"^[Aa][1-9A-HJ-NP-Za-km-z]{26,34}$", element)
                        print "Address: " + address[0]
                        payload_item['address'] = address[0]

                    print "-------------------------------------"
                payload_item['commands'] = command_list
                payload_item['username'] = post['username']
                payload_item['thread_id'] = post['id']
                payload_item['datetime'] = post_datetime
                self.log.critical("Payload item created successfully: %s %s"%(post['id'], post['username']))
                self.payload.append(payload_item)
            print "========================================="
        else:
            self.log.info("No command found in this post: '" + post['id'] + "'")
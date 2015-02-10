#Testing script for regex recognition of +AURtip instances
#
import os
import datetime
import re

# look for incasesenditive +aurtip and take next three words unless one of the words is +Aurtip, then break
# compile command object list from the resulting strings

def parseTextToPayload(post):
    global payload
    post_datetime = str(datetime.datetime.now())
    command_found = False
    command_valid = False
    # look for REGEX for +AURtip and take it plus next three expressions.
    if re.findall(r"(^|\s)[\+][aA][uU][rR][tT][iI][pP](\s|$)", post):
        self.log.debug "AURtip Command Found in post: %s"%(post)
        # TODO: check if user is registered and if not, then register them.
        # Make a list of strings to be used in the command parse.  Maybe more than one command per post.
        regex_commands = re.findall(r"([\+][aA][uU][rR][tT][iI][pP]($|[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}|[\s][\@]?[0-9a-zA-Z\.]{1,}[\s][\@]?[0-9a-zA-Z\.]{1,}|[\s][0-9a-zA-Z\.]{1,}|[\s]))", post)
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
            payload_item['commands'] = command_list
            payload_item['username'] = "Test_User"
            payload_item['post_id'] = "1_2104257"
            payload_item['datetime'] = post_datetime
            payload.append(payload_item)
    else:
        print "No command found in this post: '" + post + "'"

def payloadProcessor(payload): 
    #check is username is registered register if not.
    
    if "commands" in payload.values:
        for command in payload['commands']
            if command == 'info':
                #get user account info and send to user inbox
                pass
            if command == 'history':
                #get user account transaction history and send to user inbox
                pass
            if command == 'tip'
                # get recipeint username
                # get amount
                # check if user registerd and for recipeint preferences on file
                # 
                pass
            if command == 'accept'
                # check for tips waiting for that user
                # check user preferences for receiving tips
                # process the tip to that user based on preferences
                pass
            if command == 'reject'
                pass
            if command == 'withdraw'
                # check amount requested
                # check user address on file
                # send funds to user account
                # send message to user
                pass
            if command == 'balance'
                # get user account balance and send private message
                pass
            if command == 'pool'
                # change user preference to pool funds and not send tip right away
                pass
            if command == 'autodeposit'
                # change user preference to automatically transfer tip funds to pubkey address
                pass
            if command == 'autoaccept'
                # change user preference to automaticall accept the funds
                # maybe this should just be the norm
                pass
            if command == 'block'
                # get username to block or set user to be blocked from all messaging and tipping
                pass
            if command == 'unblock'
                # remove the block for a user or for all messaging and tipping
                pass
            if command == 'thank'
                # send a thanks message to the tipper
                pass
            if command == 'unregister'
                # remove user data from our database of registered users
                pass
            
#open test text file
test_file = open('regextest.txt', 'r')
payload = []
#read line by line
for line in test_file:
	payload_item = parseTextToPayload(line)
    
print payload
payloadProcessor(payload)
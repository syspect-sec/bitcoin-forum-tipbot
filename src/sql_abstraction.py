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

# Import Basic Modules
import logging  


class SqlConnection:
    def __init__(self, profile):
        self.log = logging.getLogger('__Aurtip__')
        if profile == "mysql":
            try:
                import MySQLdb
                import MySQLdb.cursors
                db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="", # your password
                      db="auroratip", # name of the data base
                      cursorclass=MySQLdb.cursors.DictCursor)
                db.autocommit(True)
                self.cur = db.cursor()
                self.log.debug("MySQL Database Connection Successful")
            except:
                self.log.debug("MySQL database error")
        if profile == 'psql':
            try:
                import psycopg2
                db = psycopg2.connect("dbname='auroratip' user='joseph' host='localhost' password=''")
                cur = db.cursor()
                self.log.debug("PSQL Database Connection Successful")
            except:
                self.log.debug("PSQL database error")
    
    def get_last_post(self, category):
        self.cur.execute("SELECT * FROM last_post WHERE category = %s ORDER BY datetime desc LIMIT 1", (category))
        last_post = self.cur.fetchone()
        return last_post
    
    def insert_new_last_post(self, category, thread_id, datetime):
        self.cur.execute("INSERT INTO last_post (category, thread_id, datetime) VALUES(%s, %s, %s)", (category, thread_id, datetime))

    def check_user_registration_status(self, username):
        self.cur.execute("SELECT count(*) as registered FROM user_data WHERE username = %s", (username))
        return self.cur.fetchone()
        
    def register_new_user(self, type, item, username=None):
        if type == "user":
            self.cur.execute("INSERT INTO user_data (username, regdate, balance, reg_thread_id, pool, auto_accept) VALUES (%s, %s, 0, %s, 1, 0)", (item["username"], item['datetime'], item["thread_id"]))
        elif type == "recipient":
            self.cur.execute("INSERT INTO user_data (username, regdate, balance, reg_thread_id, pool, auto_accept) VALUES (%s, %s, 0, %s, 1, 0)", (username, item['datetime'], item["thread_id"]))
        
    def get_user_info(self, username):
        self.cur.execute("SELECT username, regdate, CAST(SUM(balance) AS CHAR), pubkey, pool, auto_accept FROM user_data WHERE username = %s", (username))
        return self.cur.fetchone()
    
    def get_user_tip_preferences(self, username):
        tip_preferences = []
        self.cur.execute("SELECT pool FROM user_data WHERE username = %s", (username))
        tip_preferences.append(self.cur.fetchone()['pool'])
        self.cur.execute("SELECT auto_accept FROM user_data WHERE username = %s", (username))
        tip_preferences.append(self.cur.fetchone()['auto_accept'])
        return tip_preferences
    
    def change_user_preference(self, username, type, value):
        if type == "pool":
            if value == 1:
                self.cur.execute("UPDATE user_data SET pool = %s WHERE username = %s", (value, username))
            elif value == 0:
                # check that user has a pubkey onfile to withdraw to
                self.cur.execute("SELECT pubkey from user_data WHERE username = %s", (username))
                pubkey = self.cur.fetchone()['pubkey']
                if pubkey is None:
                    return False
                else:
                    self.cur.execute("UPDATE user_data SET pool = %s WHERE username = %s", (value, username))
                    return True
        if type == "auto_accept":
            self.cur.execute("UPDATE user_data SET auto_accept = %s WHERE username = %s", (value, username))
            
    def get_user_history(self, username):
        history_object = []
        self.cur.execute("SELECT * FROM withdrawls WHERE receive_username = %s", (username))
        history_object.append(self.cur.fetchall())
        self.cur.execute("SELECT * FROM deposits WHERE username = %s", (username))
        history_object.append(self.cur.fetchall())
        self.cur.execute("SELECT * FROM tip_transactions WHERE sender_username = %s", (username))
        history_object.append(self.cur.fetchall())
        self.cur.execute("SELECT * FROM tip_transactions WHERE receive_username = %s", (username))
        history_object.append(self.cur.fetchall())
        print history_object
        return history_object
    
    def get_user_receive_address(self, username):
        self.cur.execute("SELECT pubkey FROM user_data WHERE username = %s", (username))
        return self.cur.fetchone()[0]
    
    def store_tip(self, type, tip):
        withdrawn = 1 if type == "withdrawn" else 0
        accepted = 0 if type == "accepted" else 0
        rejected = 1 if type == "rejected" else 0
        self.cur.execute("INSERT INTO tip_transactions (thread_id, sender_username, receive_username, amount, datetime, accepted, withdrawn, rejected) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (tip[3], tip[0], tip[1], tip[2], tip[4], accepted, withdrawn, rejected))
        return self.cur.lastrowid
        
    def unregister_user(self, username, datetime, thread_id):
        self.cur.execute("INSERT INTO unregister_requests (userame, thread_id, datetime) VALUES (%s, %s, %s)", (username, recipient, thread_id))
        #Delete user info from user_data?
        
    def get_balance(self, username):
        self.cur.execute("SELECT CAST(SUM(balance) AS CHAR) as balance FROM user_data WHERE username = %s", username)
        return self.cur.fetchone()["balance"]
    
    def store_new_deposit_address(self, username, address):
        self.cur.execute("INSERT INTO deposit_addresses (username, deposit_pubkey) VALUES (%s, %s)", (username, address))
    
    def get_deposit_address_list(self):
        self.cur.execute("SELECT username, deposit_pubkey FROM deposit_addresses")
        return self.cur.fetchall()
    
    def change_user_receive_address(self, username, address):
        self.cur.execute("UPDATE user_data SET pubkey = %s WHERE username = %s", (address, username))
        
    def change_user_email_address(self, username, email):
        self.cur.execute("UPDATE user_data SET email = %s WHERE username = %s", (email, username))    
        
    def check_tip_status(self, username, unique_id):
        # check tip recipient and id are acceptable
        db_tip_id = unique_id.split("_", 2) 
        self.cur.execute("SELECT amount FROM tip_transactions WHERE receive_username = %s and id = %s and accepted = 0 and withdrawn = 0 and rejected = 0", (username, db_tip_id[0]))
        if self.cur.fetchone() is None:
            return False
        else:
            return True
    
    def accept_tip(self, unique_id):
        db_tip_id = unique_id.split("_", 2)
        self.cur.execute("SELECT sender_username, receive_username, amount FROM tip_transactions WHERE id = %s", db_tip_id[0])
        tip = self.cur.fetchone()
        self.cur.execute("UPDATE tip_transactions SET accepted = 1 WHERE id = %s", db_tip_id[0])
        # modify account balances
        self.cur.execute("UPDATE user_data SET balance = balance + %s WHERE username = %s", (tip['amount'],tip['receive_username']))
        return tip['amount']
        
    def reject_tip(self, unique_id):
        db_tip_id = unique_id.split("_", 2)
        self.cur.execute("SELECT sender_username, receive_username, amount FROM tip_transactions WHERE id = %s", db_tip_id[0])
        tip = self.cur.fetchone()
        self.cur.execute("UPDATE tip_transactions SET rejected = 1 WHERE id = %s", db_tip_id[0])
        
    def adjust_sender_balance(self, username, amount):
        self.cur.execute("UPDATE user_data SET balance = balance - %s WHERE username = %s", (amount, username))
        
    def deposit_to_user(self, username, amount, pubkey):
        datetime_now = datetime.datetime()
        self.cur.execute("UPDATE user_data SET balance = balance + %s WHERE username = %s", (amount, username))
        self.cur.execute("INSERT INTO deposits (username, amount, datetime, public_key) VALUES(%s, %s, %s, %s)", (username, amount, datetime_now, pubkey))

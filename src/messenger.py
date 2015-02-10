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

from email.mime.text import MIMEText
import datetime
import smtplib
import logging

class Messenger:
    
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "auroracoin.tipbot@gmail.com"
    SMTP_PASSWORD = "Auroranode"
    EMAIL_FROM = "auroracoin.wallet@gmail.com"
    EMAIL_SUBJECT = "+Aurtip response"
    EMAIL_SPACE = ", "
    DATA='We recieved a +Aurtip request.'
    EMAIL_SPACE = ", "
    DATA='We recieved a +Aurtip request.'
    
    def __init__(self, api, messages):
        self.log = logging.getLogger('__Aurtip_Messenger__')
        self.messages = messages.messages
        print messages.messages
        # import the messages payload
        
            
    def send_email():
        msg = MIMEText(DATA)
        msg['Subject'] = EMAIL_SUBJECT
        msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
        msg['From'] = EMAIL_FROM
        mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        mail.starttls()
        mail.login(SMTP_USERNAME, SMTP_PASSWORD)
        mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        mail.quit()

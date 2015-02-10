##Aurora Tipbot Readme
Author: Joseph Lee
Date: 2015-02-09
Email: joseph.lee.esl@gmail.com

1) Detailed documentation can be found in docs directory

2) Run the mysql database builder script in the database directory in MySQL or postgresql.

3) >> python tip-bot.py # will run the script to gather the forum posts, create a payload, process the payload, and fire off messages to users.

4) >> python tip-bot-bank.py # will run the script to gather deposits, credit user balances, and cold-storage the funds.

5) Create a cron tab job for each script to run on schedule depending on refresh rate of the forum.



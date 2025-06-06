import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd
import datetime
from datetime import date

maximum = 330 # maximum number of members
remindMeWhen = 10 # send an email when number of members is 10 away from maximum
mondayApiUrl = "https://api.monday.com/v2"

load_dotenv("config.env")
API_KEY = os.getenv("API_KEY")

headers = { "Authorization": API_KEY }

queryNumUsers = '{ users { name email is_view_only last_activity account { id } } }'
data  = { 'query': queryNumUsers }

req = requests.post(url = mondayApiUrl, json = data, headers = headers)
resultsDF = pd.DataFrame.from_dict(req.json()['data']['users'])
numTotal = resultsDF.shape[0] # total number of active users

numViewOnly = resultsDF[resultsDF['is_view_only'] == True].shape[0] # total number of view-only users
numUsers = numTotal - numViewOnly # total number of members/editors + admin]

today = datetime.datetime.now().timestamp() # today's date, in unix time

resultsDF['last_activity'] = pd.to_datetime(resultsDF.last_activity).astype('int64') / 10**9

if numUsers == maximum:
    print("")
    
elif numUsers == maximum - remindMeWhen:
    print("")
else:
    print("")

print(resultsDF['last_activity'])
print(today)

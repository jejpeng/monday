import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd
import datetime
from datetime import date
import numpy as np

maximum = 330 # maximum number of members
remindMeWhen = 10 # send an email when number of members is 10 away from maximum
timeLimit = 63072000 # number of seconds in 24 months - 
#                     users accounts are changed to viewer if they have not been active in 3 months

mondayApiUrl = "https://api.monday.com/v2"
load_dotenv("config.env")
API_KEY = os.getenv("API_KEY")

headers = { "Authorization": API_KEY }

queryNumUsers = '{ users { name email is_view_only last_activity id } }'
data  = { 'query': queryNumUsers }

req = requests.post(url = mondayApiUrl, json = data, headers = headers)
resultsDF = pd.DataFrame.from_dict(req.json()['data']['users'])
numTotal = resultsDF.shape[0] # total number of active users

numViewOnly = resultsDF[resultsDF['is_view_only'] == True].shape[0] # total number of view-only users
numUsers = numTotal - numViewOnly # total number of members/editors + admin]

today = datetime.datetime.now().timestamp() # today's date, in unix time

resultsDF['last_activity'] = pd.to_datetime(resultsDF.last_activity).astype('int64') / 10**9
resultsDF['time_since_last_activity'] = today - resultsDF['last_activity']
resultsDF = resultsDF.sort_values(by='time_since_last_activity', ascending=False)

inactiveUsers = resultsDF[(resultsDF['time_since_last_activity'] >= timeLimit) & (resultsDF['is_view_only'] == False)]['id'].astype('int').tolist()
# this is the number of users with editing permissions that haven't been active in 'timeLimit' amount of time

if len(inactiveUsers) > 0:
    queryChangePermissions = 'mutation { update_users_role ( user_ids: ' + str(inactiveUsers) +', new_role: VIEW_ONLY ) { updated_users { name id is_view_only } errors { user_id code message } } }'
    data2 = { 'query': queryChangePermissions }
    req2 = requests.post(url = mondayApiUrl, json = data2, headers = headers)
    queryChangeResults = req2.json()
    #print(queryChangeResults)

if numUsers == maximum:
    print("")
elif numUsers == maximum - remindMeWhen:
    print("")
else:
    print("All good")


print(numUsers)
#print(today)

import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd
import datetime
from datetime import date
import numpy as np
from smtplib import SMTP
import argparse

####### CHANGE THESE VARIABLES AS NEEDED ##########
maximum = 330 # maximum number of members on your Monday.com plan
remindMeWhen = 10 # take action when number of members is <remindMeWhen> away from maximum
timeLimitMonths = 24 # users accounts are changed to viewer if they have not been active in <timeLimitMonths> months
numUsersToRemove = 5
# then, make a file within the same folder as this file called "config.env",
# and then set the variable API_KEY to be equal to your Monday.com API key.
#
# INSTRUCTIONS AS FOLLOWS: (you can only do this if you are an admin!)
# Go to Monday.com -> click on your profile picture in the right corner -> Administration
# -> Connections -> Personal API token. 
# Generate the token and copy it.
# Paste it here:
# NEVER PUBLICLY SHOW YOUR API KEY. DO NOT PUBLISH IT ANYWHERE ONLINE. 
# PUT IT IN A SAFE DOCUMENT SOMEWHERE AND NOWHERE ELSE.

######## END OF CHANGEABLE PART ###########

load_dotenv("config.env")
API_KEY = os.getenv("API_KEY")


timeLimit = timeLimitMonths * 30 * 24 * 60 * 60 # time in seconds # 63072000 
mondayApiUrl = "https://api.monday.com/v2"
# from https://stackoverflow.com/questions/7427101/simple-argparse-example-wanted-1-argument-3-results
parser = argparse.ArgumentParser()
parser.add_argument("a", nargs='?', default="empty_string")
args = parser.parse_args()

# arguments for the request
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

if args.a == 'empty_string':
    print("empty arguments")
    print(f"Number of admin/members: {numUsers}")
    print(f"Number of inactive admin/members: {inactiveUsers}")

elif (args.a == 'remove') or (args.a == 'Remove'):
    if len(inactiveUsers) > 0:
        queryChangePermissions = 'mutation { update_users_role ( user_ids: ' + str(inactiveUsers) + ', new_role: VIEW_ONLY ) { updated_users { name id is_view_only } errors { user_id code message } } }'
        data2 = { 'query': queryChangePermissions }
        req2 = requests.post(url = mondayApiUrl, json = data2, headers = headers)
        queryChangeResults = req2.json()
        #print(queryChangeResults)
    else:
        print("No inactive users to remove.")
else:
    print("Unclear.")

'''
if numUsers >= maximum:
    print("") # ideas: - if over by x, change least active x users to view only
    # send email? see if the python script works in power automate 
    # python script does not, in fact, work - create new gmail account, use power automate to send to outlook?
elif numUsers >= maximum - remindMeWhen:
    removalCandidates = resultsDF[(resultsDF['is_view_only'] == False) & (resultsDF['time_since_last_activity'] < timeLimit)].head(numUsersToRemove)['id'].astype('int').tolist()
    queryChangePermissionsForMore = 'mutation { update_users_role ( user_ids: ' + str(removalCandidates) + ', new_role: VIEW_ONLY ) { updated_users { name id is_view_only } errors { user_id code message } } }'

else:
    print("All good")


print(numUsers)
#print(today)
'''
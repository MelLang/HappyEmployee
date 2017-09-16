
# coding: utf-8

# In[233]:

# Date: 17.9.2017
# Authors: Bianka Dorova, Melanie Langbein
# Use Case / Vision: Scenario 1 - desktop application to detect employee mood in the office 
#                           and find a way to cheer them up (show a joke or a funny picture) if they are sad 
#                           or keep them in a good mood by showing a positive note.
#                           The solution represents a way to keep employees in good mood and also monitor the 
#                           level of satisfaction in the office, so that measures can be taken if need and also 
#                           evaluated. For example, does giving the employees fruits/ chocolate for free have a 
#                           positive affect on the team, environment?
#                    Scenario 2 - extention of sceario 1, where a self moving robot is checking the facial expressions of 
#                           employees and tries to react appropriately - cheer them up (hug them) or being 
#                           excited when they seem happy.
# Implemeted prototype: Detect mood from a photo and based on the result, make the robot react appropriately.
# Prototype limitations: Development done on MacBook with Python 3.6.2 (for this version the libraries to control the camera are # supported only for Windows and Linux) therefore we used only a link to a photo from the internet.

# In[234]:

#Get the emotions from a picture 
import http.client, urllib.request, urllib.parse, urllib.error, base64, sys
import json

# Replace the example URL below with the URL of the image you want to analyze.
# Happy pic
#body = "{ 'url': 'http://gazettereview.com/wp-content/uploads/2017/01/jennifer-lopez-snapchat-username.jpg' }"

# Sad pic
body = "{ 'url': 'https://www.askideas.com/media/41/Baby-Crying-Sad-Face-Funny-Image.jpg' }"

# Angry pic
#body = "{ 'url': 'http://i.ndtvimg.com/mt/2014-08/360_anger.jpg' }"

headers = {
    # Request headers. Replace the placeholder key below with your subscription key.
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '8e4041dc87c345909b3eb3c2780ae129',
}

params = urllib.parse.urlencode({
})

try:
    # NOTE: You must use the same region in your REST call as you used to obtain your subscription keys.
    #   For example, if you obtained your subscription keys from westcentralus, replace "westus" in the 
    #   URL below with "westcentralus".
    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", "/emotion/v1.0/recognize?%s" % params, body, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
except Exception as e:
    print(e.args)


# In[235]:

import json
mood_prob = json.loads(data.decode("utf-8"))[0]["scores"]
max_prob = max(mood_prob.values())
face_rec_mood = [k for k, v in mood_prob.items() if v == max_prob][0]


# In[236]:

import requests
from requests.auth import HTTPDigestAuth
import urllib
import time
from threading import Thread

#Thanks to Phaiax for the code fixing  https://github.com/Phaiax/OhOnlyMusli/tree/master/pytest 

url = 'http://52.232.40.214/rw'
auth = HTTPDigestAuth('Default User', 'robotics')

session = requests.session()

# Get authenticated
r0 = session.get(url + '/rapid/symbol/data/RAPID/'+'T_ROB_R'+'/Remote/bStart?json=1',
                   auth=auth)
assert(r0.status_code == 200)


def check(arm, variable):
    r = session.get(url + '/rapid/symbol/data/RAPID/'+arm+'/Remote/'+variable+'?json=1')
    #print(r.status_code)
    assert(r.status_code == 200)
    return r.json()['_embedded']['_state'][0]['value']

def checkBool(arm, variable):
    return True if check(arm, variable) == "TRUE" else False

def setString(arm, variable, text):
    payload={'value':'"'+text+'"'}
    r = session.post(url + '/rapid/symbol/data/RAPID/'+arm+'/Remote/'+variable+'?action=set',
                     data=payload)
    #print(r)
    #print(r.text)
    assert(r.status_code == 204)
    return r

def setBool(arm, variable, state):
    payload={'value': 'true' if state else 'false' }
    r = session.post(url + '/rapid/symbol/data/RAPID/'+arm+'/Remote/'+variable+'?action=set',
                     data=payload)
    #print(r)
    #print(r.text)
    assert(r.status_code == 204)
    return r

def moveRobot(arm,action):
    #print("RUNNING:" + check(arm, 'bRunning'))

    setString(arm, 'stName', action)

    #print("bStart:" + check(arm, 'bStart'))

    setBool(arm, 'bStart', True);

    #print("bStart:" + check(arm, 'bStart'))
    time.sleep(0.5)

    running = checkBool(arm, 'bRunning')
    while running:
        running = checkBool(arm, 'bRunning')
        #print("RUNNING:" + str(running))
        time.sleep(0.4)

    return;

# Gestures only available for the right arm:
#   Kiss, SayHello, SayNo, ShakingHands, IKillYou
# Gestures for both arms:
#   Home, Contempt, NoClue, HandsUp, Surprised, ToDiss, Anger, Excited, GiveMeAHug, GoAway, Happy, Powerful, Scared

class otherArm_Hug(Thread):
    def run(self):
        moveRobot('T_ROB_L','GiveMeAHug')

class otherArm_Happy(Thread):
    def run(self):
        moveRobot('T_ROB_L','Happy')


# In[237]:

# API statuses
# scores : "happiness" -> Happy robot
#          "sadness"   -> Robot wants to hug
#          "anger","contempt","disgust","fear","neutral","surprise" -> Robot says hello


# In[238]:

if face_rec_mood in ['happiness']:
    otherArm_Happy().start()
    moveRobot('T_ROB_R','Happy')
    print(face_rec_mood)
if face_rec_mood in ['sadness']:
    otherArm_Hug().start()
    moveRobot('T_ROB_R','GiveMeAHug')
    print(face_rec_mood)
if face_rec_mood not in  ['sadness', 'happiness']:
    moveRobot('T_ROB_R','SayHello') 
    print(face_rec_mood)


# In[ ]:




#*****securityFaceId.py*****#

import requests
from operator import itemgetter
from twilio.rest import Client
from picamera import PiCamera
import sys
import json
import os
import urllib, httplib, base64, json
import boto3
import datetime
import time

import RPi.GPIO as GPIO
import time
BaseDirectory = '_____' # directory where picamera photos are stored
KEY = '_____' # authorization key for azure
account_sid = '_____' # twilio sid
auth_token = '_____' # twilio authorization token
group_id = 'employees' # name of personGroup
bucketName = '_____' # aws s3 bucket name

#*****Raspberry Pi pin setup*****#
Blue = 11
Red = 12
Green = 13
Pir= 16

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(Blue, GPIO.OUT)
GPIO.setup(Red, GPIO.OUT)
GPIO.setup(Green, GPIO.OUT)
GPIO.setup(Pir, GPIO.IN)

#*****Camera Setup*****#
camera = PiCamera() # initiate camera
camera.rotation = 180 # Used to correct orientation of camera

#*****FUNCTIONS*****#

# LED on off functions
def lightOff():
    GPIO.output(Red, 1)
    GPIO.output(Green, 1)
    GPIO.output(Blue, 1)
    time.sleep(.3)

def lightOn():
    GPIO.output(Red, 0)
    GPIO.output(Green, 0)
    GPIO.output(Blue, 0)
    time.sleep(.3)

# iterates through specified directory, detecting faces in .jpg files
def iter():
    for fileName in os.listdir(directory):
        if fileName.endswith('.jpg'):
            filePath = os.path.join(directory, fileName) # joins directory path with filename to create file's full path
            fileList.append(filePath)
            detect(filePath)

# detects faces in images from previously stated directory using azure post request
def detect(img_url):
    headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': KEY}
    body = open(img_url,'rb')

    params = urllib.urlencode({'returnFaceId': 'true'})
    conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
    conn.request("POST", '/face/v1.0/detect?%s' % params, body, headers)
    response = conn.getresponse()
    photo_data = json.loads(response.read())

    if not photo_data: # if post is empty (meaning no face found)
        print('No face identified')
    else: # if face is found
        for face in photo_data: # for the faces identified in each photo
            faceIdList.append(str(face['faceId'])) # get faceId for use in identify

# Takes in list of faceIds and uses azure post request to match face to known faces
def identify(ids):
    if not faceIdList: # if list is empty, no faces found in photos
        result = [('n', .0), 'n'] # create result with 0 confidence
        return result # return result for use in main
    else: # else there is potential for a match
        headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': KEY}
        params = urllib.urlencode({'personGroupId': group_id})
        body = "{'personGroupId':'employees', 'faceIds':"+str(ids)+", 'confidenceThreshold': '.5'}"
        conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/identify?%s" % params, body, headers)
        response = conn.getresponse()

        data = json.loads(response.read()) # turns response into index-able dictionary

        for resp in data:
            candidates = resp['candidates']
            for candidate in candidates: # for each candidate in the response
                confidence = candidate['confidence'] # retrieve confidence
                personId = str(candidate['personId']) # and personId
                confidenceList.append((personId, confidence))
        conn.close()
        SortedconfidenceList = zip(confidenceList, fileList) # merge fileList and confidence list
        sortedConfidence = sorted(SortedconfidenceList, key=itemgetter(1)) # sort confidence list by confidence
        return sortedConfidence[-1] # returns tuple with highest confidence value (sorted from smallest to biggest)


# takes in person_id and retrieves known person's name with azure GET request
def getName(person_Id):
    headers = {'Ocp-Apim-Subscription-Key': KEY}
    params = urllib.urlencode({'personGroupId': group_id, 'personId': person_Id})

    conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
    conn.request("GET", "/face/v1.0/persongroups/{"+group_id+"}/persons/"+person_Id+"?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = json.loads(response.read())
    name = data['name']
    conn.close()
    return name

# uses twilio rest api to send mms message, takes in message as body of text, and url of image
def twilio(message, imageLink):
    client = Client(account_sid, auth_token)

    message = client.messages.create(to='16135830816', from_='6137771920', body = message, media_url=imageLink)

    print(message.sid)

# uses aws s3 to upload photos
def uploadPhoto(fName):
    s3=boto3.resource('s3')
    data = open(fName, 'rb')
    s3.Bucket(bucketName).put_object(Key=fName, Body=data, ContentType = 'image/jpeg')

    # makes uploaded image link public
    object_acl = s3.ObjectAcl(bucketName, fName)
    response = object_acl.put(ACL='public-read')

    link = 'https://s3.amazonaws.com/'+bucketName+'/'+fName
    return link

#*****Main*****#
count = 0
while True:
    # lists are refreshed for every incident of motion
    fileList = [] # list of filePaths that were passed through as images
    faceIdList = [] # list for face id's generated using api - detect
    confidenceList = [] # list of confidence values derived from api - identify
    i = GPIO.input(Pir)
    if i==0:
        print("No Intruders")
        lightOff()
    elif i==1:
        count += 1 # count allows for a new directory to be made for each set of photos
        directory = BaseDirectory+str(count)+'/'
        print("Intruder Detected")
        lightOn()
        os.mkdir(directory) # make new directory for photos to be uploaded to
        print(count)
        print(directory)
        for x in range(0,3):
            date = datetime.datetime.now().strftime('%m_%d_%Y_%M_%S_') # change file name for every photo
            camera.capture(directory + date +'.jpg')
            time.sleep(1) # take photo every second
        iter()
        result = identify(faceIdList)
        if result[0][1] > .7: # if confidence is greater than .7 get name of person
            twilio(getName(result[0][0])+' is in the Office.', uploadPhoto(result[1]))
            time.sleep(600) # if recognized stop for 10 mins
        else:
            for files in fileList:
                link = uploadPhoto(files) # upload all photos of incident for evidence
            twilio('Motion Detected in the Office.', link) # send message
            time.sleep(30) # wait 30 seconds before looking for motion again




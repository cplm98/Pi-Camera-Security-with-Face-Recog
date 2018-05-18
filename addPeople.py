#*****addPeople.py*****#
import urllib, httplib, base64, json
import sys
import os

people = ['list of names goes here']
nameAndID = [] # empty list for persons' name and personId
group_id = 'employees'
KEY = 'your access key goes here'

# creates people in personGroup of specified group_Id
def addPeople():
    headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': KEY}
    params = urllib.urlencode({'personGroupId': group_id})
    conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
    for name in people:
        body = "{'name':'"+name+"'}"
        conn.request("POST", "/face/v1.0/persongroups/{employees}/persons?%s" % params, body, headers)
        response = conn.getresponse()
        data = json.loads(response.read()) # turns response into index-able dictionary
        out = name+"'s ID: " +data['personId']
        print(out)
        nameAndID.append((name, data['personId'])) # fills list with tuples of name and personId
    conn.close()
    return nameAndID

# adds faces to the created people in PersonGroup
def addFaceToPerson(list):
    headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key':KEY}
    conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
    for item in list:
        params = urllib.urlencode({'personGroupId': group_id, 'personId': item[1]}) # item[1] is the personId created from addPeople()
        directory = '/home/pi/Projects/People/'+item[0] # item[0] is peron's name, each person should have a directory named after them filled with photos of them
        for filename in os.listdir(directory):
            if filename.endswith('.jpg'): # adjust this depending on the file type of your photos
                filePath = os.path.join(directory, filename) # creates full file path
                body = open(filePath,'rb')
                conn.request("POST", "/face/v1.0/persongroups/{employees}/persons/"+item[1]+"/persistedFaces?%s" % params, body, headers)
                response = conn.getresponse()
                data = json.loads(response.read()) # successful run will print persistedFaceId
                print(data)
    conn.close()

addFaceToPerson(addPeople())

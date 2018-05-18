#*****trainPersonGroup.py*****#
import urllib, httplib, base64, json

group_id = 'employees'
KEY = 'you access key goes here'

params = urllib.urlencode({'personGroupId': group_id})
headers = {'Ocp-Apim-Subscription-Key': KEY}

conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
conn.request("POST", "/face/v1.0/persongroups/employees/train?%s" % params, "{body}", headers)
response = conn.getresponse()
data = json.loads(response.read())
print(data) # if successful prints empty json body

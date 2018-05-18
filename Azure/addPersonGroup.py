#*****addPersonGroup.py*****#
import requests
import urllib, httplib, base64

KEY = 'your access key goes here'

group_id = 'employees'
body = '{"name": "Employees"}'
params = urllib.urlencode({'personGroupId': group_id})
headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': KEY}

conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
conn.request("PUT", "/face/v1.0/persongroups/{personGroupId}?%s" % params, body, headers)
response = conn.getresponse()
data = response.read()
print(data)
conn.close()

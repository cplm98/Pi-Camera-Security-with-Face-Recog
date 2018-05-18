#*****checkTrainingStatus.py*****#
import urllib, httplib, base64, json

group_id = 'employees'
KEY = 'you access key goes here'

headers = {'Ocp-Apim-Subscription-Key': KEY}
params = urllib.urlencode({'personGroupId': group_id})
conn = httplib.HTTPSConnection('eastus2.api.cognitive.microsoft.com')
conn.request("GET", "/face/v1.0/persongroups/"+group_id+"/training?%s" % params, "{body}", headers)
response = conn.getresponse()
data = json.loads(response.read())
print(data)
conn.close()

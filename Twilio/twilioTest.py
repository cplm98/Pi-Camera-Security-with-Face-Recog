#*****twilioTest.py*****#
from twilio.rest import Client

account_sid = 'your sid'
auth_token = 'you auth token'

client = Client(account_sid, auth_token)
message = client.messages.create(to='your phone number',
                                 from_='your twilio number',
                                 body = "hello",
                                 media_url="your pic.jpg url")
print(message.sid)

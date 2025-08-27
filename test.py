import requests
from utils.pydantic_models import *

surl = 'http://localhost:5000'

def handle_endpoint(endpoint:str,payload:dict):    
    res = requests.post(
        url=surl+endpoint,
        json=payload
    )
    print(res.json())
    return res.json()

payload = Ticket(
    issuer='root',
    content='test ticket',
).model_dump()
# create the ticket
res = handle_endpoint('/push',payload)
tid = res['ticket']['id']
payload = AssignRequest(
    id=tid,
    assigned_to='chi'
).model_dump()
# assign ticket
res = handle_endpoint('/assign',payload)
# start ticket
res = handle_endpoint('/start',payload)
# get the ticket from the pile
print(requests.get(surl+'/pile/ticket/?id=' + str(tid)))

payload = CompleteRequest(
    id = tid,
    # use any assigned to for complete request doesnt matter
    assigned_to='root',
    content='test ticket content'
).model_dump()
# complete the ticket
res = handle_endpoint('/complete',payload)

print(requests.get(surl+'/pile/completions').json())

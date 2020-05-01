import requests
import binascii
import hmac
import hashlib
import json

ENV = '-sbx'
MAX_MESSAGES = 10
BODY_MAX_MESSAGES = ('{"maxNumberOfMessages": %s}' % MAX_MESSAGES).encode('utf-8')
SECRET_KEY = 'secret_key'
HEADERS = {
    'Content-Type': 'application/json',
    'X-Dispatch-Key': 'public_key'
}
b_secret_key = bytearray.fromhex(SECRET_KEY)  # translate key from hex to bytes
# Calculate the hash and assign to HTTP header
digester = hmac.new(b_secret_key, BODY_MAX_MESSAGES, hashlib.sha256)
out_headers = HEADERS
out_headers['X-Dispatch-Signature'] = binascii.hexlify(digester.digest()).decode('utf-8')
# Post to agent/out
out_response = requests.post('https://connect%s.dispatch.me/agent/out' % ENV, headers=out_headers, 
                             data=BODY_MAX_MESSAGES)
msgs = json.loads(out_response.text)
while msgs:
    for msg in msgs:
        m = msg['Message']
        req_type = m['Request']['Type']
        payload = m['Request']['Payload']
        
        ##########################################################
        # Download the payload for subsequent processing to your system
        # VERY IMPORTANT: This operation should take a few millisecs for each record - if it will take more please reach out to your Dispatch contact
        ##########################################################

        # After processing the message post acknowledgement
        receipt = '{"Receipt":"%s","ProcedureID":"%s","Result":"success"}' % \
                  (m['Receipt'], m['Request']['ProcedureID'])
        receipt = receipt.encode('utf-8')
        # Calculate the hash and assign to HTTP header
        digester = hmac.new(b_secret_key, receipt, hashlib.sha256)
        ack_headers = HEADERS
        ack_headers['X-Dispatch-Signature'] = binascii.hexlify(digester.digest()).decode('utf-8')
        # Post to agent/ack
        ack_response = requests.post('https://connect%s.dispatch.me/agent/ack' % ENV, headers=ack_headers, 
                                     data=receipt)
        print(ack_response.status_code)

    if len(msgs) == MAX_MESSAGES:
        digester = hmac.new(b_secret_key, BODY_MAX_MESSAGES, hashlib.sha256)
        out_headers = HEADERS
        out_headers['X-Dispatch-Signature'] = binascii.hexlify(digester.digest()).decode('utf-8')

        out_response = requests.post('https://connect%s.dispatch.me/agent/out' % ENV, headers=out_headers,
                                     data=BODY_MAX_MESSAGES)
        msgs = json.loads(out_response.text)
    else:
        msgs = None
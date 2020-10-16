import requests
import binascii
import hmac
import hashlib
import gzip

ENV = '-sbx'    # for production you can just set this to '' i.e. production API https://api.dispatch.me
SECRET_KEY = 'your_secret_key'
HEADERS = {
    'Content-Type': 'application/json',
    'X-Dispatch-Key': 'your_public_key',
    'MessageId': 'unique_id_for_transaction'  # optional
}

# The `record_type` would be `organization`, `user` depending on what you're trying to send over. Refer to the playbook
# This external ID fields reference the IDs unique in your system
PAYLOAD = r"""
[
    {
        "header":{
            "record_type": "job",
            "version": "v3"
        },
        "record":{
            "external_id": "dispatchme_1019_1",
            "external_organization_id": "dispatchme",
            "title": "Priority: TEST Dispatch TEST - Standard | Model Name: 24\" UNDERCOUNTER REFRIGERATOR, RIGHT HINGE",
            "description": "**Product Serial Number:** 2464376\n\n**Product Model Number:** UC-24R-RH\n\n**Product Model Name:** 24\" UNDERCOUNTER REFRIGERATOR, RIGHT HINGE\n\n**Problem Description:** THIS IS A DM TEST.\n\n**KB Article:** https://km.acme.com/advisor/showcase?project=ACME&case=K29130342\n\n**Special Authorization:** http://service.acme.com/specialauthentry/createinternal/?ticketnumber=004-00-9004007\n\n**Unit History:** http://service.acme.com/Tools/UnitHistory?SerialNumber=2464376\n\n**Product Full Warranty:** 2019-06-05\n\n**Product Parts Warranty**: 2029-06-05\n\n**Product SS Warranty**: 2022-06-05\n\n**ASKO Article Number**: \n\n**Installer**: \n\n**ACME Ticket ID**: test-ud-13012\n\n",
            "service_fee": 400,
            "service_fee_precollected": true,
            "equipment_descriptions": [
                {
                    "manufacturer": "ACME Freezer Company",
                    "model_number": "UC-24R-RH",
                    "serial_number": "2464376",
                    "installation_date": "2017-06-05",
                    "equipment_type": "Undercounter 24"
                }
            ],
            "symptom": "Door won't open",            
            "status": "offered",
            "address":{
                "postal_code": "01235",
                "city": "Boston",
                "state": "MA",
                "street_1": "122 Summer St",
                "street_2": "apt 1"
            },
            "service_type": "plumber",
            "customer": {
                "first_name": "Mitch",
                "last_name": "Davis",
                "external_id": "mitchdavis",
                "email": "devs+mitchdavis@dispatch.me",
                "phone_numbers":[
                   {
                      "number":"5552312325",
                      "type":"mobile",
                      "primary":true
                   }
                ],
                "home_address": {
                        "street_1": "72613 Porsche Street",
                        "city": "Revere",
                        "state": "MA",
                        "postal_code": "02151"
                }
            },
             "marketing_attributions": [
              {
                "content": "bingo",
                "campaign": "mamba",
                "source": "orca",
                "term": "glitter",
                "media": "twitter"
              }
            ]
        }
    }
]
"""

gzip_payload = gzip.compress(PAYLOAD.encode())
b_secret_key = bytearray.fromhex(SECRET_KEY)
digester = hmac.new(b_secret_key, gzip_payload, hashlib.sha256)
in_headers = HEADERS
in_headers['X-Dispatch-Signature'] = binascii.hexlify(digester.digest()).decode('utf-8')
post = requests.post('https://connect%s.dispatch.me/agent/in' % ENV, headers=in_headers, data=gzip_payload)
print(post.status_code)
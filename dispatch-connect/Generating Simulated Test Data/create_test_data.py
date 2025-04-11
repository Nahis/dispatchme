# This simulates jobs that are received from the Enterprise into Dispatch. 
# You will subsequently pick these up and process into your environment.

import requests
import binascii
import hmac
import hashlib
import gzip

#  Make sure to change the brand_job_id for every run. Otherwise when
#  you run again, it will update rather than insert a new record
brand_job_id = "some_unique_id"

# the next two are values you need to update only once when you start testing
test_data_generation_key = "account_key"
test_org_id = 00000

# DO NOT CHANGE THIS!
test_data_generation_id = "account|110|noop"


headers = {
    'Content-Type': 'application/json',
    'X-Dispatch-Key': test_data_generation_id
}

payload = r"""
[
    {
        "header":{
            "record_type": "job",
            "version": "v3"
        },
        "record":{
            "organization_id": %s,
            "external_id": "%s",
            "title": "job %s",
            "source": "web",
            "status": "offered",
            "description": "some description",
            "address":{
                "postal_code": "01235",
                "city": "Boston",
                "state": "MA",
                "street_1": "122 Summer St",
                "street_2": "apt 1"
            },
            "service_type": "plumber",
            "customer": {
                "first_name": "Jason",
                "last_name": "Davis",
                "external_id": "%s",
                "email": "devs+jasondavis@dispatch.me",
                "home_address": {
                        "street_1": "71601 Ford Street",
                        "city": "Revere",
                        "state": "MA",
                        "postal_code": "02151"
                }               
            },
            "equipment_descriptions": [{
                  "manufacturer": "Sub-Zero Freezer Company",
                  "model_number": "700BCI",
                  "serial_number": "2397767",
                  "installation_date": "2006-10-23T00:00:00+0000",
                  "equipment_type": "Pro 48"
            }],
            "symptom": "Display dark | Alyssa DeJong - 11/21/2018 4:02:04 PM (Central Standard Time)\n- interior light on, display dark, unit not cooling\n- advised reset at breaker\n- advised if no change possible panel, electrical, or board issue\n- referred to FCS if reset does not resolve\n- referred to FCS, dispatched\n- cust. can be reached by phone or email, phone best after 2:00pm",
            "service_fee_precollected": 0,
            "service_fee": 100,
            "service_instructions": "some instruction"                        
        }
    }
]
""" % (test_org_id, brand_job_id, brand_job_id, brand_job_id)

payload = gzip.compress(payload.encode())   
secret_key = bytearray.fromhex(test_data_generation_key)  
digester = hmac.new(secret_key, payload, hashlib.sha256)
headers['X-Dispatch-Signature'] = binascii.hexlify(digester.digest()).decode('utf-8')
post = requests.post('https://connect-sbx.dispatch.me/agent/in', headers=headers, data=payload)

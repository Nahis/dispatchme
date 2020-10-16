import requests
import binascii
import hmac
import hashlib
import gzip

ENV = '-sbx'
SECRET_KEY = 'your_secret_key'
HEADERS = {
    'Content-Type': 'application/json',
    'X-Dispatch-Key': 'your_public_key',
    'MessageId': 'unique_id_for_transaction'  # optional    
    'RecordType': 'job' # The would be `organization`, `user` etc. (any identify value is acceptable) depending on what you're trying to send over. Refer to the playbook
}

# The payload here can be any valid structure representing the data as comig out of your system
PAYLOAD = r"""
[
    {
        "your_field_1": "field 1 value",
        "your_field_2": "field 2 value"
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
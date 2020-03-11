<?php

$key = 'your_public_key';
$secret = 'your_secret_key';
$payloadData = '[
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
            "symptom": "Door wont open",            
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
]';
$compressed = gzencode(utf8_encode($payloadData));
$secret = hex2bin($secret);
$sign = hash_hmac('sha256', $compressed, $secret, true);
$sign = utf8_decode(bin2hex($sign));
$curl = curl_init();
curl_setopt_array($curl, array(
    CURLOPT_URL => "https://connect-sbx.dispatch.me/agent/in",
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING => "",
    CURLOPT_MAXREDIRS => 10,
    CURLOPT_TIMEOUT => 0,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => "POST",
    CURLOPT_POSTFIELDS => $compressed,
    CURLOPT_HTTPHEADER => array(
        "Content-Type: application/json",
        "X-Dispatch-Key: $key",
        "X-Dispatch-Signature: $sign"
    ),
));
$response = curl_exec($curl);
curl_close($curl);

echo $response;
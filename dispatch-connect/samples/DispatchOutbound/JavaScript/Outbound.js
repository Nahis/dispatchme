var http = require('http');
http.createServer(function (req, res) {
}).listen(1337, "127.0.0.1");

var key = 'your_key';
var secret = 'your_secret';
var url = 'https://connect-sbx.dispatch.me/';
var method = 'POST';
var max_messages = 10;
var out_payload = `{"maxNumberOfMessages":${max_messages}}`;
var secret = Buffer.from(secret, 'hex');
const crypto = require('crypto');
var out_signature = crypto.createHmac('sha256', secret).update(out_payload, 'utf8').digest('hex');
var out_headers = {
  'Content-Type': 'application/json',
  'X-Dispatch-Key': key,
  'X-Dispatch-Signature': out_signature
};

var out_request = {
    url: url + 'agent/out',
    method: 'POST',
    headers: out_headers,
    body: out_payload
};

const request = require('request');
request(out_request, function(err, res, body) {
    var msgs = JSON.parse(body);
    if (msgs.length) { 
        msgs.forEach(msg => {
            var m = msg.Message;
            var req_type = m.Request.Type;
            var payload = m.Request.Payload;
            console.log(payload);
            /*
            ##########################################################
            # Download the payload for subsequent processing to your system
            ##########################################################
            */
            var receipt = `{"Receipt":"${m.Receipt}","ProcedureID":"${m.Request.ProcedureID}","Result":"success","Error":""}`;
            receipt = unescape(encodeURIComponent(receipt));
            var ack_signature = crypto.createHmac('sha256', secret).update(receipt, 'utf8').digest('hex');
            var ack_headers ={
                'Content-Type': 'application/json',
                'X-Dispatch-Key': key,
                'X-Dispatch-Signature': ack_signature
            };
            var ack_request = {
                url: url + 'agent/ack',
                method: 'POST',
                headers: ack_headers,
                body: receipt
            };
            request(ack_request, function(err, res, body) {
                let r = body;
            });
        });
        if (msgs.length == max_messages) {
            out_signature = crypto.createHmac('sha256', secret).update(out_payload, 'utf8').digest('hex');
            out_headers = {
                'Content-Type': 'application/json',
                'X-Dispatch-Key': key,
                'X-Dispatch-Signature': out_signature
            };
            out_request = {
                url: url + 'agent/out',
                method: 'POST',
                headers: out_headers,
                body: out_payload
            };                
            request(out_request, function(err, res, body) {
                msgs = JSON.parse(body);
            });
        } else {
            msgs = [];
        }
    }
});

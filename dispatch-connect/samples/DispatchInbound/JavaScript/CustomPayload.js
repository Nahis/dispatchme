function post() {
    const zlib = require('zlib');
    var crypto = require('crypto');

    var key = 'your_key';
    var secret = 'your_secret';

    var payload = zlib.gzipSync('Hello, world!');
    var secret = Buffer.from(secret, 'hex');
    var signature = crypto.createHmac('sha256', secret).update(payload, 'utf8').digest('hex');

    xhttp.open("POST", "https://connect-sbx.dispatch.me/agent/in", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader("X-Dispatch-Key", key);
    xhttp.setRequestHeader("X-Dispatch-Signature", signature);
    xhttp.setRequestHeader("MessageId", "unique_id_for_transaction");  // optional
    xhttp.send(payload);    
}
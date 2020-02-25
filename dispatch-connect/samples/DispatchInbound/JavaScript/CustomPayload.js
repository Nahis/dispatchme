function post() {
    const zlib = require('zlib');
    var crypto = require('crypto');

    var secret = 'your_secret';
    var key = 'your_key';

    var payload = zlib.gzipSync('Hello, universe!');
    var secret = Buffer.from(secret, 'hex');
    var signature = crypto.createHmac('sha256', secret).update(payload, 'utf8').digest('hex');
    var request = {
      url: 'https://connect-sbx.dispatch.me/agent/in',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Dispatch-Key': key,
        'X-Dispatch-Signature': signature
      },
      data: payload
    }; 
}
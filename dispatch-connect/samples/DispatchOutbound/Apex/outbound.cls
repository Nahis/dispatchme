public class DispatchRestAPICallout {

          public static void getJOBDetails () {

            HTTP http = new HTTP();
            String data =   '{"maxNumberOfMessages": 10}';
            data = EncodingUtil.urlEncode(data, 'UTF-8');
        	String privKey = '';
        	String publicKey = '';
        	String endpoint='https://connect-sbx.dispatch.me/agent/out';
        	HttpRequest request = new HttpRequest();
    		String signature = generateHmacSHA256Signature(data, privKey);
    		System.debug('Signature : '+signature);
            String signatureHex = EncodingUtil.urlEncode(signature,'UTF-8');              
        	
        	request.setHeader('Content-Type', 'application/json');
        	request.setHeader('X-Dispatch-Key',publicKey);
        	request.setHeader('X-Dispatch-Signature',signatureHex);
            request.setBody(data);        
        	request.setMethod('POST');
        	request.setEndpoint(endpoint);
              
            HttpResponse response = http.send(request);
            system.debug('response: ' + response.getBody());
            JSONParser parser = JSON.createParser(response.getBody());
            system.debug('parser: ' + parser);
    }    
    
    private static String generateHmacSHA256Signature(String saltValue, String secretKeyValue) {
        
        blob privateKey = Blob.valueOf(secretKeyValue);
        system.debug('privateKey::'+privateKey);
        blob input = Blob.valueOf(saltValue);
		system.debug('input::'+input);
        String algorithmName = 'HmacSHA256';
        Blob hmacData = Crypto.generateMac(algorithmName, input, privateKey);
        system.debug('hmacData::'+hmacData);
        return EncodingUtil.convertToHex(hmacData);
	}

}
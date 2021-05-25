/*
Developer Name  : Nishant Kumar
Description		: This class is created to create JOBS in Dispatch through REST Integration call. Creating the payload and then passing data
				  to create multiple jobs.	
Date of change	: 8/6/2020 					  
*/
public class DispatchConnectInbound {

          public static void getJobDetails () {

            HTTP http = new HTTP();
        	String privKey = 'your_secret'; 
        	String publicKey = 'your_public_key';
        	String endpoint='https://connect-sbx.dispatch.me/agent/in';
            String data =
                    '[{' +
                            '"header":{' +
                                '"record_type": "job",' +      // The `record_type` would be `organization`, `user` depending on what you're trying to send over. Refer to the playbook
                                '"version": "v3"' +
                            '},' +
                            '"record":{' +
                                '"external_organization_id": "Balkan",' +   // This would reference the ID unique in your system
                                '"title": "some title_07_31_22",' +
                                '"status": "offered",' +
                                '"description": "some description",' +
                                '"external_id": "07_31_22",' +              // This would reference the ID unique in your system
                                '"address":{' +
                                    '"postal_code": "01235",' +
                                    '"city": "Boston",' +
                                    '"state": "MA",' +
                                    '"street_1": "125 Summer Street",' +
                                    '"street_2": "apt 5"' +
                                '},' +
                                '"service_type": "plumber",' +
                                '"customer": {' +
                                    '"first_name": "Nishant1",' +
                                    '"last_name": "Kumar1",' +
                                    '"external_id": "07_31_22ABCD",' +               // This would reference the ID unique in your system
                                    '"email": "nishantkumar@dispatch.me",' +
                                    '"home_address": {' +
                                    '"street_1": "71605 Ford Street",' +
                                    '"city": "Revercity",' +
                                    '"state": "MA",' +
                                    '"postal_code": "02155"' +
                                '}' +
                                '},' +
                                '"equipment_descriptions": [{' +
                                    '"manufacturer": "Sub-Zero Freezer Company",' +
                                    '"model_number": "700BCI",' +
                                    '"serial_number": "2397767",' +
                                    '"installation_date": "2006-10-23T00:00:00+0000",' +
                                    '"equipment_type": "Pro 48"' +
                                '}],' +
                                '"symptom": "problem description",' +
                                '"service_fee_precollected": 0,' +
                                '"service_fee": 100,' +
                                '"service_instructions": "some instruction"' +
                                '}' +
                            '}]';
  
        	HttpRequest request = new HttpRequest();
    		String signature = generateHmacSHA256Signature(data, privKey);
    		System.debug('Signature : '+signature);
            String signatureHex = EncodingUtil.urlEncode(signature,'UTF-8');              
        	
        	request.setHeader('Content-Type', 'application/json');
        	request.setHeader('X-Dispatch-Key',publicKey);
        	request.setHeader('X-Dispatch-Signature',signatureHex);
            request.setHeader("MessageId", "unique_id_for_transaction");  // optional
            request.setHeader('Accept-Encoding', 'gzip');
            request.setBody(data);        
        	request.setMethod('POST');
        	request.setEndpoint(endpoint);
              
            HttpResponse response = http.send(request);
            system.debug('response: ' + response.getBody());
            JSONParser parser = JSON.createParser(response.getBody());
            system.debug('parser: ' + parser);
    }    
    
    private static String generateHmacSHA256Signature(String payLoad, String secretKeyValue) {
      
        blob privateKey = EncodingUtil.convertFromHex(secretKeyValue);
        system.debug('privateKey::'+privateKey);
        blob input = Blob.valueOf(payLoad);
		system.debug('input::'+input);
        String algorithmName = 'HmacSHA256';
        Blob hmacData = Crypto.generateMac(algorithmName, input, privateKey);
        system.debug('hmacData::'+hmacData);
        return EncodingUtil.convertToHex(hmacData);
	}
}
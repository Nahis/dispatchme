/*
Developer Name  : Nishant Kumar
Description     : This class is created to call the Dispatch REST Integration. Fetching the JSON response from Dispatch and Sending the ACK
Date of change  : 8/6/2020
*/
// Currently we can call this class method using below command in anonymous window but later we can set Batch class.
public class DispatchConnectOutbound {    
    //This method actually call the REST Integartion using payload and secret key.
    //Later we can move this endpoint to custom label or custom setting.
    //Parameteres : data = Payload & type = out
    public static HttpResponse PerformDispatchPostCall(String data,String type)
    {
            HTTP http = new HTTP(); 
            //Set URL, Public key and Private Key in custom metadata 
            Dispatch_Credentials__mdt dispatchCred = [SELECT Dispatch_Private_Key__c, Dispatch_Public_Key__c, Dispatch_URL__c FROM Dispatch_Credentials__mdt];
            String privKey = dispatchCred.Dispatch_Private_Key__c;
            String publicKey = dispatchCred.Dispatch_Public_Key__c;
            String endpoint= dispatchCred.Dispatch_URL__c+type;

            System.debug('test endpoint::'+endpoint);
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
            system.debug('response ' + response);
            system.debug('response body' + response.getBody());
            return response;
    }
    
    @future(callout=true)
    public static void PerformDispatchPostCallACK(String data,String type)
    {
            HTTP http = new HTTP(); 
            Dispatch_Credentials__mdt dispatchCred = [SELECT Dispatch_Private_Key__c, Dispatch_Public_Key__c, Dispatch_URL__c FROM Dispatch_Credentials__mdt];
            String privKey = dispatchCred.Dispatch_Private_Key__c;
            String publicKey = dispatchCred.Dispatch_Public_Key__c;
            String endpoint= dispatchCred.Dispatch_URL__c+type;
            System.debug('test endpoint::'+endpoint);
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
            system.debug('response ' + response);
            system.debug('response body' + response.getBody());
    }

    //This method is creating the  Signature using Payload and SecretKey and then return Hex value of that signature key.
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
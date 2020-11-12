public class DispatchAPIConnectorAgentOutIterable implements Iterator<DispatchAPIConnectorAgentOut.DispatchAPIResponse>{ 
 
    DispatchAPIConnectorAgentOut.DispatchAPIResponse recs {get; set;} 
    HttpRequest out_request;
    HTTP http = new HTTP();
    String publicKey;
    String secret;
    String endpoint = '.dispatch.me/agent/';
    Integer i {get; set;}
 
    public DispatchAPIConnectorAgentOutIterable() {
        Map<String,String> settings = DispatchUtils.getDispatchSettings();
        if (settings.get(DispatchUtils.setting_env) == 'PRODUCTION') {
            this.endpoint = 'https://connect' + this.endpoint;
        } else {
            this.endpoint = 'https://connect-sbx' + this.endpoint;
        }
        publicKey = DispatchUtils.decrypt(settings.get('CONNECTOR_ID'));
        secret = DispatchUtils.decrypt(settings.get('CONNECTOR_SECRET'));
        out_request = prepareConnectorHttpRequest(this.publicKey, this.secret, '{"maxNumberOfMessages": 10}', this.endpoint + 'out');
        i = 0;
    }   
 
    public boolean hasNext() {
        if (i > 50) {  // to limit the number of API calls so that it remains within governor limits
            return False;
        }
        HttpResponse out_response = http.send(out_request);
        recs = get_recs(out_response); 
        for (DispatchAPIConnectorAgentOut.DispatchAPIObject rec : recs.Messages) {
            String payload = '{"Receipt":"'+rec.Message.Receipt+'","ProcedureID":"'+rec.Message.Request.ProcedureID+'","Result":"success"}';
            HttpRequest ack_request = prepareConnectorHttpRequest(this.publicKey, this.secret, payload, this.endpoint + 'ack');
            HttpResponse ack_response = http.send(ack_request);
        }
        return recs.Messages.size() > 0;
    }
 
    public DispatchAPIConnectorAgentOut.DispatchAPIResponse next() {
        i++;
        return recs;
    }

    private static DispatchAPIConnectorAgentOut.DispatchAPIResponse get_recs(HttpResponse response) {
        return (DispatchAPIConnectorAgentOut.DispatchAPIResponse)JSON.deserialize('{"Messages": ' + response.getBody()+ '}', DispatchAPIConnectorAgentOut.DispatchAPIResponse.class);
    }

    private static HttpRequest prepareConnectorHttpRequest(String publicKey, String secretKey, String payload, String endpoint) {
        HttpRequest request = new HttpRequest();
        String signature = EncodingUtil.convertToHex(Crypto.generateMac('HmacSHA256', Blob.valueOf(payload), EncodingUtil.convertFromHex(secretKey)));
        request.setHeader('Content-Type', 'application/json');
        request.setHeader('X-Dispatch-Key', publicKey);
        request.setHeader('X-Dispatch-Signature', EncodingUtil.urlEncode(signature,'UTF-8'));
        request.setBody(payload);
        request.setMethod('POST');
        request.setEndpoint(endpoint);
        return request;
    }	

}
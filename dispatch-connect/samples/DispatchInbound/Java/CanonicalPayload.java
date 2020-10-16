import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.zip.GZIPOutputStream;

public class DispatchInbound {

    public static void main(String[] args) {
        try {
            String PublicKey = "your_public_id";
            String SecretKey = "your_secret_key";
            String Payload =
                    "[{" +
                            "\"header\":{" +
                                "\"record_type\": \"job\"," +      // The `record_type` would be `organization`, `user` depending on what you're trying to send over. Refer to the playbook
                                "\"version\": \"v3\"" +
                            "}," +
                            "\"record\":{" +
                                "\"external_organization_id\": \"dispatchme\"," +   // This would reference the ID unique in your system
                                "\"title\": \"some title\"," +
                                "\"status\": \"offered\"," +
                                "\"description\": \"some description\"," +
                                "\"external_id\": \"12_03_03\"," +              // This would reference the ID unique in your system
                                "\"address\":{" +
                                    "\"postal_code\": \"01235\"," +
                                    "\"city\": \"Boston\"," +
                                    "\"state\": \"MA\"," +
                                    "\"street_1\": \"122 Summer St\"," +
                                    "\"street_2\": \"apt 1\"" +
                                "}," +
                                "\"service_type\": \"plumber\"," +
                                "\"customer\": {" +
                                    "\"first_name\": \"Jason\"," +
                                    "\"last_name\": \"Davis\"," +
                                    "\"external_id\": \"11_22_01\"," +               // This would reference the ID unique in your system
                                    "\"email\": \"devs+jasondavis@dispatch.me\"," +
                                    "\"home_address\": {" +
                                    "\"street_1\": \"71601 Ford Street\"," +
                                    "\"city\": \"Revere\"," +
                                    "\"state\": \"MA\"," +
                                    "\"postal_code\": \"02151\"" +
                                "}" +
                                "}," +
                                "\"equipment_descriptions\": [{" +
                                    "\"manufacturer\": \"Sub-Zero Freezer Company\"," +
                                    "\"model_number\": \"700BCI\"," +
                                    "\"serial_number\": \"2397767\"," +
                                    "\"installation_date\": \"2006-10-23T00:00:00+0000\"," +
                                    "\"equipment_type\": \"Pro 48\"" +
                                "}]," +
                                "\"symptom\": \"problem description\"," +
                                "\"service_fee_precollected\": 0," +
                                "\"service_fee\": 100," +
                                "\"service_instructions\": \"some instruction\"" +
                                "}" +
                            "}]";

            // gZip the Payload
            byte[] bPayload = Payload.getBytes(java.nio.charset.StandardCharsets.UTF_8);
            byte[] gZipPayload = Compress(bPayload);

            // Calculate Dispatch Signature
            byte[] bSecretKey = ConvertHexStringToByteArray(SecretKey);
            String XDispatchSignature = GetSignatureHash(bSecretKey, gZipPayload);

            URL url = new URL("https://connect-sbx.dispatch.me/agent/in");  // the production API is https://connect.dispatch.me
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json");
            con.setRequestProperty("X-Dispatch-Key", PublicKey);
            con.setRequestProperty("X-Dispatch-Signature", XDispatchSignature);
            con.setRequestProperty("MessageId", "unique_id_for_transaction");  // optional
            con.setDoOutput(true);
            DataOutputStream gzipOutputStream = new DataOutputStream(con.getOutputStream());
            gzipOutputStream.write(gZipPayload);
            gzipOutputStream.flush();
            gzipOutputStream.close();
            System.out.println(con.getResponseMessage());
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    private static byte[] Compress(byte[] content)
    {
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        try {
            GZIPOutputStream gzipOutputStream = new GZIPOutputStream(byteArrayOutputStream);
            gzipOutputStream.write(content);
            gzipOutputStream.close();
        } catch(IOException e){
            throw new RuntimeException(e);
        }
        return byteArrayOutputStream.toByteArray();
    }

    private static byte[] ConvertHexStringToByteArray(String hexString)
    {
        int len = hexString.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2){
            data[i / 2] = (byte) ((Character.digit(hexString.charAt(i), 16) << 4)
                    + Character.digit(hexString.charAt(i+1), 16));
        }
        return data;
    }

    private static String GetSignatureHash(byte[] key, byte[] message) throws Exception
    {
        byte[] returnVal = null;
        String algorithm="HmacSHA256";
        SecretKeySpec signingKey = new SecretKeySpec(key, algorithm);
        Mac mac = Mac.getInstance(algorithm);
        mac.init(signingKey);
        returnVal = mac.doFinal(message);
        StringBuilder hashString = new StringBuilder();
        for (byte x : returnVal)
        {
            hashString.append(String.format("%02x", x));
        }
        return hashString.toString();
    }
}
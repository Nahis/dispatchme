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
            // The payload here can be any valid structure representing the data as comig out of your system
             String Payload =
                    "[{" +
                        "{" +
                            "\"your_field_1\": \"field 1 value\"," +
                            "\"your_field_2\": \"field 2 value\"" +
                        "}" +
                    "}]";

            // gZip the Payload
            byte[] bPayload = Payload.getBytes(java.nio.charset.StandardCharsets.UTF_8);
            byte[] gZipPayload = Compress(bPayload);

            // Calculate Dispatch Signature
            byte[] bSecretKey = ConvertHexStringToByteArray(SecretKey);
            String XDispatchSignature = GetSignatureHash(bSecretKey, gZipPayload);

            URL url = new URL("https://connect-sbx.dispatch.me/agent/in");    // the production API is https://connect.dispatch.me
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json");
            con.setRequestProperty("RecordType", "job");               // The would be `organization`, `user` etc. (any identifying value is acceptable) depending on what you're trying to send over. Refer to the playbook
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
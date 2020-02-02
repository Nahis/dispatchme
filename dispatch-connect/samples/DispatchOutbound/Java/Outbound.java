import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;

public class DispatchOutbound {

    public static void main(String[] args) {
        try {
            String PublicKey = "your_public_id";
            String SecretKey = "your_secret_key";
            String maxMessages = "{\"maxNumberOfMessages\": 10}";

            int numRecs = 0;
            // Calculate Dispatch Signature
            byte[] bMaxMessages = maxMessages.getBytes(java.nio.charset.StandardCharsets.UTF_8);
            byte[] bSecretKey = ConvertHexStringToByteArray(SecretKey);

            HttpURLConnection AgentOutEndPoint = (HttpURLConnection) new URL("https://connect-sbx.dispatch.me/agent/out").openConnection();  // the production API is https://connect.dispatch.me
            AgentOutEndPoint.setRequestMethod("POST");
            AgentOutEndPoint.setRequestProperty("Content-Type", "application/json");
            AgentOutEndPoint.setRequestProperty("X-Dispatch-Key", PublicKey);
            AgentOutEndPoint.setDoOutput(true);
            DataOutputStream AgentOutStream;
            do {
                String OutSignature = GetSignatureHash(bSecretKey, bMaxMessages);
                AgentOutEndPoint.setRequestProperty("X-Dispatch-Signature", OutSignature);
                AgentOutStream = new DataOutputStream(AgentOutEndPoint.getOutputStream());
                AgentOutStream.write(bMaxMessages);

                BufferedReader reader = new BufferedReader(new InputStreamReader(AgentOutEndPoint.getInputStream()));
                StringBuilder stringBuilder = new StringBuilder();
                String line = null;
                while ((line = reader.readLine()) != null)
                {
                    stringBuilder.append(line + "\n");
                }
                String AgentOutString = stringBuilder.toString();
                ObjectMapper objectMapper = new ObjectMapper();

                AgentOutJson[] AgentOut = objectMapper.readValue(AgentOutString, AgentOutJson[].class);
                MessageJson m;
                numRecs = AgentOut.length;
                for (AgentOutJson rec : AgentOut) {
                    m = rec.Message;
                    String ret = "Success";
                    String err = "";
                    try
                    {
                        JobJson payload = m.Request.Payload.Actions.get(0).Put.job;
                        ////////////////////////////////////////////////////////////
                        // Download the payload for subsequent processing to your system
                        ////////////////////////////////////////////////////////////
                    }
                    catch (Exception e)
                    {
                        ret = "error";
                        err = e.getMessage();
                    }
                    finally
                    {
                        String receipt = String.format("%s\"Receipt\":\"%s\",\"ProcedureID\":\"%s\",\"Result\":\"%s\",\"Error\":\"%s\"%s", "{", m.Receipt, m.Request.ProcedureID, ret, err, "}");
                        byte[] bReceipt = receipt.getBytes(java.nio.charset.StandardCharsets.UTF_8);
                        String AckSignature = GetSignatureHash(bSecretKey, bReceipt);

                        HttpURLConnection AgentAckEndPoint = (HttpURLConnection) new URL("https://connect-sbx.dispatch.me/agent/ack").openConnection();
                        AgentAckEndPoint.setRequestMethod("POST");
                        AgentAckEndPoint.setRequestProperty("Content-Type", "application/json");
                        AgentAckEndPoint.setRequestProperty("X-Dispatch-Key", PublicKey);
                        AgentAckEndPoint.setRequestProperty("X-Dispatch-Signature", AckSignature);
                        AgentAckEndPoint.setDoOutput(true);

                        DataOutputStream AgentAckStream = new DataOutputStream(AgentAckEndPoint.getOutputStream());
                        AgentAckStream.write(bReceipt);
                        // System.out.println(AgentAckEndPoint.getResponseMessage());
                    }
                }
            } while (numRecs >= 10);
            AgentOutStream.flush();
            AgentOutStream.close();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
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

@JsonIgnoreProperties(ignoreUnknown = true)
class AgentOutJson
{
    public MessageJson Message;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class MessageJson
{
    public RequestJson Request;
    public String ID;
    public String Receipt;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class RequestJson
{
    public RequestJson() {}
    public String ProcedureID;
    public String Type;
    public PayloadJson Payload;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class PayloadJson
{
    public List<ActionsJson> Actions;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class ActionsJson
{
    public String ID;
    public PutJson Put;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class PutJson
{
    public JobJson job;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class JobJson
{
    public int id;
    public String title;
    public String created_at;
    public String updated_at;
    public AddressJson address;
    public CustomerJson customer;
    public List<EquipmentJson> equipment_descriptions;
    public List<String> external_ids;
    public String service_type;
    public float service_fee;
    public String symptom;
    public String timezone;
    public CustomFieldsJson custom_fields;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class AddressJson
{
    public String street_1;
    public String street_2;
    public String postal_code;
    public String city;
    public String state;
    public String country;
    public double latitude;
    public double longitude;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class CustomerJson
{
    public String first_name;
    public String last_name;
    public String email;
    public String city;
    public String phone_number;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class EquipmentJson
{
    public String equipment_type;
    public String installation_date;
    public String manufacturer;
    public String model_number;
    public String serial_number;
}

@JsonIgnoreProperties(ignoreUnknown = true)
class CustomFieldsJson
{
    public String custom_field_1;
    public String custom_field_2;
}

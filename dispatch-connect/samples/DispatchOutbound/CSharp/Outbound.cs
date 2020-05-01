using System;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;

namespace DispatchConnect
{
    class Program
    {

        public class AgentOutJson
        {
            public MessageJson Message { get; set; }
        }

        public class MessageJson
        {
            public RequestJson Request { get; set; }
            public String ID { get; set; }
            public String Receipt { get; set; }
        }

        public class RequestJson
        {
            public String ProcedureID { get; set; }
            public String Type { get; set; }
            public PayloadJson Payload { get; set; }
        }

        public class PayloadJson
        {
            public ActionsJson[] Actions { get; set; }
        }

        public class ActionsJson
        {
            public String ID { get; set; }
            public PutJson Put { get; set; }
        }

        public class PutJson
        {
            public JobJson Job { get; set; }
        }

        public class JobJson
        {
            public int id { get; set; }
            public String title { get; set; }
            public String created_at { get; set; }
            public String updated_at { get; set; }
            public AddressJson address { get; set; }
            public CustomerJson customer { get; set; }
            public EquipmentJson[] equipment_descriptions { get; set; }
            public String[] external_ids { get; set; }
            public String service_type { get; set; }
            public float service_fee { get; set; }
            public float service_fee_pre_collected { get; set; }
            public String symptom { get; set; }
            public String timezone { get; set; }
            public CustomFieldsJson custom_fields { get; set; }

        }

        public class AddressJson
        {
            public String street_1 { get; set; }
            public String street_2 { get; set; }
            public String postal_code { get; set; }
            public String city { get; set; }
            public String state { get; set; }
            public String country { get; set; }
            public double latitude { get; set; }
            public double longitude { get; set; }
        }

        public class CustomerJson
        {
            public String first_name { get; set; }
            public String last_name { get; set; }
            public String email { get; set; }
            public String city { get; set; }
            public String phone_number { get; set; }
        }

        public class EquipmentJson
        {
            public String equipment_type { get; set; }
            public String installation_date { get; set; }
            public String manufacturer { get; set; }
            public String model_number { get; set; }
            public String serial_number { get; set; }
        }

        public class CustomFieldsJson
        {
            public String custom_field_1 { get; set; }
            public String custom_field_2 { get; set; }
        }

        const string PublicKey = "your_public_key";
        const string SecretKey = "your_secret";
        const string maxMessages = "{\"maxNumberOfMessages\": 10}";
        static void Main(string[] args)
        {
            int numRecs = 0;
            byte[] bMaxMessages = Encoding.UTF8.GetBytes(maxMessages);
            byte[] mysecretyKey = ConvertHexStringToByteArray(SecretKey);
            HttpWebRequest AgentOutEndPoint = (HttpWebRequest)HttpWebRequest.Create("https://connect-sbx.dispatch.me/agent/out");   // the production API is https://connect.dispatch.me
            AgentOutEndPoint.Method = "POST";
            AgentOutEndPoint.Headers.Add("X-Dispatch-Key", PublicKey);
            AgentOutEndPoint.ContentType = "application/json";
            do
            {
                string OutSignature = GetSignatureHash(mysecretyKey, bMaxMessages);
                AgentOutEndPoint.Headers.Add("X-Dispatch-Signature", OutSignature);
                Stream outStream = AgentOutEndPoint.GetRequestStream();
                outStream.Write(bMaxMessages, 0, bMaxMessages.Length);
                HttpWebResponse ResponseAgentOut = (HttpWebResponse)AgentOutEndPoint.GetResponse();
                Stream receiveOutStream = ResponseAgentOut.GetResponseStream();
                StreamReader readOutStream = new StreamReader(receiveOutStream, Encoding.UTF8);

                String json = readOutStream.ReadToEnd();
                AgentOutJson[] agentOut = JsonConvert.DeserializeObject<AgentOutJson[]>(json);
                MessageJson m;
                numRecs = agentOut.Length;
                foreach (AgentOutJson rec in agentOut)
                {
                    m = rec.Message;
                    String ret = "Success";
                    JobJson payload = m.Request.Payload.Actions[0].Put.Job;
                    ////////////////////////////////////////////////////////////
                    // Download the payload for subsequent processing to your system
                    ////////////////////////////////////////////////////////////
                    String receipt = string.Format("{0}\"Receipt\":\"{1}\",\"ProcedureID\":\"{2}\",\"Result\":\"{3}\"{5}", "{", m.Receipt, m.Request.ProcedureID, ret, "}");
                    byte[] bReceipt = Encoding.UTF8.GetBytes(receipt);
                    String AckSignature = GetSignatureHash(mysecretyKey, bReceipt);
                    HttpWebRequest AgentAckEndPoint = (HttpWebRequest)HttpWebRequest.Create("https://connect-sbx.dispatch.me/agent/ack");
                    AgentAckEndPoint.Method = "POST";
                    AgentAckEndPoint.Headers.Add("X-Dispatch-Signature", AckSignature);
                    AgentAckEndPoint.Headers.Add("X-Dispatch-Key", PublicKey);
                    AgentAckEndPoint.ContentType = "application/json";
                    Stream ackStream = AgentAckEndPoint.GetRequestStream();
                    ackStream.Write(bReceipt, 0, bReceipt.Length);
                    HttpWebResponse ResponseAgentAck = (HttpWebResponse)AgentAckEndPoint.GetResponse();
                    Stream receiveAckStream = ResponseAgentAck.GetResponseStream();
                    StreamReader readAckstream = new StreamReader(receiveAckStream, Encoding.UTF8);
                }
            } while (numRecs >= 10);
        }

        public static byte[] Compress(byte[] raw)
        {
            using (MemoryStream memory = new MemoryStream())
            {
                using (GZipStream gzip = new GZipStream(memory, CompressionMode.Compress, true))
                {
                    gzip.Write(raw, 0, raw.Length);
                }
                return memory.ToArray();
            }
        }
        public static byte[] ConvertHexStringToByteArray(string hexString)
        {
            byte[] HexAsBytes = new byte[hexString.Length / 2];
            for (int index = 0; index < HexAsBytes.Length; index++)
            {
                string byteValue = hexString.Substring(index * 2, 2);
                HexAsBytes[index] = byte.Parse(byteValue, NumberStyles.HexNumber, CultureInfo.InvariantCulture);
            }
            return HexAsBytes;
        }

        public static String GetSignatureHash(byte[] key, byte[] message)
        {
            HMACSHA256 hmac = new HMACSHA256(key);
            byte[] hash = hmac.ComputeHash(message);
            StringBuilder hashString = new StringBuilder();
            foreach (byte x in hash)
            {
                hashString.AppendFormat("{0:x2}", x);
            }
            return hashString.ToString();
        }
    }
}

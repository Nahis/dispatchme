using System;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net;
using System.Security.Cryptography;
using System.Text;

namespace DispatchConnect
{
    class Program
    {
        const string PublicKey = "your_public_key";
        const string SecretKey = "your_secret";
        static void Main(string[] args)
        {
            string payload = @"[" +
                    "{" +
                        "\"header\":{" +
                            "\"record_type\": \"job\"," +  // The `record_type` would be `organization`, `user` depending on what you're trying to send over. Refer to the playbook
                            "\"version\": \"v3\"" +
                        "}," +
                        "\"record\":{" +
                            "\"external_organization_id\": \"dispatchme\"," +    // This would reference the ID unique in your system
                            "\"title\": \"some title\"," +
                            "\"status\": \"offered\"," +
                            "\"description\": \"some description\"," +
                            "\"external_id\": \"your_external_id\"," +        // This would reference the ID unique in your system
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
                                "\"external_id\": \"11_22_01\"," +
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
                    "}" +
                "]";
            byte[] bPayload = Encoding.UTF8.GetBytes(payload);
            byte[] gZipPayload = Compress(bPayload);
            byte[] bSecretyKey = ConvertHexStringToByteArray(SecretKey);
            string XDispatchSignature = GetSignatureHash(bSecretyKey, gZipPayload);
            HttpWebRequest WR = (HttpWebRequest)HttpWebRequest.Create("https://connect-sbx.dispatch.me/agent/in");   // the production API is https://connect.dispatch.me
            WR.Method = "POST";
            WR.Headers.Add("X-Dispatch-Signature", XDispatchSignature);
            WR.Headers.Add("X-Dispatch-Key", PublicKey);
            WR.Headers.Add("MessageId", "unique_id_for_transaction");  // optional
            WR.ContentType = "application/json";
            Stream stream = WR.GetRequestStream();
            stream.Write(gZipPayload, 0, gZipPayload.Length);
            HttpWebResponse Response = (HttpWebResponse)WR.GetResponse();
            Stream receiveStream = Response.GetResponseStream();
            StreamReader readstream = new StreamReader(receiveStream, Encoding.UTF8);
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

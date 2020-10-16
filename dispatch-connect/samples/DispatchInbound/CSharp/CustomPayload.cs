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
            // The payload here can be any valid structure representing the data as comig out of your system
            string payload = @"[" +
                    "{" +
                        "\"your_field_1\": \"field 1 value\"," +
                        "\"your_field_2\": \"field 2 value\"" +
                    "}" +
                "]";
            byte[] bPayload = Encoding.UTF8.GetBytes(payload);
            byte[] gZipPayload = Compress(bPayload);
            byte[] bSecretyKey = ConvertHexStringToByteArray(SecretKey);
            string XDispatchSignature = GetSignatureHash(bSecretyKey, gZipPayload);
            HttpWebRequest WR = (HttpWebRequest)HttpWebRequest.Create("https://connect-sbx.dispatch.me/agent/in");   // the production API is https://connect.dispatch.me
            WR.Method = "POST";
            WR.Headers.Add("X-Dispatch-Signature", XDispatchSignature);
            WR.Headers.Add("RecordType", "job");             // The would be `organization`, `user` etc. (any identify value is acceptable) depending on what you're trying to send over. Refer to the playbook
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

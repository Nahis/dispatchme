<?php

$key = 'your_public_key';
$secret = 'your_secret_key';
// The payload here can be any valid structure representing the data as comig out of your system
$payloadData = '[{"your_field_1": "field 1 value","your_field_2": "field 2 value"}]';
$compressed = gzencode(utf8_encode(json_encode($payloadData)));
$secret = hex2bin($secret);
$sign = hash_hmac('sha256', $compressed, $secret, true);
$sign = utf8_decode(bin2hex($sign));
$curl = curl_init();
curl_setopt_array($curl, array(
    CURLOPT_URL => "https://connect-sbx.dispatch.me/agent/in",
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING => "",
    CURLOPT_MAXREDIRS => 10,
    CURLOPT_TIMEOUT => 0,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => "POST",
    CURLOPT_POSTFIELDS => $compressed,
    CURLOPT_HTTPHEADER => array(
        "Content-Type: application/json",
        "X-Dispatch-Key: $key",
        "X-Dispatch-Signature: $sign",
        "MessageId: unique_id_for_transaction",  // optional
        "RecordType: job"  // The would be `organization`, `user` etc. (any identifying value is acceptable) depending on what you're trying to send over. Refer to the playbook
    ),
));
$response = curl_exec($curl);
curl_close($curl);

echo $response;

?>

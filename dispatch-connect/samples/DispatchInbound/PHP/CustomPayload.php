<?php

$key = 'your_public_key';
$secret = 'your_secret_key';
// The payload here can be any valid structure representing the data as comig out of your system
$payloadData = '[{"your_field_1": "field 1 value","your_field_2": "field 2 value"}]';
$compressed = gzencode(utf8_encode(json_encode($payloadData)));
$secret = hex2bin($secret);
$sign = hash_hmac('sha256', $compressed, $secret, true);
$sign = utf8_decode(bin2hex($sign));
$opts = [
    "http" => [
        "method" => "POST",
        "header" => "Content-Type: application/json\r\n" .
            "X-Dispatch-Key: $key\r\n" .
            "X-Dispatch-Signature: $sign\r\n" .
            "MessageId: unique_id_for_transaction\r\n" .  // optional but must be unique value for each transaction if passed
            "RecordType: job\r\n", // The would be `organization`, `user` etc. (any identifying value is acceptable) depending on what you're trying to send over. Refer to the playbook
        'content' => $compressed
    ]
];

$context = stream_context_create($opts);
$result = file_get_contents('https://connect-sbx.dispatch.me/agent/in', false, $context);
echo $result


?>
<?php

$key = 'your_key';
$secret = 'your_secret';

$maxMessages = 10;
$outPayload = utf8_encode('{"maxNumberOfMessages": '.$maxMessages.'}');
$secret = hex2bin($secret);
$outSign = hash_hmac('sha256', $outPayload, $secret, true);
$outSign = utf8_decode(bin2hex($outSign));
$outCurl = curl_init();
curl_setopt_array($outCurl, array(
    CURLOPT_URL => "https://connect-sbx.dispatch.me/agent/out",
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING => "",
    CURLOPT_MAXREDIRS => 10,
    CURLOPT_TIMEOUT => 0,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => "POST",
    CURLOPT_POSTFIELDS => $outPayload,
    CURLOPT_HTTPHEADER => array(
        "Content-Type: application/json",
        "X-Dispatch-Key: $key",
        "X-Dispatch-Signature: $outSign"
    ),
));
$outResponse = curl_exec($outCurl);
$outResults = json_decode($outResponse,true);
while (!empty($outResults)) {
       foreach($outResults as $outResult) {
              $m = $outResult['Message'];
              $reqType = $m['Request']['Type'];
              $payload = $m['Request']['Payload'];
              $receipt = $m['Receipt'];
              $procID = $m['Request']['ProcedureID'];
              
              ##########################################################
              # Download the payload for subsequent processing to your system. 
              # VERY IMPORTANT: This operation should take a few millisecs for each record - if it will take more please reach out to your Dispatch contact
              ##########################################################
              
              # After processing the message post acknowledgement
              $ackPayload = utf8_encode('{"Receipt":"'.$receipt.'","ProcedureID":"'.$procID.'","Result":"success"}');
              $ackSign = hash_hmac('sha256', $ackPayload, $secret, true);
              $ackSign = utf8_decode(bin2hex($ackSign));

              $ackCurl = curl_init();
              curl_setopt_array($ackCurl, array(
                  CURLOPT_URL => "https://connect-sbx.dispatch.me/agent/ack",
                  CURLOPT_RETURNTRANSFER => true,
                  CURLOPT_ENCODING => "",
                  CURLOPT_MAXREDIRS => 10,
                  CURLOPT_TIMEOUT => 0,
                  CURLOPT_FOLLOWLOCATION => true,
                  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
                  CURLOPT_CUSTOMREQUEST => "POST",
                  CURLOPT_POSTFIELDS => $ackPayload,
                  CURLOPT_HTTPHEADER => array(
                      "Content-Type: application/json",
                      "X-Dispatch-Key: $key",
                      "X-Dispatch-Signature: $ackSign"
                  ),
              ));              
              $ackResponse = curl_exec($ackCurl);
              echo($ackResponse);
              curl_close($ackCurl);
       }
       $outResponse = curl_exec($outCurl);
       echo($outResponse);
       $outResults = json_decode($outResponse,true);
}
curl_close($outCurl);
?>

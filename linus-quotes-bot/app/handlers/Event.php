<?php
namespace handlers;

class Event {
    /**
     * @var \React\Http\Request $request
     * @var \React\Http\Response $response
     */
    public static function dispatch($request, $response, $data = []) {
        $requestBody = '';
        $headers = $request->getHeaders();
        $contentLength = (int)$headers['Content-Length'];
        $receivedData = 0;
        $request->on('data', function($requestData) use ($request, $response, &$requestBody, &$receivedData, $contentLength, $data) {
            $requestBody .= $requestData;
            $receivedData += strlen($requestData);
            if ($receivedData >= $contentLength) {
                $requestData = json_decode($requestData, true);
                if (isset($requestData['text'])) {
                    $keyFound = false;
                    $keys = ['linus', 'torvalds', 'линус', 'торвальдс', 'linux', 'линукc'];
                    foreach ($keys as $key) {
                        if (false !== strstr(mb_strtolower($requestData['text']), $key)) {
                            $keyFound = true;
                            break;
                        }
                    }

                    if ($keyFound) {
                        $quoteIndex = mt_rand(0, count($data) - 1);
                        $response->writeHead(201, ['Content-Type' => 'application/json']);
                        $response->end('{"text": "'.trim($data[$quoteIndex]).' -- Линус Торвальдс", "bot": "linus-quotes-bot"}');
                        return;
                    }
                }

                $response->writeHead(417, ['Content-Type' => 'application/json']);
                $response->end('');
            }
        });
    }
}
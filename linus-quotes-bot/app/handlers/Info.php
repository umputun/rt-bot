<?php
namespace handlers;

class Info {
    /**
     * @var \React\Http\Request $request
     * @var \React\Http\Response $response
     */
    public static function dispatch($request, $response, $data = []) {
        $response->writeHead(200, ['Content-Type' => 'application/json']);
        $response->end('{"author": "Vladimir", "info": "Цитаты Линуса Торвальдса", "commands": []}');
    }
}
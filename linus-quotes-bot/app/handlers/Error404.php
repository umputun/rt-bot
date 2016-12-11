<?php
namespace handlers;

class Error404 {
    /**
     * @var \React\Http\Request $request
     * @var \React\Http\Response $response
     */
    public static function dispatch($request, $response, $data = []) {
        $response->writeHead(404, ['Content-Type' => 'application/json']);
        $response->end('');
    }
}
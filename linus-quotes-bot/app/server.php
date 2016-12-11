<?php
$loader = require_once 'vendor/autoload.php';

$loader->addPsr4('components\\', __DIR__.'/components/');
$loader->addPsr4('handlers\\', __DIR__.'/handlers/');

$data = explode("\n", file_get_contents(__DIR__.'/data/quotes.txt'));

/**
 * @var React\Http\Request $request
 * @var React\Http\Response $response
 */
$app = function ($request, $response) use ($data) {

    $router = new components\Router([
        'post' => [
            'event' => 'Event::dispatch',
        ],
        'get' => [
            'info' => 'Info::dispatch',
        ]
    ]);
    $result = $router->route($request, $response, $data);
};

$loop = React\EventLoop\Factory::create();
$socket = new React\Socket\Server($loop);
$http = new React\Http\Server($socket);

$http->on('request', $app);

$socket->listen(8080, '0.0.0.0');
$loop->run();
<?php

namespace components;

class Router {
    private $routes = [];

    public function __construct($routes) {
        $this->routes = $routes;
    }

    /**
     * @var \React\Http\Request $request
     * @var \React\Http\Response $response
     */
    public function route($request, $response, $data) {
        $method = strtolower($request->getMethod());
        $path = explode('/', strtolower($request->getPath()));

        if (count($path) < 2 || empty(trim($path[1])) || !isset($this->routes[$method][$path[1]])) {
            return call_user_func('handlers\Error404::dispatch', $request, $response, $data);
        }
        else {
            return call_user_func('handlers\\'.$this->routes[$method][$path[1]], $request, $response, $data);
        }
    }
}
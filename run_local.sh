#!/bin/bash

# Запускает проект локально на https://localhost

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export SSL_KEY=nginx.key
export SSL_CERT=nginx.crt

(
    cd "$DIR"
    SSL_KEYS_DIR="etc/ssl"

    if [ ! -f "$SSL_KEYS_DIR/$SSL_KEY" ] ||  [ ! -f "$SSL_KEYS_DIR/$SSL_CERT" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -subj "/C=US/ST=Test/L=Test/O=Dis/CN=localhost" \
            -keyout "$SSL_KEYS_DIR/$SSL_KEY" \
            -out "$SSL_KEYS_DIR/$SSL_CERT"
    fi

    docker-compose up
)

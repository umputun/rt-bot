FROM php:7.0-alpine

COPY timezone.ini /usr/local/etc/php/conf.d/timezone.ini
COPY app /root/app

EXPOSE 8080
WORKDIR /root/app/

CMD ["php", "server.php"]

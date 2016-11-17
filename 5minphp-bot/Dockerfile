FROM php:7.0-alpine

RUN mkdir /bot

COPY src/index.php /bot/
COPY src/rollbar.php /bot/

RUN chmod 777 /bot

WORKDIR /bot/

EXPOSE 8080

CMD ["php", "-S", "0.0.0.0:8080"]

# bots

Бот, который возвращает список остальных ботов.

Пример сообщения на которое бот отвечает:

    $ curl \
        -v \
        -X POST \
        -d '{"text":"list","username":"123","display_name":"login"}' \
        http://docker:8080/event

Бот отвечает статусом 201 и в ответе json:

    {"bot":"bots","text":"hello, memberberries, wiki-bot, search-bot, noter-bot, repl-bot, stat-bot, gif-bot"}

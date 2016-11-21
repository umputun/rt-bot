#Giphy

Находит гифку (на самом деле - не гифку, а `.webp`) с помощью сервиса [Giphy](http://giphy.com/) и вставляет её в чат.

Использует [Translate Endpoint](https://github.com/Giphy/GiphyAPI#translate-endpoint) из их API.

Использует `fixed_height_small` версию картинки, чтобы не засорять чат.

Отзывается на любое сообщение вида `giphy <запрос>` (case-insensitive).

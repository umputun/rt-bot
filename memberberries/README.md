# Member Berries
Радио-Т бот-вспоминашка по мотивам 20 сезона сериала Южный Парк.

## Запрос
```
$ curl -H "Content-type: application/json" -X POST http://localhost:8080/event -d \
'{
    "text" : "Помните Оляпку?",
    "id": 1024,
    "display_name": "User Name"
}'
```

## Ответ
```
{
  "text": "Я помню...",
  "bot": "MemberBerries"
}
```
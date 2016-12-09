#Бот для чата [Радио-Т](https://chat.radio-t.com) 

##Описание
Если в чате была упомянута какая то валюта например (110$) то бот напишет сколько это в доларах, евро, рублях и гривнях.

Курсы валют берутся с бесплатного [сервиса](http://free.currencyconverterapi.com), у них ограничение 100 запросов/час. 
И не особо быстрый ответ (1-2с). Если кто-то знает лучший безплатный сервис то пожалуйста напишите.

## Пример
Сообщение:
```json
{
  text: "а на digital ocean такой сервер стоит 5 евро",
  username: "test",
  display_name: "test"
}
```

Ответ:
```json
{
  bot: "money_bot",
  text: "5.30 $ (доларов)
         5.00 € (евро)
         136.67 ₴ (гривень)
         335.51 ₽ (рублей)
        "
}
```
# coding: utf-8

import json
import re
import random
from flask import Flask, request, Response

# Вариатны ответа на - что лучше?
start_better_phrases = [
  "",
  "Понятное дело ",
  "Думаю ",
  "Странный вопрос, конечно ",
  "А ты как думаешь, конечно ",
  "Я слышал что ",
  "Гугл говорит что ",
  "Уверен, ",
  "Мне говорили что ",
  "Моя мама говорит ",
  "Несомненно ",
  "Во всем мире считают что ",
  "Бобук говорил ",
  "Билл Мюррей же говорил что ",
  "Спроси у Бобука, он тебе скажет что ",
  "Спроси что полегче, наверное ",
  "У меня на работе считают что ",
  "Каждый выберает свое, но я думаю ",
  "Тим Кук утверждает что ",
  "Все знают что ",
  "Все уже давно знают ",
  "Сложный вопрос, думаю ",
  "Без понятия, но все твердят что "
]
end_better_phrases = [
  "",
  " получше будет",
  " выигрывает во всем",
  " в сто крат лучше",
  " лучше",
  " это тема",
  " всех уделает",
  " лучше, не это не точно",
  " койфовей, но надо проверить",
  " лучше, но есть ли смысл?",
  " круче, но лучше самому проверить",
  ", но не факт",
  ", хотя надо подумать..",
  ", а сколько стоит?",
  ", так что даже не думай",
  ", бери не пожалеешь",
  " у Умпутуна спроси",
  ", следующий вопрос..",
]


def better_handler(text):

  text = text[11:].strip()

  if text[-1] == "?":
    text = text[:-1]

  variation = text.split(' или ')
  r = random.randint(0, len(variation) - 1)

  choice = variation[r].strip()

  start_phrases_choice = start_better_phrases[random.randint(0, len(start_better_phrases) - 1)]
  end_phrases_choice = end_better_phrases[random.randint(0, len(end_better_phrases) - 1)]

  return start_phrases_choice + choice + end_phrases_choice
  

def event():
  try:
    data = json.loads(request.data.decode('utf-8'))
  except ValueError:
    return silence()

  message = data.get('text')
  message = message.strip()

  if (re.match(r"что лучше, ", message) or re.match(r"кто лучше, ", message)) and re.search(r" или ", message):
    return Response(
      response=json.dumps({'text': better_handler(message), 'bot': 'or-bot'}),
      status=201,
      mimetype="application/json"
    )
  else:
    return silence()


def info():
  return Response(
    response=json.dumps({
      'author': "Sergey Lamantin",
      "info": "Бот or-bot поможет сделать трудный выбор"
    }),
    status=200,
    mimetype="application/json",
  )


def silence():
  return Response(
    response=json.dumps({'error': True, 'status': 417}),
    status=417,
    mimetype="application/json"
  )


app = Flask('or-bot')

app.add_url_rule('/event', 'event', event, methods=['POST'])
app.add_url_rule('/info', 'info', info, methods=['GET'])

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)

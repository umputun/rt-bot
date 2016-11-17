import os


BOT_NAME = 'karma-bot'
BOT_DESCRIPTION = 'Бот позволяет изменять карму пользователей чата'
AUTHOR = 'Sergey Levitin <selevit@gmail.com>'

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

LISTEN_HOST = os.environ.get('LISTEN_HOST', '0.0.0.0')
LISTEN_PORT = int(os.environ.get('LISTEN_PORT', 8080))

DEBUG = bool(os.environ.get('DEBUG', False))

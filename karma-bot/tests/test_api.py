import json
import unittest
from unittest.mock import patch

from mockredis import mock_strict_redis_client

import rt_karma_bot
import settings
from karma import KarmaApp


class KarmaBotAPITestCase(unittest.TestCase):

    def setUp(self):
        rt_karma_bot.app.config['TESTING'] = True
        self.app = rt_karma_bot.app.test_client()

    def test_bot_info(self):
        response = self.app.get('/info')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(
            data,
            {
                "author": settings.AUTHOR,
                "info": settings.BOT_DESCRIPTION,
                "commands": [
                    'username++ (увеличить карму пользователя)',
                    'username-- (уменьшить карму пользователя)',
                    '/karma username (узнать карму пользователя)',
                    '/karma (узнать свою карму)',
                    '/karma-top 100 (показать топ 100 пользователей)',
                    '/karma-top (показать топ 10 пользователей)',
                ],
            }
        )

    def test_invalid_msg_format(self):
        response = self.app.get('/event')
        self.assertEqual(response.status_code, 405)
        response = self.app.post('/event', data=json.dumps({
            'invalid_key': '1',
        }))
        self.assertEqual(response.status_code, 417)
        response = self.app.post('/event', data='invalid json"')
        self.assertEqual(response.status_code, 417)
        response = self.app.post('/event', data='invalid json"')

    def test_expectation_failed(self):
        response = self.app.post('/event', data=json.dumps({
            'username': 'joe',
            'display_name': 'Test',
            'text': 'Hello!',
        }))
        self.assertEqual(response.status_code, 417)

    @patch('karma.redis.StrictRedis', mock_strict_redis_client)
    def test_incr_karma(self):
        g_mock_redis = mock_strict_redis_client()

        def _mock_karma_app_factory(*args, **kwargs):
            karma_app = KarmaApp(*args, **kwargs)
            karma_app.redis = g_mock_redis
            return karma_app

        with patch('rt_karma_bot.KarmaApp', _mock_karma_app_factory):
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe',
                'display_name': 'Test',
                'text': 'Alice++',
            }))
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(response_data['bot'], settings.BOT_NAME)
            self.assertEqual(
                response_data['text'],
                'Карма пользователя @Alice увеличена (текущее значение: 1).'
            )
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe2',
                'display_name': 'Test',
                'text': 'alice++',
            }))
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(
                response_data['text'],
                'Карма пользователя @alice увеличена (текущее значение: 2).'
            )
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe2',
                'display_name': 'Test',
                'text': 'Alice++',
            }))
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(
                response_data['text'],
                'Вы можете менять карму пользователю не чаще раза в сутки.',
            )
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe',
                'display_name': 'Test',
                'text': 'joe++',
            }))
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(
                response_data['text'],
                'Вы не можете изменять свою карму!'
            )
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe2',
                'display_name': 'Test',
                'text': 'joe++',
            }))
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(
                response_data['text'],
                'Карма пользователя @joe увеличена (текущее значение: 1).'
            )

    @patch('karma.redis.StrictRedis', mock_strict_redis_client)
    def test_decr_karma(self):
        g_mock_redis = mock_strict_redis_client()

        def _mock_karma_app_factory(*args, **kwargs):
            karma_app = KarmaApp(*args, **kwargs)
            karma_app.redis = g_mock_redis
            return karma_app

        with patch('rt_karma_bot.KarmaApp', _mock_karma_app_factory):
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe',
                'display_name': 'Test',
                'text': 'Alice--',
            }))
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(response_data['bot'], settings.BOT_NAME)
            self.assertEqual(
                response_data['text'],
                'Карма пользователя @Alice уменьшена (текущее значение: -1).'
            )
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe2',
                'display_name': 'Test',
                'text': 'alice--',
            }))
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(
                response_data['text'],
                'Карма пользователя @alice уменьшена (текущее значение: -2).'
            )
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe2',
                'display_name': 'Test',
                'text': 'Alice--',
            }))
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(
                response_data['text'],
                'Вы можете менять карму пользователю не чаще раза в сутки.',
            )
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe',
                'display_name': 'Test',
                'text': 'joe--',
            }))
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(
                response_data['text'],
                'Вы не можете изменять свою карму!'
            )

    @patch('karma.redis.StrictRedis', mock_strict_redis_client)
    def test_stat_own_karma(self):
        g_mock_redis = mock_strict_redis_client()

        def _mock_karma_app_factory(*args, **kwargs):
            karma_app = KarmaApp(*args, **kwargs)
            karma_app.redis = g_mock_redis
            return karma_app

        with patch('rt_karma_bot.KarmaApp', _mock_karma_app_factory):
            self.app.post('/event', data=json.dumps({
                'username': 'joe',
                'display_name': 'Test',
                'text': 'Alice++',
            }))
            self.app.post('/event', data=json.dumps({
                'username': 'joe2',
                'display_name': 'Test',
                'text': 'alice++',
            }))
            response = self.app.post('/event', data=json.dumps({
                'username': 'Alice',
                'display_name': 'Test',
                'text': '/karma',
            }))
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(response_data['bot'], settings.BOT_NAME)
            self.assertEqual(
                response_data['text'],
                '@Alice, ваша карма: 2.',
            )

    @patch('karma.redis.StrictRedis', mock_strict_redis_client)
    def test_stat_other_user_karma(self):
        g_mock_redis = mock_strict_redis_client()

        def _mock_karma_app_factory(*args, **kwargs):
            karma_app = KarmaApp(*args, **kwargs)
            karma_app.redis = g_mock_redis
            return karma_app

        with patch('rt_karma_bot.KarmaApp', _mock_karma_app_factory):
            self.app.post('/event', data=json.dumps({
                'username': 'joe',
                'display_name': 'Test',
                'text': 'alice++',
            }))
            self.app.post('/event', data=json.dumps({
                'username': 'joe2',
                'display_name': 'Test',
                'text': '@Alice++',
            }))
            response = self.app.post('/event', data=json.dumps({
                'username': 'joe',
                'display_name': 'Test',
                'text': '/karma @Alice',
            }))
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(response_data['bot'], settings.BOT_NAME)
            self.assertEqual(
                response_data['text'],
                'Карма пользователя @Alice: 2.',
            )

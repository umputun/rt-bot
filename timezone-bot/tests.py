import unittest
from unittest import TestCase, mock

from flask import json

from .timezone_bot import app


class EventTestCase(TestCase):
    """Test case for POST /event"""

    def setUp(self):
        self.client = app.test_client()

        self.url = '/event'
        self.places = {
            'status': 'OK',
            'results': [
                {
                    'geometry': {
                        'location': 'Location'
                    },
                    'formatted_address': 'Krasnoyarsk'
                }
            ]
        }
        self.timezone = {
            'status': 'OK',
            'timeZoneId': 'Asia/Krasnoyarsk'
        }
        self.empty_data = json.dumps({})
        self.invalid_data = json.dumps({'text': 'Hello world'})
        self.valid_data = json.dumps({'text': 'время в красноярске'})

    def test_event_with_no_data_sent(self):
        """Ensure that 417 status code returns when no data sent"""
        resp = self.client.post(self.url)
        self.assertEquals(resp.status_code, 417)

    def test_event_with_empty_dict_sent(self):
        """Ensure that 417 status code returns when empty dict sent"""
        resp = self.client.post(self.url, data=self.empty_data)
        self.assertEquals(resp.status_code, 417)

    def test_some_random_message(self):
        """Ensure that bot will not say if shouldn't"""
        resp = self.client.post(self.url, data=self.invalid_data)
        self.assertEquals(resp.status_code, 417)

    @mock.patch('googlemaps.Client.places')
    def test_correct_message_for_bot(self, places):
        """Ensure that bot will try to answer if 'время в/во <cityname>'
        obtained from request data
        """
        resp = self.client.post(self.url, data=self.valid_data)
        self.assertEquals(resp.status_code, 201)
        places.assert_called_with('красноярске')
        dict_data = json.loads(resp.data)
        self.assertEquals(dict_data['text'], 'Не могу найти город по запросу '
                                             '"красноярске"')

    @mock.patch('googlemaps.Client.places')
    @mock.patch('googlemaps.Client.timezone')
    def test_problems_with_timezone(self, timezone, places):
        """Ensure that if timezone is not loaded correctly, bot answers that
        can't obtain and load timezone data
        """
        places.return_value = self.places
        resp = self.client.post(self.url, data=self.valid_data)
        timezone.assert_called_with('Location')
        self.assertEquals(resp.status_code, 201)
        dict_data = json.loads(resp.data)
        self.assertEquals(dict_data['text'], 'Не могу получить данные о '
                                             'часовом поясе')

    @mock.patch('googlemaps.Client.places')
    @mock.patch('googlemaps.Client.timezone')
    def test_timezone_obtained(self, timezone, places):
        """Ensure that if timezone correctly obtained, bot says time in this
        timezone
        """
        places.return_value = self.places
        timezone.return_value = self.timezone
        resp = self.client.post(self.url, data=self.valid_data)
        self.assertEquals(resp.status_code, 201)
        dict_data = json.loads(resp.data)
        self.assertIn('Местное время в Krasnoyarsk сейчас', dict_data['text'])


class InfoTestCase(TestCase):
    """Test case for GET /info endpoint"""

    def setUp(self):
        self.client = app.test_client()
        self.url = '/info'

    def test_info_obtaining(self):
        """Ensure that correct fields exists in response"""
        resp = self.client.get(self.url)
        self.assertEquals(resp.status_code, 200)
        dict_data = json.loads(resp.data)
        self.assertIn('author', dict_data)
        self.assertIn('info', dict_data)
        self.assertIn('commands', dict_data)


if __name__ == '__main__':
    unittest.main()

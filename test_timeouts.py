import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock dependencies
sys.modules['speech_recognition'] = MagicMock()
sys.modules['gtts'] = MagicMock()
sys.modules['playsound'] = MagicMock()
sys.modules['wikipedia'] = MagicMock()
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()

mock_requests = MagicMock()
# Mock exceptions for requests
class RequestException(Exception): pass
mock_requests.exceptions.RequestException = RequestException
sys.modules['requests'] = mock_requests

sys.modules['bs4'] = MagicMock()

mock_toga = MagicMock()
sys.modules['toga'] = mock_toga
sys.modules['toga.style'] = MagicMock()
sys.modules['toga.style.pack'] = MagicMock()
sys.modules['java'] = MagicMock()

# Avoid Toga App __init__ issues
mock_toga.App = MagicMock

import voice_assistant
from src.helpistos.app import Helpistos

class TestTimeouts(unittest.TestCase):
    def setUp(self):
        mock_requests.get.reset_mock()

    def test_voice_assistant_get_weather_timeout(self):
        with patch('voice_assistant.listen', return_value='Athens'):
            mock_response = MagicMock()
            # Return data for BOTH calls
            mock_response.json.side_effect = [
                {'results': [{'latitude': 0, 'longitude': 0, 'name': 'Athens'}]},
                {'current': {'temperature_2m': 20, 'weather_code': 0}}
            ]
            mock_requests.get.return_value = mock_response

            with patch('voice_assistant.speak'):
                voice_assistant.get_weather(MagicMock(), MagicMock())

                # Verify that requests.get was called with timeout=10
                self.assertEqual(mock_requests.get.call_count, 2)
                for call in mock_requests.get.call_args_list:
                    self.assertEqual(call.kwargs.get('timeout'), 10)

    def test_voice_assistant_get_news_timeout(self):
        mock_response = MagicMock()
        mock_response.text = '<rss><channel><item><title>Test News</title></item></channel></rss>'
        mock_requests.get.return_value = mock_response

        with patch('voice_assistant.speak'), patch('voice_assistant.BeautifulSoup'):
            voice_assistant.get_news()

            # Verify that requests.get was called with timeout=10
            found = False
            for call in mock_requests.get.call_args_list:
                if call.kwargs.get('timeout') == 10 and 'headers' in call.kwargs:
                    found = True
                    break
            self.assertTrue(found, "requests.get was not called with timeout=10 and headers in voice_assistant.get_news")

    def test_app_get_weather_logic_timeout(self):
        app = Helpistos()
        mock_response = MagicMock()
        mock_response.json.side_effect = [
            {'results': [{'latitude': 0, 'longitude': 0, 'name': 'Athens'}]},
            {'current': {'temperature_2m': 20}}
        ]
        mock_requests.get.return_value = mock_response

        with patch.object(app, 'speak'):
            app.get_weather_logic("καιρός")

            # Verify that requests.get was called with timeout=10
            self.assertEqual(mock_requests.get.call_count, 2)
            for call in mock_requests.get.call_args_list:
                self.assertEqual(call.kwargs.get('timeout'), 10)

    def test_app_get_news_logic_timeout(self):
        app = Helpistos()
        mock_response = MagicMock()
        mock_response.text = '<rss><channel><item><title>Test News</title></item></channel></rss>'
        mock_requests.get.return_value = mock_response

        with patch.object(app, 'speak'), patch('src.helpistos.app.BeautifulSoup'):
            app.get_news_logic()

            # Verify that requests.get was called with timeout=10
            mock_requests.get.assert_called_with(unittest.mock.ANY, timeout=10)

if __name__ == '__main__':
    unittest.main()

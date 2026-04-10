import unittest
from unittest.mock import MagicMock, patch
import requests

# Mock modules that might not be available or would cause side effects
import sys
sys.modules['gtts'] = MagicMock()
sys.modules['playsound'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

import voice_assistant

class TestVoiceAssistant(unittest.TestCase):

    @patch('voice_assistant.NEWS_SESSION')
    @patch('voice_assistant.speak')
    def test_get_news_success(self, mock_speak, mock_session):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<?xml version="1.0" encoding="UTF-8"?><rss><channel><item><title>News Headline 1</title></item><item><title>News Headline 2</title></item></channel></rss>'
        mock_session.get.return_value = mock_response

        # Call the function
        voice_assistant.get_news()

        # Verify NEWS_SESSION was used
        mock_session.get.assert_called_once_with("https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el")

        # Verify speak was called with the headlines
        mock_speak.assert_any_call("Οι δύο κυριότερες ειδήσεις είναι:")
        mock_speak.assert_any_call("News Headline 1")
        mock_speak.assert_any_call("News Headline 2")

    @patch('voice_assistant.NEWS_SESSION')
    @patch('voice_assistant.speak')
    def test_get_news_failure(self, mock_speak, mock_session):
        # Setup mock to raise exception
        mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")

        # Call the function
        voice_assistant.get_news()

        # Verify error message was spoken
        mock_speak.assert_called_with("Συγγνώμη, δεν μπορώ να συνδεθώ στην υπηρεσία ειδήσεων.")

if __name__ == '__main__':
    unittest.main()

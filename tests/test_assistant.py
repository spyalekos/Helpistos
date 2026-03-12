import unittest
from unittest.mock import patch, MagicMock
import sys

# Define dummy exception classes for mocking
class UnknownValueError(Exception): pass
class RequestError(Exception): pass

# Mock pynput and other UI/Audio related modules that might fail in headless environment
mock_sr = MagicMock()
mock_sr.UnknownValueError = UnknownValueError
mock_sr.RequestError = RequestError

sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()
sys.modules['playsound'] = MagicMock()
sys.modules['speech_recognition'] = mock_sr

import voice_assistant
import requests

class TestVoiceAssistant(unittest.TestCase):

    @patch('voice_assistant.playsound')
    @patch('voice_assistant.gTTS')
    @patch('os.remove')
    def test_speak_success(self, mock_remove, mock_gtts, mock_playsound):
        # Test successful speech production
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance

        voice_assistant.speak("Γεια")

        mock_gtts.assert_called_once_with(text="Γεια", lang="el")
        mock_tts_instance.save.assert_called_once()
        mock_playsound.assert_called_once()
        mock_remove.assert_called_once()

    @patch('voice_assistant.requests.get')
    @patch('voice_assistant.speak')
    def test_get_weather_success(self, mock_speak, mock_get):
        # Mocking geocoding and weather responses
        mock_geo_resp = MagicMock()
        mock_geo_resp.json.return_value = {
            "results": [{"name": "Αθήνα", "latitude": 37.98, "longitude": 23.72}]
        }
        mock_geo_resp.raise_for_status = MagicMock()

        mock_weather_resp = MagicMock()
        mock_weather_resp.json.return_value = {
            "current": {"temperature_2m": 25.5, "weather_code": 0}
        }
        mock_weather_resp.raise_for_status = MagicMock()

        mock_get.side_effect = [mock_geo_resp, mock_weather_resp]

        # We need to mock listen() to return "αθήνα"
        with patch('voice_assistant.listen', return_value="αθήνα"):
            voice_assistant.get_weather(MagicMock(), MagicMock())

        mock_speak.assert_any_call("Στην πόλη Αθήνα, η θερμοκρασία είναι 25.5 βαθμοί Κελσίου και ο καιρός είναι Καθαρός ουρανός.")

    @patch('voice_assistant.requests.get')
    @patch('voice_assistant.speak')
    def test_get_weather_city_not_found(self, mock_speak, mock_get):
        mock_geo_resp = MagicMock()
        mock_geo_resp.json.return_value = {"results": []}
        mock_get.return_value = mock_geo_resp

        with patch('voice_assistant.listen', return_value="αγνωστηπολη"):
            voice_assistant.get_weather(MagicMock(), MagicMock())

        mock_speak.assert_any_call("Δεν μπόρεσα να βρω την πόλη αγνωστηπολη.")

    @patch('voice_assistant.requests.get')
    @patch('voice_assistant.speak')
    def test_get_news_success(self, mock_speak, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = """
        <rss><channel>
            <item><title>Είδηση 1</title></item>
            <item><title>Είδηση 2</title></item>
        </channel></rss>
        """
        mock_get.return_value = mock_resp

        voice_assistant.get_news()

        mock_speak.assert_any_call("Οι δύο κυριότερες ειδήσεις είναι:")
        mock_speak.assert_any_call("Είδηση 1")
        mock_speak.assert_any_call("Είδηση 2")

    @patch('voice_assistant.requests.get')
    @patch('voice_assistant.speak')
    def test_get_news_network_failure(self, mock_speak, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        voice_assistant.get_news()

        mock_speak.assert_called_with("Συγγνώμη, δεν μπορώ να συνδεθώ στην υπηρεσία ειδήσεων.")

    @patch('voice_assistant.speak')
    @patch('datetime.datetime')
    def test_get_time_format(self, mock_datetime, mock_speak):
        # Set a fixed date/time: Monday, 1 January 2024, 10:30 AM
        mock_datetime.now.return_value.strftime.return_value = "Η ώρα είναι 10:30 AM και η ημερομηνία είναι Monday, 01 January 2024"

        voice_assistant.get_time()

        mock_speak.assert_called_with("Η ώρα είναι 10:30 AM και η ημερομηνία είναι Monday, 01 January 2024")

    def test_listen_timeout_or_empty(self):
        mock_recognizer = MagicMock()
        mock_microphone = MagicMock()

        # Test UnknownValueError (no speech detected)
        mock_recognizer.recognize_google.side_effect = UnknownValueError()

        result = voice_assistant.listen(mock_recognizer, mock_microphone)
        self.assertEqual(result, "")

    def test_listen_request_error(self):
        mock_recognizer = MagicMock()
        mock_microphone = MagicMock()

        # Test RequestError (API failure)
        mock_recognizer.recognize_google.side_effect = RequestError()

        with patch('voice_assistant.speak') as mock_speak:
            result = voice_assistant.listen(mock_recognizer, mock_microphone)
            self.assertEqual(result, "")
            mock_speak.assert_called_with("Συγγνώμη, η υπηρεσία ομιλίας δεν είναι διαθέσιμη.")

if __name__ == '__main__':
    unittest.main()

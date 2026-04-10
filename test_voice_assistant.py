import sys
from unittest.mock import MagicMock, patch

# Define real exception classes for mocking
class MockUnknownValueError(Exception): pass
class MockRequestError(Exception): pass
class MockRequestException(Exception): pass

# Mocking missing dependencies
sr_mock = MagicMock()
sr_mock.UnknownValueError = MockUnknownValueError
sr_mock.RequestError = MockRequestError
sys.modules["speech_recognition"] = sr_mock

sys.modules["gtts"] = MagicMock()
sys.modules["playsound"] = MagicMock()
sys.modules["wikipedia"] = MagicMock()

requests_mock = MagicMock()
requests_mock.exceptions.RequestException = MockRequestException
sys.modules["requests"] = requests_mock

sys.modules["bs4"] = MagicMock()
sys.modules["pyperclip"] = MagicMock()
sys.modules["pynput"] = MagicMock()
sys.modules["pynput.keyboard"] = MagicMock()

import unittest
import voice_assistant
import datetime

class TestVoiceAssistant(unittest.TestCase):

    @patch('voice_assistant.gTTS')
    @patch('voice_assistant.playsound')
    @patch('voice_assistant.os.remove')
    def test_speak(self, mock_remove, mock_playsound, mock_gTTS):
        text = "Γεια σας"
        voice_assistant.speak(text)

        mock_gTTS.assert_called_once_with(text=text, lang=voice_assistant.WIKI_LANG)
        mock_gTTS.return_value.save.assert_called_once_with("temp_speech.mp3")
        mock_playsound.assert_called_once_with("temp_speech.mp3", block=True)
        mock_remove.assert_called_once_with("temp_speech.mp3")

    @patch('voice_assistant.sr.Recognizer')
    @patch('voice_assistant.sr.Microphone')
    def test_listen_success(self, mock_microphone, mock_recognizer):
        mock_rec_inst = mock_recognizer.return_value
        mock_rec_inst.recognize_google.return_value = "Γεια"

        result = voice_assistant.listen()

        self.assertEqual(result, "γεια")
        mock_rec_inst.adjust_for_ambient_noise.assert_called_once()
        mock_rec_inst.listen.assert_called_once()

    @patch('voice_assistant.sr.Recognizer')
    @patch('voice_assistant.sr.Microphone')
    def test_listen_unknown_value(self, mock_microphone, mock_recognizer):
        mock_rec_inst = mock_recognizer.return_value
        mock_rec_inst.recognize_google.side_effect = MockUnknownValueError()

        result = voice_assistant.listen()

        self.assertEqual(result, "")

    @patch('voice_assistant.speak')
    @patch('voice_assistant.sr.Recognizer')
    @patch('voice_assistant.sr.Microphone')
    def test_listen_request_error(self, mock_microphone, mock_recognizer, mock_speak):
        mock_rec_inst = mock_recognizer.return_value
        mock_rec_inst.recognize_google.side_effect = MockRequestError()

        result = voice_assistant.listen()

        self.assertEqual(result, "")
        mock_speak.assert_called_once_with("Συγγνώμη, η υπηρεσία ομιλίας δεν είναι διαθέσιμη.")

    @patch('voice_assistant.speak')
    @patch('voice_assistant.datetime')
    def test_get_time(self, mock_datetime_module, mock_speak):
        fixed_now = datetime.datetime(2023, 10, 27, 10, 30)
        mock_datetime_module.datetime.now.return_value = fixed_now

        voice_assistant.get_time()

        self.assertTrue(mock_speak.called)
        args, _ = mock_speak.call_args
        # Since locale might not be set correctly in this environment,
        # let's just check if it contains parts we know for sure are there
        self.assertIn("10:30", args[0])

    @patch('voice_assistant.speak')
    @patch('voice_assistant.listen')
    @patch('voice_assistant.requests.get')
    def test_get_weather_success(self, mock_get, mock_listen, mock_speak):
        mock_listen.return_value = "αθήνα"

        # Mock geocoding response
        mock_geo_resp = MagicMock()
        mock_geo_resp.json.return_value = {
            "results": [{"name": "Αθήνα", "latitude": 37.98, "longitude": 23.72}]
        }

        # Mock weather response
        mock_weather_resp = MagicMock()
        mock_weather_resp.json.return_value = {
            "current": {"temperature_2m": 25.0, "weather_code": 0}
        }

        mock_get.side_effect = [mock_geo_resp, mock_weather_resp]

        voice_assistant.get_weather()

        mock_speak.assert_any_call("Για ποια πόλη θέλετε να μάθετε τον καιρό;")
        expected_weather_msg = "Στην πόλη Αθήνα, η θερμοκρασία είναι 25.0 βαθμοί Κελσίου και ο καιρός είναι Καθαρός ουρανός."
        mock_speak.assert_any_call(expected_weather_msg)

    @patch('voice_assistant.speak')
    @patch('voice_assistant.listen')
    @patch('voice_assistant.requests.get')
    def test_get_weather_city_not_found(self, mock_get, mock_listen, mock_speak):
        mock_listen.return_value = "άγνωστη πόλη"

        mock_geo_resp = MagicMock()
        mock_geo_resp.json.return_value = {"results": []}
        mock_get.return_value = mock_geo_resp

        voice_assistant.get_weather()

        mock_speak.assert_any_call("Δεν μπόρεσα να βρω την πόλη άγνωστη πόλη.")

    @patch('voice_assistant.speak')
    @patch('voice_assistant.listen')
    @patch('voice_assistant.requests.get')
    def test_get_weather_request_error(self, mock_get, mock_listen, mock_speak):
        mock_listen.return_value = "αθήνα"
        mock_get.side_effect = MockRequestException()

        voice_assistant.get_weather()

        mock_speak.assert_any_call("Συγγνώμη, δεν μπορώ να συνδεθώ στην υπηρεσία καιρού αυτή τη στιγμή.")

    @patch('voice_assistant.speak')
    @patch('voice_assistant.requests.get')
    def test_get_news_success(self, mock_get, mock_speak):
        mock_resp = MagicMock()
        mock_resp.text = """
        <rss><channel>
            <item><title>Είδηση 1</title></item>
            <item><title>Είδηση 2</title></item>
        </channel></rss>
        """
        mock_get.return_value = mock_resp

        # Mock BeautifulSoup because we mocked bs4 in sys.modules
        with patch('voice_assistant.BeautifulSoup') as mock_bs:
            mock_soup = mock_bs.return_value
            mock_item1 = MagicMock()
            mock_item1.title.text = "Είδηση 1"
            mock_item2 = MagicMock()
            mock_item2.title.text = "Είδηση 2"
            mock_soup.find_all.return_value = [mock_item1, mock_item2]

            voice_assistant.get_news()

            mock_speak.assert_any_call("Οι δύο κυριότερες ειδήσεις είναι:")
            mock_speak.assert_any_call("Είδηση 1")
            mock_speak.assert_any_call("Είδηση 2")

    @patch('voice_assistant.speak')
    @patch('voice_assistant.requests.get')
    def test_get_news_no_items(self, mock_get, mock_speak):
        mock_resp = MagicMock()
        mock_resp.text = "<rss><channel></channel></rss>"
        mock_get.return_value = mock_resp

        with patch('voice_assistant.BeautifulSoup') as mock_bs:
            mock_soup = mock_bs.return_value
            mock_soup.find_all.return_value = []

            voice_assistant.get_news()

            mock_speak.assert_called_with("Δεν βρέθηκαν άρθρα ειδήσεων στο feed.")

    @patch('voice_assistant.speak')
    @patch('voice_assistant.requests.get')
    def test_get_news_request_error(self, mock_get, mock_speak):
        mock_get.side_effect = MockRequestException()

        voice_assistant.get_news()

        mock_speak.assert_called_with("Συγγνώμη, δεν μπορώ να συνδεθώ στην υπηρεσία ειδήσεων.")

if __name__ == '__main__':
    unittest.main()

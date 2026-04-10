import unittest
from unittest.mock import MagicMock, patch
import subprocess
import os
import time

def speak_logic(text, add_log_func, os_name, temp_file="temp_speech.mp3"):
    add_log_func(f"Assistant: {text}")
    try:
        # Use system player fallback for Linux/Desktop
        if os_name == 'posix':
            # Try mpg123, ffplay, or other available players
            try:
                subprocess.run(["mpg123", "-q", temp_file], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file], check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
        elif os_name == 'nt':
            os.startfile(temp_file)

        time.sleep(0.1) # Reduced for testing
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except Exception as e:
        add_log_func(f"Speak Error: {e}")

class TestAudioPlayback(unittest.TestCase):
    def setUp(self):
        self.add_log = MagicMock()

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('time.sleep')
    def test_speak_mpg123_success(self, mock_sleep, mock_remove, mock_exists, mock_run):
        # Mock subprocess.run to succeed on the first call (mpg123)
        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True

        speak_logic("Hello", self.add_log, 'posix')

        # Check if mpg123 was called
        mock_run.assert_called_once_with(["mpg123", "-q", "temp_speech.mp3"], check=True)
        self.add_log.assert_any_call("Assistant: Hello")

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('time.sleep')
    def test_speak_mpg123_fails_ffplay_success(self, mock_sleep, mock_remove, mock_exists, mock_run):
        # Mock subprocess.run: first call fails, second succeeds
        mock_run.side_effect = [subprocess.CalledProcessError(1, 'mpg123'), MagicMock(returncode=0)]
        mock_exists.return_value = True

        speak_logic("Hello", self.add_log, 'posix')

        # Check if both were called
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(["mpg123", "-q", "temp_speech.mp3"], check=True)
        mock_run.assert_any_call(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "temp_speech.mp3"], check=True)

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('time.sleep')
    def test_speak_mpg123_not_found_ffplay_success(self, mock_sleep, mock_remove, mock_exists, mock_run):
        # Mock subprocess.run: first call raises FileNotFoundError, second succeeds
        mock_run.side_effect = [FileNotFoundError(), MagicMock(returncode=0)]
        mock_exists.return_value = True

        speak_logic("Hello", self.add_log, 'posix')

        # Check if both were called
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(["mpg123", "-q", "temp_speech.mp3"], check=True)
        mock_run.assert_any_call(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "temp_speech.mp3"], check=True)

if __name__ == '__main__':
    unittest.main()

import sys
from unittest.mock import MagicMock

# Mock dependencies before importing voice_assistant
sys.modules['speech_recognition'] = MagicMock()
sys.modules['gtts'] = MagicMock()
sys.modules['playsound'] = MagicMock()
sys.modules['wikipedia'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['bs4'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

import voice_assistant
import datetime
import locale
from unittest.mock import patch

def test_get_time():
    """Tests the get_time function to ensure it calls speak with the correct Greek string."""
    fixed_now = datetime.datetime(2023, 10, 27, 14, 30, 0)

    with patch('datetime.datetime') as mock_datetime, \
         patch('locale.setlocale') as mock_setlocale, \
         patch('voice_assistant.speak') as mock_speak:

        mock_datetime.now.return_value = fixed_now

        # We need to mock strftime on the returned object because datetime.datetime.now()
        # returns an instance, but we mocked the class.
        # Actually, let's mock the instance's strftime.
        mock_now = MagicMock()
        mock_datetime.now.return_value = mock_now
        mock_now.strftime.return_value = "Η ώρα είναι 02:30 PM και η ημερομηνία είναι Friday, 27 October 2023"

        voice_assistant.get_time()

        # Verify locale was attempted to be set
        mock_setlocale.assert_called_with(locale.LC_TIME, 'el_GR.UTF-8')

        # Verify strftime was called with the correct format string
        mock_now.strftime.assert_called_with("Η ώρα είναι %I:%M %p και η ημερομηνία είναι %A, %d %B %Y")

        # Verify speak was called with the string returned by strftime
        mock_speak.assert_called_with("Η ώρα είναι 02:30 PM και η ημερομηνία είναι Friday, 27 October 2023")

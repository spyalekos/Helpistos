import sys
from unittest.mock import MagicMock, patch

# Mock dependencies before importing voice_assistant
sys.modules['gtts'] = MagicMock()
sys.modules['playsound'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()
sys.modules['wikipedia'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['bs4'] = MagicMock()

import voice_assistant

def test_get_time():
    """Tests the get_time function by mocking datetime and speak."""
    mock_time_str = "Η ώρα είναι 10:00 AM και η ημερομηνία είναι Monday, 01 January 2024"

    with patch('voice_assistant.speak') as mock_speak:
        with patch('voice_assistant.datetime.datetime') as mock_datetime:
            with patch('voice_assistant.locale.setlocale') as mock_setlocale:
                # Set up the mock datetime object
                mock_now = MagicMock()
                mock_datetime.now.return_value = mock_now
                mock_now.strftime.return_value = mock_time_str

                # Call the function
                voice_assistant.get_time()

                # Assertions
                mock_datetime.now.assert_called_once()
                mock_now.strftime.assert_called_once_with("Η ώρα είναι %I:%M %p και η ημερομηνία είναι %A, %d %B %Y")
                mock_speak.assert_called_once_with(mock_time_str)
                # Verify locale was attempted to be set
                mock_setlocale.assert_called_with(voice_assistant.locale.LC_TIME, 'el_GR.UTF-8')

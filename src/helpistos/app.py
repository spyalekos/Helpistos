import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import threading
import speech_recognition as sr
from gtts import gTTS
import os
try:
    import wikipedia
except ImportError:
    wikipedia = None
import datetime
import locale
import requests
from bs4 import BeautifulSoup
import pyperclip
import time

import sys
print(f"DEBUG: sys.path: {sys.path}")
print(f"DEBUG: 'java' in sys.modules: {'java' in sys.modules}")

try:
    from java import autoclass, dynamic_proxy
    print("DEBUG: java import SUCCESS")
except Exception as e:
    print(f"DEBUG: java import failed: {e}")
    # Try alternative
    try:
        import java
        print("DEBUG: import java SUCCESS")
    except Exception as e2:
         print(f"DEBUG: import java failed too: {e2}")
    autoclass = None
    dynamic_proxy = None

# --- Configuration ---
WIKI_LANG = "el"
SPEECH_LANG = "el-GR"

WMO_CODES_GREEK = {
    0: "Καθαρός ουρανός", 1: "Κυρίως αίθριος", 2: "Μερικώς νεφελώδης", 3: "Νεφελώδης",
    45: "Ομίχλη", 48: "Πάχνη",
    51: "Ελαφρύ ψιλόβροχο", 53: "Μέτριο ψιλόβροχο", 55: "Πυκνό ψιλόβροχο",
    56: "Παγωμένο ελαφρύ ψιλόβροχο", 57: "Παγωμένο πυκνό ψιλόβροχο",
    61: "Ασθενής βροχή", 63: "Μέτρια βροχή", 65: "Δυνατή βροχή",
    66: "Παγωμένη ασθενής βροχή", 67: "Παγωμένη δυνατή βροχή",
    71: "Ασθενής χιονόπτωση", 73: "Μέτρια χιονόπτωση", 75: "Πυκνή χιονόπτωση",
    77: "Χιονονιφάδες",
    80: "Ασθενείς μπόρες", 81: "Μέτριες μπόρες", 82: "Δυνατές μπόρες",
    85: "Ασθενείς χιονομπόρες", 86: "Δυνατές χιονομπόρες",
    95: "Καταιγίδα", 96: "Καταιγίδα με ασθενές χαλάζι", 99: "Καταιγίδα με δυνατό χαλάζι",
}

class Helpistos(toga.App):
    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        self.status_label = toga.Label(
            "Έλα μου. Τι θες;",
            style=Pack(padding=(0, 0, 10, 0))
        )
        
        self.output_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, padding=(0, 0, 10, 0))
        )

        listen_button = toga.Button(
            "Άκουσέ με",
            on_press=self.on_listen_press,
            style=Pack(padding=5)
        )

        main_box.add(self.status_label)
        main_box.add(self.output_text)
        main_box.add(listen_button)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

        # Try to set locale
        try:
            locale.setlocale(locale.LC_TIME, 'el_GR.UTF-8')
        except locale.Error:
            print("Locale 'el_GR.UTF-8' not supported.")

    def add_log(self, text):
        self.output_text.value += f"\n{text}"

    def speak(self, text):
        self.add_log(f"Assistant: {text}")
        def run_speak():
            try:
                tts = gTTS(text=text, lang=WIKI_LANG)
                temp_file = "temp_speech.mp3"
                tts.save(temp_file)
                
                # Use system player fallback for Linux/Desktop
                if os.name == 'posix':
                    # Try mpg123, ffplay, or other available players
                    os.system(f"mpg123 -q {temp_file} || ffplay -nodisp -autoexit -loglevel quiet {temp_file}")
                elif os.name == 'nt':
                    os.startfile(temp_file)
                
                time.sleep(1) # Give it a second to play
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                self.add_log(f"Speak Error: {e}")

        threading.Thread(target=run_speak, daemon=True).start()

    def on_listen_press(self, widget):
        self.status_label.text = "Ακούω..."
        threading.Thread(target=self.listen_and_process, daemon=True).start()

    def listen_android(self):
        # Class-level imports to avoid issues on non-Android platforms
        SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
        RecognizerIntent = autoclass('android.speech.RecognizerIntent')
        Intent = autoclass('android.content.Intent')
        
        # Get the MainActivity instance
        MainActivity = autoclass('org.beeware.android.MainActivity')
        context = MainActivity.singleton

        result_event = threading.Event()
        recognized_text = [None]
        error_msg = [None]

        @dynamic_proxy("android.speech.RecognitionListener")
        class HelperListener:
            def onReadyForSpeech(self, params):
                print("DEBUG: onReadyForSpeech")
            def onBeginningOfSpeech(self):
                print("DEBUG: onBeginningOfSpeech")
            def onRmsChanged(self, rmsdB): pass
            def onBufferReceived(self, buffer): pass
            def onEndOfSpeech(self):
                print("DEBUG: onEndOfSpeech")
            def onError(self, error):
                error_codes = {
                    1: "Network timeout", 2: "Network error", 3: "Audio error",
                    4: "Server error", 5: "Client error", 6: "Speech timeout",
                    7: "No match", 8: "Recognizer busy", 9: "Insufficient permissions"
                }
                msg = error_codes.get(error, f"Unknown error {error}")
                print(f"DEBUG: onError: {msg}")
                error_msg[0] = msg
                result_event.set()
            def onResults(self, results):
                print("DEBUG: onResults")
                matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if matches and matches.size() > 0:
                    recognized_text[0] = matches.get(0)
                    print(f"DEBUG: Recognized: {recognized_text[0]}")
                result_event.set()
            def onPartialResults(self, partialResults):
                print("DEBUG: onPartialResults")
            def onEvent(self, eventType, params): pass

        def start_recognition():
            try:
                # Check permissions at runtime
                PackageManager = autoclass('android.content.pm.PackageManager')
                Manifest = autoclass('android.provider.Settings').System # Fallback if direct Manifest import is tricky
                # Correct way for Manifest:
                ManifestPerm = autoclass('android.Manifest$permission')
                
                if context.checkSelfPermission(ManifestPerm.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED:
                    print("DEBUG: Requesting RECORD_AUDIO permission")
                    context.requestPermissions([ManifestPerm.RECORD_AUDIO], 1)
                    # We might need to wait for result or user to re-press, 
                    # but for now let's hope it's granted or that this triggers the dialog.
                
                recognizer = SpeechRecognizer.createSpeechRecognizer(context)
                recognizer.setRecognitionListener(HelperListener())
                
                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, SPEECH_LANG)
                
                print("DEBUG: Calling startListening")
                recognizer.startListening(intent)
            except Exception as e:
                print(f"DEBUG: Exception in start_recognition: {e}")
                error_msg[0] = str(e)
                result_event.set()

        # SpeechRecognizer MUST be called on the main thread
        context.runOnUiThread(start_recognition)
        
        # Wait for result
        finished = result_event.wait(timeout=15)
        if not finished:
            self.add_log("Error: Η αναγνώριση ομιλίας έληξε (Timeout).")
        elif error_msg[0]:
            self.add_log(f"Error: {error_msg[0]}")
        elif recognized_text[0]:
            command = recognized_text[0].lower()
            self.add_log(f"User: {command}")
            self.process_command(command)
        
        self.status_label.text = "Έλα μου. Τι θες;"

    def listen_and_process(self):
        # Use native Android recognition if on Android
        try:
            platform = str(self.platform).lower()
        except AttributeError:
            platform = "unknown"
            
        print(f"DEBUG: Current platform detected as: {platform}")
        print(f"DEBUG: autoclass available: {autoclass is not None}")
        
        if autoclass and platform == 'android':
            print("DEBUG: Redirecting to native Android recognition")
            self.listen_android()
            return

        print("DEBUG: Falling back to standard speech_recognition (requires PyAudio)")

        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                self.status_label.text = "Προσαρμογή θορύβου..."
                r.adjust_for_ambient_noise(source, duration=1)
                self.status_label.text = "Ακούω..."
                audio = r.listen(source, timeout=10, phrase_time_limit=10)
                self.status_label.text = "Αναγνώριση..."
                command = r.recognize_google(audio, language=SPEECH_LANG).lower()
                self.add_log(f"User: {command}")
                self.process_command(command)
        except sr.WaitTimeoutError:
            self.add_log("Error: Δεν ακούστηκε ομιλία (Timeout).")
        except sr.UnknownValueError:
            self.add_log("Error: Δεν ήταν δυνατή η αναγνώριση της ομιλίας.")
        except Exception as e:
            self.add_log(f"Listen Error: {e}")
        finally:
            self.status_label.text = "Έλα μου. Τι θες;"

    def process_command(self, command):
        if "γεια" in command:
            self.speak("Γεια και σε εσάς!")
        elif "ώρα" in command:
            now = datetime.datetime.now()
            time_str = now.strftime("Η ώρα είναι %I:%M %p και η ημερομηνία είναι %A, %d %B %Y")
            self.speak(time_str)
        elif "καιρός" in command:
            self.speak("Αναζήτηση καιρού...")
            # Simple weather logic moved here
            self.get_weather_logic(command)
        elif "νέα" in command or "ειδήσεις" in command:
            self.get_news_logic()
        elif "τέλος" in command or "έξοδος" in command or "στοπ" in command:
            self.speak("Αντίο!")
            self.exit()
        else:
            # Fallback to copy/paste if on desktop
            try:
                pyperclip.copy(command)
                self.add_log(f"Αντιγράφηκε: {command}")
            except Exception:
                pass

    def get_weather_logic(self, command):
        # Extremely simplified for the port
        city = "Athens" # Default or extract from command
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=el&format=json"
            geo_data = requests.get(geo_url).json()
            if geo_data.get("results"):
                loc = geo_data["results"][0]
                temp_url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}&current=temperature_2m,weather_code"
                w_data = requests.get(temp_url).json()
                temp = w_data["current"]["temperature_2m"]
                self.speak(f"Στην πόλη {loc['name']}, η θερμοκρασία είναι {temp} βαθμοί.")
        except Exception:
            self.speak("Σφάλμα καιρού.")

    def get_news_logic(self):
        try:
            url = "https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el"
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, 'xml')
            items = soup.find_all('item')[:2]
            for item in items:
                self.speak(item.title.text)
        except Exception:
            self.speak("Σφάλμα ειδήσεων.")

def main():
    return Helpistos("Helpistos", "com.example.helpistos")

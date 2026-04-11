import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import threading
# import speech_recognition as sr  # Moved to lazy import in listen_and_process
from gtts import gTTS
import os
import datetime
import locale
import requests
from bs4 import BeautifulSoup
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False
import time

# Java bridge imports moved to lazy initialization in listen_android()
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

        self.main_window = toga.MainWindow(title=f"{self.formal_name} v1.0.16")
        self.main_window.content = main_box
        self.main_window.show()

        # Detect Android flag
        import sys
        self.is_android_flag = False
        if hasattr(sys, 'getandroidsdk') or 'ANDROID_ROOT' in os.environ or 'android' in sys.platform.lower():
            self.is_android_flag = True

        # Helper for Java Bridge
        def get_java_bridge():
            _autoclass = None
            _dynamic_proxy = None
            _method = "None"
            try:
                from rubicon.java import autoclass as _autoclass, dynamic_proxy as _dynamic_proxy
                _method = "Rubicon"
            except:
                try:
                    import java
                    _autoclass = getattr(java, 'autoclass', None) or getattr(java, 'jclass', None)
                    _dynamic_proxy = getattr(java, 'dynamic_proxy', None)
                    _method = "Chaquopy"
                except:
                    try:
                        from jnius import autoclass as _autoclass
                        _method = "PyJnius"
                    except: pass
            return _autoclass, _dynamic_proxy, _method
        
        self.get_java_bridge = get_java_bridge

        # Try to set locale
        try:
            locale.setlocale(locale.LC_TIME, 'el_GR.UTF-8')
        except locale.Error:
            print("Locale 'el_GR.UTF-8' not supported.")
            
        # Request Android permissions at startup
        def request_initial_permissions():
            try:
                _autoclass, _, _method = self.get_java_bridge()
                if _autoclass:
                    self.add_log(f"[DEBUG] Java Bridge detect: {_method}")
                    PackageManager = _autoclass('android.content.pm.PackageManager')
                    ManifestPerm = _autoclass('android.Manifest$permission')
                    MainActivity = _autoclass('org.beeware.android.MainActivity')
                    context = MainActivity.singleton
                    
                    if context.checkSelfPermission(ManifestPerm.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED:
                        print("DEBUG: Requesting RECORD_AUDIO at startup")
                        context.requestPermissions([ManifestPerm.RECORD_AUDIO], 1)
            except Exception as e:
                print(f"DEBUG: Startup Permission Error: {e}")

        # Run on UI thread if possible
        if self.is_android_flag:
            try:
                _autoclass, _, _ = self.get_java_bridge()
                MainActivity = _autoclass('org.beeware.android.MainActivity')
                MainActivity.singleton.runOnUiThread(request_initial_permissions)
            except: pass

    def add_log(self, text):
        self.output_text.value += f"\n{text}"

    def speak(self, text):
        self.add_log(f"Assistant: {text}")
        def run_speak():
            try:
                tts = gTTS(text=text, lang=WIKI_LANG)
                temp_file = os.path.join(self.paths.app, "temp_speech.mp3")
                tts.save(temp_file)
                
                # Android Native Player
                if self.is_android_flag:
                    try:
                        _autoclass, _, _method = self.get_java_bridge()
                        if _autoclass:
                            MediaPlayer = _autoclass('android.media.MediaPlayer')
                            FileInputStream = _autoclass('java.io.FileInputStream')
                            
                            self.add_log(f"[DEBUG] Preparing MediaPlayer ({_method})")
                            player = MediaPlayer()
                            
                            fis = FileInputStream(temp_file)
                            player.setDataSource(fis.getFD())
                            player.prepare()
                            player.start()
                            fis.close()
                            
                            self.add_log("[DEBUG] MediaPlayer started")
                            
                            duration = player.getDuration()
                            time.sleep((duration / 1000) + 0.5)
                            player.release()
                        else:
                            self.add_log("Error: Java bridge not found for MediaPlayer")
                    except Exception as e:
                        self.add_log(f"Android Speak Error: {e}")
                
                # Use system player fallback for Linux/Desktop
                elif os.name == 'posix':
                    # Try mpg123, ffplay, or other available players
                    os.system(f"mpg123 -q {temp_file} || ffplay -nodisp -autoexit -loglevel quiet {temp_file}")
                elif os.name == 'nt':
                    os.startfile(temp_file)
                
                if not self.is_android_flag:
                    time.sleep(1) # Give it a second to play on desktop
                
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                self.add_log(f"Speak Error: {e}")

        threading.Thread(target=run_speak, daemon=True).start()

    def on_listen_press(self, widget):
        self.status_label.text = "Ακούω..."
        threading.Thread(target=self.listen_and_process, daemon=True).start()

    def listen_android(self):
        # Use helper for bridge discovery
        _autoclass, _dynamic_proxy, _method = self.get_java_bridge()

        if _autoclass is None:
            self.add_log("Error: Java bridge not found for STT.")
            return

        if _dynamic_proxy is None:
            self.add_log(f"Error: dynamic_proxy not available on bridge {_method}")
            return

        self.add_log(f"[DEBUG] Using STT bridge: {_method}")
        global autoclass, dynamic_proxy
        autoclass = _autoclass
        dynamic_proxy = _dynamic_proxy

        SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
        RecognizerIntent = autoclass('android.speech.RecognizerIntent')
        Intent = autoclass('android.content.Intent')
        
        # Get the MainActivity instance
        MainActivity = _autoclass('org.beeware.android.MainActivity')
        context = MainActivity.singleton

        result_event = threading.Event()
        recognized_text = [None]
        error_msg = [None]

        # Implementation of Listener based on bridge method
        if _method == "Rubicon":
            @_dynamic_proxy("android.speech.RecognitionListener")
            class HelperListener:
                def onReadyForSpeech(self, params): print("DEBUG: onReadyForSpeech")
                def onBeginningOfSpeech(self): print("DEBUG: onBeginningOfSpeech")
                def onRmsChanged(self, rmsdB): pass
                def onBufferReceived(self, buffer): pass
                def onEndOfSpeech(self): print("DEBUG: onEndOfSpeech")
                def onError(self, error):
                    error_msg[0] = f"Error code {error}"
                    result_event.set()
                def onResults(self, results):
                    matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    if matches and matches.size() > 0: recognized_text[0] = matches.get(0)
                    result_event.set()
                def onPartialResults(self, partialResults): pass
                def onEvent(self, eventType, params): pass
            listener = HelperListener()
        elif _method == "Chaquopy":
            # In Chaquopy, dynamic_proxy is a base class factory
            class HelperListener(_dynamic_proxy(_autoclass("android.speech.RecognitionListener"))):
                def onReadyForSpeech(self, params): print("DEBUG: onReadyForSpeech")
                def onBeginningOfSpeech(self): print("DEBUG: onBeginningOfSpeech")
                def onRmsChanged(self, rmsdB): pass
                def onBufferReceived(self, buffer): pass
                def onEndOfSpeech(self): print("DEBUG: onEndOfSpeech")
                def onError(self, error):
                    error_msg[0] = f"Error code {error}"
                    result_event.set()
                def onResults(self, results):
                    matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    if matches and matches.size() > 0: recognized_text[0] = matches.get(0)
                    result_event.set()
                def onPartialResults(self, partialResults): pass
                def onEvent(self, eventType, params): pass
            listener = HelperListener()
        else:
            self.add_log(f"Error: Unsupported bridge method {_method} for Proxy.")
            return

        def start_recognition():
            try:
                # Check permissions at runtime
                PackageManager = autoclass('android.content.pm.PackageManager')
                # Correct way for Manifest:
                ManifestPerm = autoclass('android.Manifest$permission')
                
                if context.checkSelfPermission(ManifestPerm.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED:
                    print("DEBUG: RECORD_AUDIO not granted. Cannot listen.")
                    error_msg[0] = "Παρακαλώ δώστε άδεια μικροφώνου."
                    result_event.set()
                    return
                
                recognizer = SpeechRecognizer.createSpeechRecognizer(context)
                recognizer.setRecognitionListener(listener)
                
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
        import sys
        import os
        
        # Ultra-robust Android detection
        is_android = False
        
        # Method 1: sys.getandroidsdk
        if hasattr(sys, 'getandroidsdk'): 
            is_android = True
            print("DEBUG: Detected Android via sys.getandroidsdk")
            
        # Method 2: os.environ
        if 'ANDROID_ROOT' in os.environ:
            is_android = True
            print("DEBUG: Detected Android via ANDROID_ROOT")
            
        # Method 3: sys.platform
        if 'android' in sys.platform.lower():
            is_android = True
            print("DEBUG: Detected Android via sys.platform")
            
        # Method 4: Toga platform attribute
        toga_platform = str(getattr(self, 'platform', 'unknown')).lower()
        if 'android' in toga_platform:
            is_android = True
            print(f"DEBUG: Detected Android via Toga platform: {toga_platform}")

        # Visible debug info for the user
        self.add_log(f"\n[DEBUG] Platform: {sys.platform} / Toga: {toga_platform}")
        self.add_log(f"[DEBUG] is_android: {is_android}")

        if self.is_android_flag:
            print("DEBUG: Executing Android/Native recognition path")
            self.listen_android()
            return

        # Desktop Fallback
        print("DEBUG: Executing Desktop/Fallback recognition path")
        try:
            import speech_recognition as sr
        except ImportError:
            self.add_log("Error: Η βιβλιοθήκη speech_recognition λείπει.")
            return

        try:
            import pyaudio
        except ImportError:
            self.add_log("Error: Το PyAudio λείπει (απαραίτητο για Desktop).")
            return

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
            if HAS_PYPERCLIP:
                try:
                    pyperclip.copy(command)
                    self.add_log(f"Αντιγράφηκε: {command}")
                except Exception:
                    self.add_log(f"Δεν κατάλαβα: {command}")
            else:
                self.add_log(f"Δεν κατάλαβα: {command}")

    def get_weather_logic(self, command):
        # Extremely simplified for the port
        city = "Athens" # Default or extract from command
        try:
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {
                "name": city,
                "count": 1,
                "language": "el",
                "format": "json"
            }
            geo_data = requests.get(geo_url, params=geo_params).json()
            if geo_data.get("results"):
                loc = geo_data["results"][0]
                temp_url = "https://api.open-meteo.com/v1/forecast"
                temp_params = {
                    "latitude": loc['latitude'],
                    "longitude": loc['longitude'],
                    "current": "temperature_2m,weather_code"
                }
                w_data = requests.get(temp_url, params=temp_params).json()
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
            if not items:
                self.speak("Δεν βρέθηκαν άρθρα ειδήσεων.")
                return

            headlines = [item.title.text for item in items]
            intro = "Οι δύο κυριότερες ειδήσεις είναι: "
            full_news = intro + ". ".join(headlines)
            self.speak(full_news)
        except Exception:
            self.speak("Σφάλμα ειδήσεων.")

def main():
    return Helpistos("Helpistos", "com.example.helpistos")

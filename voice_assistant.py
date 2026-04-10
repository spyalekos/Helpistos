import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
import wikipedia
import datetime
import locale
import requests
from bs4 import BeautifulSoup
import pyperclip
from pynput.keyboard import Key, Controller
import time

# --- Configuration ---
# Set the language for Wikipedia and speech recognition
WIKI_LANG = "el"
SPEECH_LANG = "el-GR"

# Initialize a global session for news fetching to enable connection pooling
NEWS_SESSION = requests.Session()
NEWS_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# --- Data ---
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

# --- Core Functions ---
def speak(text):
    """Converts text to speech using gTTS and plays it."""
    try:
        tts = gTTS(text=text, lang=WIKI_LANG)
        temp_file = "temp_speech.mp3"
        tts.save(temp_file)
        playsound(temp_file, block=True)
        os.remove(temp_file)
    except Exception as e:
        print(f"Σφάλμα κατά την αναπαραγωγή ήχου: {e}")

def listen(recognizer, microphone):
    """Listens for audio input from the microphone and converts it to text."""
    with microphone as source:
        print("Ακούω...")
        try:
            audio = recognizer.listen(source)
            print("Αναγνώριση...")
            command = recognizer.recognize_google(audio, language=SPEECH_LANG)
            print(f"Είπατε: {command}")
            return command.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            speak("Συγγνώμη, η υπηρεσία ομιλίας δεν είναι διαθέσιμη.")
            return ""

# --- Feature Functions ---
def get_time():
    """Gets the current time and date in Greek."""
    try:
        locale.setlocale(locale.LC_TIME, 'el_GR.UTF-8')
    except locale.Error:
        print("Locale 'el_GR.UTF-8' not supported, using default.")
    
    now = datetime.datetime.now()
    time_str = now.strftime("Η ώρα είναι %I:%M %p και η ημερομηνία είναι %A, %d %B %Y")
    speak(time_str)

def get_weather(recognizer, microphone):
    """Asks for a city and provides the weather forecast."""
    speak("Για ποια πόλη θέλετε να μάθετε τον καιρό;")
    city = listen(recognizer, microphone)
    if not city:
        speak("Δεν άκουσα το όνομα της πόλης.")
        return
        
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": city,
            "count": 1,
            "language": "el",
            "format": "json"
        }
        geo_response = requests.get(geo_url, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            speak(f"Δεν μπόρεσα να βρω την πόλη {city}.")
            return

        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        found_city_name = location["name"]

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code"
        }
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        temperature = weather_data["current"]["temperature_2m"]
        weather_code = weather_data["current"]["weather_code"]
        weather_description = WMO_CODES_GREEK.get(weather_code, "άγνωστες καιρικές συνθήκες")

        speak(f"Στην πόλη {found_city_name}, η θερμοκρασία είναι {temperature} βαθμοί Κελσίου και ο καιρός είναι {weather_description}.")
    except requests.exceptions.RequestException:
        speak("Συγγνώμη, δεν μπορώ να συνδεθώ στην υπηρεσία καιρού αυτή τη στιγμή.")
    except (KeyError, IndexError):
        speak("Παρουσιάστηκε σφάλμα κατά την ανάκτηση των δεδομένων καιρού.")

def get_news():
    """Fetches and reads the top 2 news headlines from Google News Greece."""
    try:
        url = "https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el"
        response = NEWS_SESSION.get(url)
        response.raise_for_status()
        
        # Explicitly use the lxml parser for robustness
        soup = BeautifulSoup(response.text, 'lxml-xml')

        items = soup.find_all('item')
        if not items:
            # This case might happen if the RSS structure changes
            speak("Δεν βρέθηκαν άρθρα ειδήσεων στο feed.")
            print("DEBUG: RSS feed was fetched, but no <item> tags were found.")
            print(f"DEBUG: Response text: {response.text[:500]}") # Print first 500 chars of response
            return

        headlines = [item.title.text for item in items[:2]]

        if not headlines:
            speak("Δεν μπόρεσα να βρω τους τίτλους των ειδήσεων.")
            return

        intro = "Οι δύο κυριότερες ειδήσεις είναι: "
        full_news = intro + ". ".join(headlines)
        speak(full_news)

    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request failed: {e}")
        speak("Συγγνώμη, δεν μπορώ να συνδεθώ στην υπηρεσία ειδήσεων.")
    except Exception as e:
        # Print the full error for debugging
        print(f"An unexpected error occurred in get_news: {e}")
        speak("Παρουσιάστηκε ένα σφάλμα κατά την ανάκτηση των ειδήσεων.")

# --- Main Loop ---
def main():
    try:
        locale.setlocale(locale.LC_TIME, 'el_GR.UTF-8')
    except locale.Error:
        print("Locale 'el_GR.UTF-8' not supported. Using default.")

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Configure recognizer
    recognizer.pause_threshold = 2.0  # Increased from 1.0 based on user feedback

    with microphone as source:
        print("Ρύθμιση θορύβου περιβάλλοντος...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

    speak("Έλα μου. Τι θες;")
    
    while True:
        command = listen(recognizer, microphone)
        if not command:
            continue

        if "γεια" in command:
            speak("Γεια και σε εσάς!")
        elif "ώρα" in command:
            get_time()
        elif "καιρός" in command:
            get_weather(recognizer, microphone)
        elif command.startswith("βρες"):
            search_term = command.replace("βρες", "").strip()
            if not search_term:
                speak("Δεν κατάλαβα τι να βρω. Πείτε για παράδειγμα 'βρες την Αθήνα'.")
            else:
                try:
                    wikipedia.set_lang(WIKI_LANG)
                    summary = wikipedia.summary(search_term, sentences=2)
                    speak(f"Σύμφωνα με τη Βικιπαίδεια, {summary}")
                except wikipedia.exceptions.PageError:
                    speak(f"Δεν βρήκα πληροφορίες για το θέμα: {search_term}.")
                except wikipedia.exceptions.DisambiguationError:
                    speak(f"Η αναζήτησή σας για '{search_term}' δεν είναι συγκεκριμένη. Μπορείτε να είστε πιο σαφής;")
                except Exception as e:
                    speak("Παρουσιάστηκε ένα σφάλμα κατά την αναζήτηση στη Βικιπαίδεια.")
                    print(f"Wikipedia Error: {e}")
        elif "νέα" in command or "ειδήσεις" in command:
            get_news()
        elif "τέλος" in command or "έξοδος" in command or "στοπ" in command:
            speak("Αντίο!")
            break
        else:
            try:
                keyboard = Controller()
                pyperclip.copy(command)
                time.sleep(0.1) 
                with keyboard.pressed(Key.ctrl):
                    keyboard.press('v')
                    keyboard.release('v')
            except Exception as e:
                with open("paste_error.log", "w", encoding="utf-8") as f:
                    f.write(f"An error occurred during paste with pynput: {e}")


if __name__ == "__main__":
    main()

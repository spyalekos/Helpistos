# Οδηγίες & Κανόνες Ανάπτυξης AI (AI Reminders) — Helpistos

*Αυτό το αρχείο διαβάζεται και λαμβάνεται υπόψη από τον AI agent κατά την εκκίνηση του τρέχοντος project για την αποφυγή επαναλαμβανόμενων διευκρινίσεων.*

## Βασικοί Κανόνες (Σημαντικοί)

1. **Package / Dependency Management:** 
   - Χρησιμοποιούμε **ΠΑΝΤΟΤΕ** `uv`. 
   - Δεν τρέχουμε «γυμνές» pip εντολές. Αξιοποιούμε `uv pip install ...` ή `uv add ...` ή `uv run ...`.
   - **ΠΡΟΣΟΧΗ:** Το `pyperclip` ΔΕΝ είναι συμβατό με Android ARM. Πρέπει να αφαιρείται από τα dependencies/requires και να χρησιμοποιείται με conditional import (`HAS_PYPERCLIP` guard) στον κώδικα.

2. **Framework:** 
   - Το project χρησιμοποιεί το **BeeWare (Toga)** framework. 
   - Όλες οι UI αλλαγές πρέπει να ακολουθούν τα APIs της Toga.
   - **Ανίχνευση Android:** Χρησιμοποιούμε το flag `self.is_android_flag` που ορίζεται στο `startup` για καθαρότερο κώδικα.

3. **Android Build & Release:** 
   - Για παραγωγή APK χρησιμοποιούμε **αποκλειστικά** το script `./build_apk.sh`. 
   - Το script ρυθμίζει αυτόματα τα περιβάλλοντα (JAVA_HOME, ANDROID_HOME, PATH για Python 3.12).
   - **GitHub Release:** Μετά από κάθε επιτυχημένο build και increment έκδοσης, δημιουργούμε Release στο GitHub χρησιμοποιώντας το `gh` CLI:
     `gh release create vX.Y.Z ./build/helpistos-vXYZ.apk --title "vX.Y.Z" --notes "..."`

4. **Εκδόσεις (Versioning):** 
   - Οι εκδόσεις αυξάνονται κατά **0.0.1**.
   - Ενημερώνονται σε: `pyproject.toml`, `src/helpistos/app.py` (MainWindow title), `CHANGELOG.md` και `build_apk.sh`.

5. **Γλώσσα Τεκμηρίωσης:** 
   - Changelog, `README.md` και τεκμηρίωση παραδίδονται **ΠΑΝΤΟΤΕ στα Ελληνικά**.

## Αρχιτεκτονική Ήχου & Αναγνώρισης (Voice Architecture)

1. **TTS (Text-to-Speech):**
   - Χρησιμοποιούμε `gTTS`.
   - **Android:** Χρήση `android.media.MediaPlayer` μέσω `autoclass` (ή fallback σε `jclass` από το module `java`).
     - **ΠΡΟΣΟΧΗ:** Το αρχείο ήχου πρέπει να ορίζεται με **απόλυτο μονοπάτι** χρησιμοποιώντας το `self.paths.app`.
     - Απαραίτητη η χρήση `player.prepare()` και `player.start()`.
     - Πρέπει να γίνεται `player.release()` μετά την αναπαραγωγή για απελευθέρωση πόρων.
   - **Desktop:** Fallback σε `mpg123` ή `ffplay` μέσω `os.system`.

2. **STT (Speech-to-Text):**
   - **Android:** Native `android.speech.SpeechRecognizer` μέσω `rubicon-java`. Η κλήση `startListening` πρέπει να γίνεται στο UI thread (`runOnUiThread`).
   - **Desktop:** Fallback στο `speech_recognition` (SR) library.

## Πιθανά Προβλήματα & Σημεία Προσοχής (Gotchas)

1. **Paths στο Android:** 
   - Ποτέ μην χρησιμοποιείτε σχετικά μονοπάτια (π.χ. `"temp.mp3"`) για εγγραφή αρχείων στο Android. Χρησιμοποιείτε πάντα `os.path.join(self.paths.app, "filename")`.
2. **UI Thread:** 
   - Οποιαδήποτε αλληλεπίδραση με native Android APIs (SpeechRecognizer, MediaPlayer) πρέπει να διασφαλίζεται ότι τρέχει στο σωστό thread αν απαιτείται από το API.
3. **Chaquopy:** 
   - Απαιτεί Python 3.12 στο PATH κατά το build. Το `build_apk.sh` το φροντίζει αυτόματα αν η Python βρίσκεται στο standard uv path.
4. **Clipboard:** 
   - Το `pyperclip` αποτυγχάνει σε Android. Πάντα χρησιμοποιούμε guards.

5. **BeeWare Android permissions (`pyproject.toml`):**
   - Τα δικαιώματα (όπως το `RECORD_AUDIO`) ΔΕΝ μπαίνουν πλέον στο `[tool.briefcase.app.myapp.android]` ως απλή λίστα. 
   - Απαιτούν ρητά τη χρήση του cross-platform dict του BeeWare στο root του app config:
     ```toml
     [tool.briefcase.app.helpistos]
     permission = { microphone = "Λόγος χρήσης" }
     ```
   - Χωρίς αυτό, το `AndroidManifest.xml` αγνοεί τις άδειες και το Android λειτουργικό κρύβει τις ρυθμίσεις αδειών από τον χρήστη.

6. **Chaquopy Android Context & UI Threads:**
   - Η κλήση `MainActivity.singleton` είναι καταργημένη/επικίνδυνη. Το σωστό Android Context λαμβάνεται **αποκλειστικά** μέσω της Toga: `self.main_window.app._impl.native` (ή `toga.App.app._impl.native`).
   - Για να εκτελεστεί μέθοδος (όπως to STT) στο UI Thread, η Chaquopy απαιτεί τη δημιουργία ρητού proxy `java.lang.Runnable`. Αλλιώς, η κλήση `runOnUiThread(method)` θα αποτύχει σιωπηλά ή θα κρασάρει. Παράδειγμα proxy:
     ```python
     Runnable = autoclass("java.lang.Runnable")
     class PythonRunnable(dynamic_proxy(Runnable)):
         def __init__(self, target):
             super().__init__()
             self.target = target
         def run(self):
             self.target()
     ```
   - **Ποτέ** δεν ανανεώνουμε ενδείξεις οθόνης Toga (`self.status_label.text = ...`) απευθείας από background thread, γιατί προκαλείται άμεσο Crash (`Animators may only be run on Looper threads`). Χρησιμοποιούμε ΠΑΝΤΑ: `main_window.app.loop.call_soon_threadsafe(update_ui_func)`.

---
*Όταν ο χρήστης ζητά αλλαγές σ' αυτό το project, ξεκινάμε με γνώμονα αυτούς τους κανόνες.*

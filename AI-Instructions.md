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

3. **Android Build (Briefcase):** 
   - Για παραγωγή APK χρησιμοποιούμε **αποκλειστικά** το script `./build_apk.sh`. 
   - Το script ρυθμίζει αυτόματα:
     - `JAVA_HOME` και `ANDROID_HOME` (από το briefcase tools cache).
     - `GRADLE_OPTS="-Xmx2g -Dorg.gradle.daemon=false"`.
     - Προσθήκη της Python 3.12 του `uv` στο `PATH` (απαραίτητο για το Chaquopy).
   - Χρησιμοποιούμε ένα dedicated venv (`.briefcase-venv`) για το briefcase για να αποφύγουμε συγκρούσεις με system libs (π.χ. `pygobject`).

4. **Εκδόσεις (Versioning):** 
   - Οι εκδόσεις αυξάνονται κατά **0.0.1**.
   - Ενημερώνονται σε: `pyproject.toml` (`[project].version` και `[tool.briefcase].version`), `app.py`.

5. **Γλώσσα Τεκμηρίωσης:** 
   - Changelog, `README.md` και τεκμηρίωση παραδίδονται **ΠΑΝΤΟΤΕ στα Ελληνικά**.

## Αρχιτεκτονική Ήχου & Αναγνώρισης (Voice Architecture)

1. **TTS (Text-to-Speech):**
   - Χρησιμοποιούμε `gTTS`.
   - Στο Android, η αναπαραγωγή γίνεται μέσω `android.media.MediaPlayer` (autoclass).
   - Στο Desktop, χρησιμοποιούμε system players (`mpg123`, `ffplay`) μέσω `os.system`.

2. **STT (Speech-to-Text):**
   - **Android:** Χρησιμοποιούμε το native `android.speech.SpeechRecognizer` μέσω `rubicon-java` (autoclass). Η κλήση `startListening` πρέπει να γίνεται στο UI thread (`runOnUiThread`).
   - **Desktop:** Fallback στο `speech_recognition` (SR) library.

3. **Permissions:**
   - Τα permissions (`RECORD_AUDIO`, `INTERNET`) πρέπει να δηλώνονται στο `pyproject.toml` κάτω από `[tool.briefcase.app.helpistos.android]`.
   - Στο Android, γίνεται runtime check/request για το `RECORD_AUDIO`.

## Πιθανά Προβλήματα & Σημεία Προσοχής (Gotchas)

1. **Chaquopy & Python Version:** 
   - Το Chaquopy απαιτεί την αντίστοιχη έκδοση Python (3.12) στο `PATH` του host κατά το build.
2. **UI Thread (Android):** 
   - Οποιαδήποτε αλληλεπίδραση με native Android APIs (SpeechRecognizer, MediaPlayer) πρέπει να διασφαλίζεται ότι τρέχει στο σωστό thread.
3. **Clipboard:** 
   - Το `pyperclip` αποτυγχάνει σε Android (έλλειψη X11/Wayland). Πάντα χρησιμοποιούμε guards.
4. **Build Memory:** 
   - Το APK build είναι ενεργοβόρο. Αν αποτύχει το Gradle λόγω μνήμης, επιβεβαιώνουμε τα `GRADLE_OPTS` στο `build_apk.sh`.

---
*Όταν ο χρήστης ζητά αλλαγές σ' αυτό το project, ξεκινάμε με γνώμονα αυτούς τους κανόνες.*

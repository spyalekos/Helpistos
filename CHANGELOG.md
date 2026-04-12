## 1.0.27
- Fix: Επίλυση του `ERROR_RECOGNIZER_BUSY` (Error 8) μέσω επαναχρησιμοποίησης του `SpeechRecognizer` instance και κλήσης της `cancel()` πριν από κάθε νέα έναρξη αναγνώρισης.

## 1.0.26
- Fix: Επίλυση του `AttributeError: 'HelperListener' object has no attribute 'add_log'` κατά την εκκίνηση του STT (Chaquopy/Rubicon proxy classes scoping alias).

## 1.0.25
- Fix: Επίλυση σφάλματος `UnboundLocalError: cannot access local variable 'Intent'` το οποίο εμφανίστηκε (μετά την επιτυχή εκχώρηση αδειών) λόγω python variable scope shadowing στη συνάρτηση έναρξης της αναγνώρισης (STT).

## 1.0.24
- Fix: Διόρθωση του `pyproject.toml` για να γίνεται deploy η Android άδεια μικροφώνου στο `AndroidManifest.xml` (αντικατάσταση του παλιού `.android` list με το νέο cross-platform dictionary `permission` του BeeWare).

## 1.0.23
- Fix: Διόρθωση του `pyproject.toml` για να γίνεται deploy η Android άδεια μικροφώνου στο `AndroidManifest.xml` (αντικατάσταση του παλιού `.android` list με το νέο cross-platform dictionary `permission` του BeeWare).

## 1.0.22
- Feature: Αυτόματο άνοιγμα των Ρυθμίσεων Εφαρμογής (Application Settings) σε περίπτωση που το σύστημα Android απορρίψει την αίτηση αδειών μικροφώνου, διευκολύνοντας την χειροκίνητη ενεργοποίησή τους από τον χρήστη.

## 1.0.21
- Fix: Διόρθωση Fatal Exception κατά την ενημέρωση του UI (status label) από background thread μέσω `call_soon_threadsafe`.
- Fix: Διασφάλιση εμφάνισης του παραθύρου δικαιωμάτων μικροφώνου (Java String Array casting για Chaquopy).

## 1.0.20
- Fix: Καθολικό `try-except` γύρω από όλη τη `listen_android` για τον εντοπισμό σιωπηρών σφαλμάτων.
- Fix: Αντικατάσταση του παρωχημένου `MainActivity.singleton` με τον επίσημο τρόπο `toga.App.app._impl.native` για την ασφαλή απόκτηση του Android context στο Chaquopy.
- Fix: Καθυστέρηση κλήσης των αδειών (permissions) για να βεβαιωθούμε ότι έχει δημιουργηθεί το `_impl`.

## 1.0.19
- Fix: Υλοποίηση `Runnable` proxy για τη γέφυρα Chaquopy, επιτρέποντας την εκτέλεση κώδικα στο UI Thread (runOnUiThread).
- Fix: Εφαρμογή του Runnable proxy στην αναγνώριση φωνής και στην αίτηση αδειών.
- UI: Πρόσθετο log `[DEBUG] STT: Wrapping start_recognition in Runnable proxy`.

## 1.0.18
- Fix: Αλλαγή του `add_log` ώστε να χρησιμοποιεί το `call_soon_threadsafe` για αξιόπιστη εμφάνιση logs από το UI thread.
- Fix: Απόλυτη θωράκιση της `start_recognition` με καθολικό `try/except` και διαγνωστικά logs στην κορυφή.
- Fix: Διασφάλιση πρόσβασης στις Java κλάσεις εντός του UI thread closure.

## 1.0.17
- UI: Super-Logging για όλα τα Android callbacks απευθείας στην οθόνη.
- Fix: Thread-safe `add_log` για αποφυγή θεμάτων με background tasks.
- Diagnostics: Έλεγχος διαθεσιμότητας SpeechRecognizer και κατάστασης permissions στο log.
- Diagnostics: Έλεγχος ύπαρξης αρχείου ήχου πριν την αναπαραγωγή.

## 1.0.16
- Fix: Διαφορετική υλοποίηση Proxy (Listener) για Rubicon και Chaquopy.
- Fix: Χρήση `FileInputStream` και `FileDescriptor` για αναπαραγωγή ήχου στον `MediaPlayer`.
- UI: Πρόσθετα logs για την προετοιμασία του ήχου και τη δημιουργία του Proxy.

## 1.0.15
- Fix: Κεντρική μέθοδος `get_java_bridge` για ομοιόμορφη ανίχνευση Java (Rubicon, Chaquopy, PyJnius).
- UI: Βελτιωμένο debugging με αναφορά της μεθόδου Java Bridge στην οθόνη.
- Fix: Διασφάλιση ύπαρξης `dynamic_proxy` πριν την έναρξη του STT.

## 1.0.14
- Fix: Υλοποίηση `android.media.MediaPlayer` για αναπαραγωγή ήχου στο Android.
- Fix: Δημιουργία απόλυτου μονοπατιού για τα προσωρινά αρχεία ήχου.
- Refactor: Βελτιστοποίηση ανίχνευσης Android μέσω class flag.

## 1.0.13
- Fix: Αίτηση άδειας μικροφώνου κατά την εκκίνηση.
- UI: Βελτιωμένη ροή αναγνώρισης φωνής.

## 1.0.12
- Fix: Οριστική επίλυση Java Bridge με χρήση του `jclass` (fallback για autoclass).

## 1.0.11
- Fix: Προσθήκη `pyjnius` και ενισχυμένο debugging του module `java`.

## 1.0.10
- Fix: Διόρθωση σφάλματος NoneType στην κλήση της Java.
- Fix: Διασφάλιση συγχρονισμού έκδοσης και χρόνου build.

## 1.0.9
- Fix: Διόρθωση IndentationError στο app.py.

## 1.0.8
- Fix: Διόρθωση crash στην εκκίνηση (lazy java initialization).
- Fix: Συγχρονισμός εσωτερικής έκδοσης APK και μετονομασία αρχείου.

## 1.0.7
- Fix: Οριστική επίλυση Java Bridge με Super-Robust imports και διόρθωση Build Script (`update -r`).

## 1.0.6
- Fix: Προσθήκη `rubicon-java` στα requirements και προτίμηση Rubicon Bridge για Native Android APIs.

## 1.0.5
- Ενημέρωση εσωτερικής έκδοσης APK και αυτοματοποίηση update στο build script.

## 1.0.4
- Fix: Υποστήριξη εναλλακτικού Java Bridge (rubicon-java) και λεπτομερής καταγραφή σφαλμάτων.

## 1.0.3
- Fix: Υπερ-ενισχυμένη ανίχνευση Android (4 μέθοδοι) και debug info στην οθόνη.

## 1.0.2
- Fix: Οριστική λύση στο detection του Android και απομόνωση του Desktop κώδικα (PyAudio).

## 1.0.1
- Hotfix: Διόρθωση σφάλματος PyAudio στο Android (lazy load & robust detection).

## 1.0.0
- Πλήρης υποστήριξη Android (Native SPEECH_RECOGNITION).
- Διόρθωση ασυμβατότητας με `pyperclip`.
- Δημιουργία αυτοματοποιημένου script build (`build_apk.sh`).
- Συγχρονισμός με το GitHub repository.
- Ενημέρωση AI-Instructions.md για BeeWare/Toga.

## 0.1.0
- Initial release.

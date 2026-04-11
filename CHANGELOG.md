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

import time

def mock_speak(text):
    """Simulates the overhead of gTTS generation, disk I/O, and playback initialization."""
    # Each call to speak() involves:
    # 1. gTTS(text, lang='el') - Network request to Google Translate TTS API
    # 2. tts.save("temp.mp3") - Disk I/O
    # 3. playsound("temp.mp3") - Audio device initialization and playback
    # 4. os.remove("temp.mp3") - Disk I/O
    print(f"Speaking: {text[:50]}...")
    time.sleep(2.0) # Simulated 2 seconds overhead per call

def run_baseline():
    headlines = [
        "Πρώτη είδηση: Η Ελλάδα ενισχύει τις διπλωματικές της σχέσεις.",
        "Δεύτερη είδηση: Νέα μέτρα για την προστασία του περιβάλλοντος."
    ]

    print("--- Running Baseline (Multiple speak calls) ---")
    start_time = time.time()

    mock_speak("Οι δύο κυριότερες ειδήσεις είναι:")
    for headline in headlines:
        mock_speak(headline)

    end_time = time.time()
    baseline_duration = end_time - start_time
    print(f"Baseline Duration: {baseline_duration:.2f} seconds\n")
    return baseline_duration

def run_optimized():
    headlines = [
        "Πρώτη είδηση: Η Ελλάδα ενισχύει τις διπλωματικές της σχέσεις.",
        "Δεύτερη είδηση: Νέα μέτρα για την προστασία του περιβάλλοντος."
    ]

    print("--- Running Optimized (Single speak call) ---")
    start_time = time.time()

    full_text = "Οι δύο κυριότερες ειδήσεις είναι: " + ". ".join(headlines)
    mock_speak(full_text)

    end_time = time.time()
    optimized_duration = end_time - start_time
    print(f"Optimized Duration: {optimized_duration:.2f} seconds\n")
    return optimized_duration

if __name__ == "__main__":
    b_time = run_baseline()
    o_time = run_optimized()

    improvement = b_time - o_time
    percentage = (improvement / b_time) * 100

    print(f"Total Improvement: {improvement:.2f} seconds")
    print(f"Speedup: {percentage:.1f}%")

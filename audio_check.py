import speech_recognition as sr
try:
    mics = sr.Microphone.list_microphone_names()
    print("Available Microphones:")
    for i, name in enumerate(mics):
        print(f"{i}: {name}")
    
    with sr.Microphone() as source:
        print(f"\nDefault Microphone: {source.device_index}")
except Exception as e:
    print(f"Error listing microphones: {e}")

import pyttsx3

print("Testing voice system...")

try:
    engine = pyttsx3.init()
    
    # Get available voices
    voices = engine.getProperty('voices')
    print(f"Found {len(voices)} voices:")
    for i, voice in enumerate(voices):
        print(f"  {i}: {voice.name} (ID: {voice.id})")
    
    # Test each voice
    for i, voice in enumerate(voices):
        print(f"\nTesting voice {i}: {voice.name}")
        engine.setProperty('voice', voice.id)
        engine.setProperty('rate', 120)
        engine.setProperty('volume', 1.0)
        
        print("Saying test phrase...")
        engine.say(f"This is test voice number {i}")
        engine.runAndWait()
        print("Done")
        
        input("Press Enter to continue to next voice...")
    
    print("\nVoice test completed!")
    
except Exception as e:
    print(f"Voice error: {e}")
    print("Possible solutions:")
    print("1. Check your system volume")
    print("2. Check speakers/headphones are connected")
    print("3. Try running as administrator")
    print("4. Windows text-to-speech might be disabled")

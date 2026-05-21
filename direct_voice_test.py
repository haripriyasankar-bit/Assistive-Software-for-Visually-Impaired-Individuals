import pyttsx3
import time

print("Direct voice test - Testing different approaches...")

try:
    # Method 1: Basic initialization
    print("\n1. Testing basic voice...")
    engine1 = pyttsx3.init()
    engine1.say("Test 1: Basic voice working")
    engine1.runAndWait()
    print("Method 1 completed")
    
    time.sleep(2)
    
    # Method 2: With explicit voice selection
    print("\n2. Testing with voice selection...")
    engine2 = pyttsx3.init()
    voices = engine2.getProperty('voices')
    print(f"Available voices: {len(voices)}")
    
    for i, voice in enumerate(voices):
        print(f"Voice {i}: {voice.name}")
        engine2.setProperty('voice', voice.id)
        engine2.say(f"Test 2: Voice {i} - {voice.name}")
        engine2.runAndWait()
        time.sleep(1)
    
    # Method 3: Different settings
    print("\n3. Testing with different settings...")
    engine3 = pyttsx3.init()
    engine3.setProperty('rate', 100)  # Slower
    engine3.setProperty('volume', 1.0)  # Max volume
    engine3.say("Test 3: Slow and loud")
    engine3.runAndWait()
    print("Method 3 completed")
    
    print("\n✅ All voice tests completed!")
    print("If you didn't hear anything, check:")
    print("1. Windows volume settings")
    print("2. Audio output device (speakers/headphones)")
    print("3. Windows text-to-speech settings")
    
except Exception as e:
    print(f"❌ Voice error: {e}")

input("\nPress Enter to exit...")

import pyttsx3

print("Simple voice test - You should hear 'Hello World'")

try:
    engine = pyttsx3.init()
    engine.say("Hello World")
    engine.runAndWait()
    print("Voice test completed - Did you hear it?")
except Exception as e:
    print(f"Error: {e}")

input("Press Enter to exit...")

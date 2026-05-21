import torch
import cv2
import pyttsx3
import threading
import time

print("Loading model...")

# Initialize text-to-speech engine - simple approach (like working test)
try:
    engine = pyttsx3.init()
    # Test voice immediately
    print("Testing voice...")
    engine.say("Detection system ready")
    engine.runAndWait()
    print("Voice test completed - Working!")
    print("Voice engine initialized successfully")
except Exception as e:
    print(f"Voice engine failed: {e}")
    engine = None

# Load YOLOv5 pretrained model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

print("Model loaded successfully")

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not opened")
    exit()

print("Camera opened")

# Voice announcement function - simplified and reliable
def speak_detected_objects(objects, voice_engine):
    if voice_engine and objects:
        # Count unique objects and list all of them
        unique_objects = {}
        for obj in objects:
            name = obj['name']
            if name not in unique_objects:
                unique_objects[name] = 0
            unique_objects[name] += 1
        
        # Create announcement text with ALL objects
        announcement = "I see: "
        object_list = []
        for name, count in unique_objects.items():
            if count == 1:
                object_list.append(f"{name}")
            else:
                object_list.append(f"{count} {name}s")
        
        announcement += ", ".join(object_list)
        print(f"🎤 Speaking: {announcement}")  # Debug line
        
        # Simple direct approach (like test 1 that worked)
        try:
            voice_engine.say(announcement)
            voice_engine.runAndWait()
            print("✅ Voice announcement completed")
        except Exception as e:
            print(f"❌ Voice error: {e}")
    else:
        print("🔇 No voice engine or no objects to announce")

# Global voice state
is_speaking = False

# Track last announcement time to avoid spam
last_announcement_time = 0
announcement_delay = 1  # seconds between announcements (reduced from 3)

while True:
    try:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break

        # Run detection
        results = model(frame)

        # Get detected objects information
        detections = results.pandas().xyxy[0]
        
        # Convert to list of dictionaries for voice function
        detected_objects = []
        for idx, row in detections.iterrows():
            detected_objects.append({
                'name': row['name'],
                'confidence': row['confidence']
            })
        
        # Voice announcement with proper timing to prevent overload
        current_time = time.time()
        if detected_objects and (current_time - last_announcement_time) > 1.5:  # 1.5 seconds between announcements
            speak_detected_objects(detected_objects, engine)
            last_announcement_time = current_time
        
        # Print detected objects to console
        if len(detections) > 0:
            print(f"\n--- Detected Objects ({len(detections)}) ---")
            for idx, row in detections.iterrows():
                print(f"{idx+1}. {row['name']} (Confidence: {row['confidence']:.2f})")
        else:
            print("\n--- No objects detected ---")

        # Render results on frame
        annotated_frame = results.render()[0]
        
        # Add object count overlay
        text = f"Objects: {len(detections)}"
        cv2.putText(annotated_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Object Detection", annotated_frame)

        # Press Q to quit (reduced wait time for more frequent processing)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Detection stopped by user")
            break
            
    except Exception as e:
        print(f"Error in detection loop: {e}")
        continue

try:
    cap.release()
    cv2.destroyAllWindows()
    if engine:
        try:
            engine.stop()
        except:
            pass
except Exception as e:
    print(f"Cleanup error: {e}")

print("Detection completed successfully")

import torch
import cv2
import pyttsx3
import time

print("Loading model...")

# Initialize voice exactly like the working test
engine = pyttsx3.init()
print("Voice engine ready")

# Load YOLOv5 pretrained model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
print("Model loaded successfully")

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not opened")
    exit()

print("Camera opened")
print("Starting detection...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read frame")
        break

    # Run detection
    results = model(frame)

    # Get detected objects information
    detections = results.pandas().xyxy[0]
    
    # Convert to list for voice function
    detected_objects = []
    for idx, row in detections.iterrows():
        detected_objects.append(row['name'])
    
    # Print detected objects to console
    if len(detections) > 0:
        print(f"\n--- Detected Objects ({len(detections)}) ---")
        for idx, row in detections.iterrows():
            print(f"{idx+1}. {row['name']} (Confidence: {row['confidence']:.2f})")
        
        # Voice announcement - simple approach like working test
        if detected_objects:
            # Create simple announcement
            unique_objects = list(set(detected_objects))  # Remove duplicates
            announcement = "I see: " + ", ".join(unique_objects)
            
            print(f"🎤 Speaking: {announcement}")
            
            # Simple voice call (exactly like working test 1)
            engine.say(announcement)
            engine.runAndWait()
            print("✅ Voice completed")
    else:
        print("\n--- No objects detected ---")

    # Render results on frame
    annotated_frame = results.render()[0]
    
    # Add object count overlay
    text = f"Objects: {len(detections)}"
    cv2.putText(annotated_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Object Detection", annotated_frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Detection stopped by user")
        break

    # Small delay to prevent voice overload
    time.sleep(1.5)

cap.release()
cv2.destroyAllWindows()
print("Detection completed successfully")

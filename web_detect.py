from flask import Flask, render_template, Response, jsonify, request
import cv2
import torch
import threading
import time
import math
from datetime import datetime
from collections import deque
from modules.chatbot.app import chatbot_bp

app = Flask(__name__, template_folder='templates')

# Print template folder info
import os
print(f"📁 Main app template folder: {app.template_folder}")
print(f"📁 Main app template folder exists: {os.path.exists(app.template_folder)}")
print(f"📁 Current working directory: {os.getcwd()}")

# Register chatbot blueprint
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
print("🤖 Chatbot blueprint registered with /chatbot prefix")

# Print all registered routes for debugging
print("📋 Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint} ({rule.methods})")

# Global variables for camera and detection
camera = None
model = None
current_detections = []
detection_lock = threading.Lock()
# Store last 5 detection sets
detection_history = deque(maxlen=5)
# Sequential detection control
sequential_mode = True
speech_in_progress = False
detection_ready = False
# Camera state tracking
camera_active = False
# Distance estimation constants
FOCAL_LENGTH = 800  # Estimated focal length for typical webcam
KNOWN_OBJECT_WIDTHS = {
    'person': 1.5,  # Average shoulder width in feet
    'car': 6.0,     # Average car width in feet
    'bicycle': 1.8, # Average bicycle width in feet
    'chair': 1.5,   # Average chair width in feet
    'bottle': 0.25, # Average bottle width in feet
    'cup': 0.15,    # Average cup width in feet
    'laptop': 1.0,  # Average laptop width in feet
    'cell phone': 0.25, # Average phone width in feet
    'book': 0.5,    # Average book width in feet
    'backpack': 1.0 # Average backpack width in feet
}

def estimate_distance(object_width_in_pixels, object_name):
    """
    Estimate distance in feet using the formula:
    Distance = (Known_Width * Focal_Length) / Perceived_Width
    """
    if object_name in KNOWN_OBJECT_WIDTHS:
        known_width = KNOWN_OBJECT_WIDTHS[object_name]
        distance = (known_width * FOCAL_LENGTH) / object_width_in_pixels
        return max(0.5, min(distance, 50))  # Clamp between 0.5 and 50 feet
    else:
        # For unknown objects, use average width and apply a scaling factor
        estimated_width = 2.0  # Default 2 feet for unknown objects
        distance = (estimated_width * FOCAL_LENGTH) / object_width_in_pixels
        return max(0.5, min(distance, 50))

def initialize_camera():
    global camera, model, camera_active
    print("Initializing camera and model...")
    
    # Load YOLOv5 model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    
    # Initialize camera
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Camera not opened")
        camera_active = False
        return False
    
    # Set camera active state
    camera_active = True
    
    # Get camera dimensions for calibration
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"📷 Camera resolution: {width}x{height}")
    
    print("✅ Camera and model initialized successfully")
    return True

def detect_objects():
    global current_detections, camera, model, detection_history, sequential_mode, speech_in_progress, detection_ready, camera_active
    
    while True:
        # Stop detection if camera is not active
        if not camera_active or camera is None or model is None:
            time.sleep(0.1)
            continue
        
        # In sequential mode, wait for speech to complete before next detection
        if sequential_mode and speech_in_progress:
            time.sleep(0.1)
            continue
            
        ret, frame = camera.read()
        if not ret:
            time.sleep(0.1)
            continue
        
        # Run detection
        results = model(frame)
        
        # Get detected objects
        detections = results.pandas().xyxy[0]
        
        # Process detections
        detected_objects = []
        for idx, row in detections.iterrows():
            # Calculate object width in pixels
            object_width_pixels = float(row['xmax']) - float(row['xmin'])
            
            # Estimate distance
            distance = estimate_distance(object_width_pixels, row['name'])
            
            detected_objects.append({
                'name': row['name'],
                'confidence': float(row['confidence']),
                'bbox': [float(row['xmin']), float(row['ymin']), float(row['xmax']), float(row['ymax'])],
                'distance': round(distance, 1),
                'width_pixels': round(object_width_pixels, 0)
            })
        
        # Update global detections
        with detection_lock:
            current_detections = detected_objects
            detection_ready = True
            
            # Add to history if objects detected and different from last
            if detected_objects:
                # Create unique object list
                unique_objects = {}
                for obj in detected_objects:
                    name = obj['name']
                    if name not in unique_objects:
                        unique_objects[name] = 0
                    unique_objects[name] += 1
                
                # Create summary
                summary = ""
                for name, count in unique_objects.items():
                    if count == 1:
                        summary += f"{name}, "
                    else:
                        summary += f"{count} {name}s, "
                summary = summary.rstrip(", ")
                
                # Add to history if different from last detection
                if not detection_history or detection_history[-1]['summary'] != summary:
                    detection_history.append({
                        'objects': detected_objects.copy(),
                        'summary': summary,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
        
        # In sequential mode, wait longer between detections
        if sequential_mode:
            time.sleep(2.0)  # Wait 2 seconds before next detection
        else:
            time.sleep(0.1)  # Small delay to prevent overload

def generate_frames():
    global camera, model, current_detections, camera_active
    
    while True:
        if not camera_active or camera is None:
            time.sleep(0.1)
            continue
            
        ret, frame = camera.read()
        if not ret:
            break
        
        # Get current detections
        with detection_lock:
            detections = current_detections.copy()
        
        # Draw bounding boxes and labels
        for obj in detections:
            x1, y1, x2, y2 = map(int, obj['bbox'])
            confidence = obj['confidence']
            name = obj['name']
            distance = obj.get('distance', 0)
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label with distance
            label = f"{name} {confidence:.2f} {distance}ft"
            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add object count
        cv2.putText(frame, f"Objects: {len(detections)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detections')
def get_detections():
    with detection_lock:
        detections = current_detections.copy()
        history = list(detection_history)
        ready = detection_ready
    
    # Create text summary
    if detections:
        unique_objects = {}
        for obj in detections:
            name = obj['name']
            if name not in unique_objects:
                unique_objects[name] = 0
            unique_objects[name] += 1
        
        summary = ""
        for name, count in unique_objects.items():
            if count == 1:
                summary += f"{name}, "
            else:
                summary += f"{count} {name}s, "
        summary = summary.rstrip(", ")
    else:
        summary = "No objects detected"
    
    return jsonify({
        'detections': detections,
        'summary': summary,
        'count': len(detections),
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'history': history,  # Send last 5 detection sets
        'ready': ready,  # Indicate if new detection is ready
        'sequential_mode': sequential_mode
    })

@app.route('/speech_status', methods=['POST'])
def set_speech_status():
    global speech_in_progress, detection_ready
    data = request.get_json()
    speech_in_progress = data.get('speaking', False)
    
    # Reset detection ready flag when speech starts
    if speech_in_progress:
        with detection_lock:
            detection_ready = False
    
    return jsonify({'status': 'ok'})

@app.route('/camera_status', methods=['GET'])
def camera_status():
    """Get current camera status"""
    global camera, camera_active
    return jsonify({
        'camera_on': camera_active and (camera is not None and camera.isOpened() if camera else False)
    })

@app.route('/camera_toggle', methods=['POST'])
def camera_toggle():
    """Toggle camera on/off"""
    global camera, camera_active
    
    try:
        if camera is None or not camera.isOpened() or not camera_active:
            # Turn camera on
            if initialize_camera():
                return jsonify({'status': 'success', 'camera_on': True})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to initialize camera'}), 500
        else:
            # Turn camera off
            camera_active = False
            if camera and camera.isOpened():
                camera.release()
            camera = None
            
            # Clear detection data
            with detection_lock:
                current_detections.clear()
                detection_history.clear()
            
            return jsonify({'status': 'success', 'camera_on': False})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    if initialize_camera():
        # Start detection thread
        detection_thread = threading.Thread(target=detect_objects, daemon=True)
        detection_thread.start()
        
        print("🌐 Starting web interface...")
        print("📊 Open http://localhost:5000 in your browser")
        print("🎯 Live object detection with continuous updates")
        print("🔊 Voice announcements enabled")
        print("📝 Showing last 5 detections")
        print("🛑 Press Ctrl+C to stop")
        
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ Failed to initialize camera")

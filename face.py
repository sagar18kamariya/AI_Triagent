"""
Face detection using OpenCV Haarcascade frontal face detector.
Optimized for real-time performance.
"""

import cv2
import numpy as np
import os

# Global cascade classifier for performance (load once)
_FACE_CASCADE = None

def _load_cascade():
    """
    Load the Haarcascade frontal face classifier.
    Returns the classifier object.
    """
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        # Try to load from OpenCV's built-in data
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            # Fallback to local file or alternative path
            cascade_path = 'haarcascade_frontalface_default.xml'
            if not os.path.exists(cascade_path):
                raise FileNotFoundError(
                    "Haarcascade XML file not found. "
                    "Please ensure 'haarcascade_frontalface_default.xml' is in the working directory "
                    "or OpenCV is properly installed with its data files."
                )
        _FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
        if _FACE_CASCADE.empty():
            raise RuntimeError("Failed to load cascade classifier. Check the XML file.")
    return _FACE_CASCADE

def detect_face(frame):
    """
    Detect a face in the given image frame.

    Parameters:
    -----------
    frame : numpy.ndarray
        Input image frame (BGR color format).

    Returns:
    --------
    tuple or None
        If a face is detected, returns (x, y, w, h) bounding box of the first face.
        If no face is detected, returns None.
    """
    # Convert frame to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Load cascade classifier (cached)
    face_cascade = _load_cascade()
    
    # Detect faces with optimized parameters for real-time performance
    # scaleFactor: Parameter specifying how much the image size is reduced at each image scale
    # minNeighbors: Parameter specifying how many neighbors each candidate rectangle should have to retain it
    # minSize: Minimum possible object size (smaller objects are ignored)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,      # Slight scaling for speed
        minNeighbors=5,       # Balanced between false positives and detection rate
        minSize=(30, 30),     # Minimum face size (pixels)
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Return first face or None
    if len(faces) > 0:
        # Return the first detected face (largest if we sort by area)
        # For real-time, we can just take the first one
        x, y, w, h = faces[0]
        return (x, y, w, h)
    return None

def detect_faces(frame, max_faces=None):
    """
    Detect multiple faces in the given image frame.

    Parameters:
    -----------
    frame : numpy.ndarray
        Input image frame (BGR color format).
    max_faces : int or None
        Maximum number of faces to return. If None, return all detected faces.

    Returns:
    --------
    list of tuples
        List of (x, y, w, h) bounding boxes for each detected face.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = _load_cascade()
    
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    if max_faces is not None and len(faces) > max_faces:
        faces = faces[:max_faces]
    
    return [(x, y, w, h) for (x, y, w, h) in faces]

def draw_faces(frame, faces, color=(0, 255, 0), thickness=2):
    """
    Draw bounding boxes around detected faces on the frame.

    Parameters:
    -----------
    frame : numpy.ndarray
        Input image frame (will be modified in place).
    faces : list of tuples
        List of (x, y, w, h) bounding boxes.
    color : tuple
        BGR color for rectangles (default: green).
    thickness : int
        Thickness of rectangle lines.

    Returns:
    --------
    numpy.ndarray
        Frame with drawn rectangles.
    """
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    return frame

def main():
    """
    Example usage: Capture from webcam and detect faces in real-time.
    """
    # Check if OpenCV is available
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return
        
        print("Starting face detection. Press 'q' to quit.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            
            # Detect face
            face_box = detect_face(frame)
            
            if face_box is not None:
                x, y, w, h = face_box
                # Draw rectangle
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Display coordinates
                cv2.putText(frame, f"Face: {x},{y}", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Display FPS (simple calculation)
            cv2.putText(frame, "Press 'q' to quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Face Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Error in main: {e}")
        print("Make sure OpenCV is installed and webcam is available.")

if __name__ == "__main__":
    main()
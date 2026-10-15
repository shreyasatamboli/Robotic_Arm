#!/usr/bin/env python3
"""
Example: Test object detection without the robotic arm

This example demonstrates the vision system in isolation.
Use this to test and tune color/shape detection parameters.
"""

import cv2
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'software'))

from vision.object_detector import ObjectDetector


def main():
    """Test object detection with live camera feed"""
    
    print("=" * 50)
    print("  Object Detection Test")
    print("=" * 50)
    print()
    print("Controls:")
    print("  q - Quit")
    print("  s - Save screenshot")
    print()
    
    # Initialize detector
    detector = ObjectDetector()
    
    # Open camera
    camera = cv2.VideoCapture(2)
    if not camera.isOpened():
        print("Error: Could not open camera")
        return 1
    
    # Set resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    screenshot_count = 0
    
    try:
        while True:
            # Capture frame
            ret, frame = camera.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Detect objects
            objects = detector.detect_objects(frame)
            
            # Draw detections
            display_frame = detector.draw_detections(frame, objects)
            
            # Add info text
            info_text = f"Objects detected: {len(objects)}"
            cv2.putText(display_frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show detected objects info
            y_offset = 60
            for i, obj in enumerate(objects):
                text = f"{i+1}. {obj['color']} {obj['shape']} at {obj['centroid']}"
                cv2.putText(display_frame, text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_offset += 25
            
            # Display
            cv2.imshow('Object Detection Test', display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f'screenshot_{screenshot_count:03d}.png'
                cv2.imwrite(filename, display_frame)
                print(f"Saved: {filename}")
                screenshot_count += 1
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
    
    print("Test complete")
    return 0


if __name__ == '__main__':
    sys.exit(main())

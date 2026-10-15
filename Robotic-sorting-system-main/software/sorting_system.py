"""
Main Sorting System Module

Coordinates the vision system and robotic arm to sort objects.
"""

import cv2
import time
import numpy as np
from typing import Dict, List

from vision.object_detector import ObjectDetector
from control.arm_controller import RoboticArmController


class SortingSystem:
    """Main sorting system that coordinates vision and arm control"""
    
    def __init__(self, arm_port: str = '/dev/ttyUSB0', camera_id: int = 0):
        """
        Initialize the sorting system
        
        Args:
            arm_port: Serial port for robotic arm
            camera_id: Camera device ID
        """
        self.detector = ObjectDetector()
        self.arm = RoboticArmController(port=arm_port)
        self.camera_id = camera_id
        self.camera = None
        
        # Define sorting zones (in mm from robot base)
        self.sorting_zones = {
            'red': (200, 100, 0),
            'green': (200, -100, 0),
            'blue': (-200, 100, 0),
            'yellow': (-200, -100, 0),
            'circle': (150, 150, 0),
            'square': (150, -150, 0),
            'triangle': (-150, 150, 0),
            'rectangle': (-150, -150, 0)
        }
        
        # Camera calibration parameters
        self.camera_height = 400  # mm above work surface
        self.pixels_per_mm = 2.0  # Calibration factor
        
        # Pickup zone (center of camera view)
        self.pickup_zone_center = (320, 240)  # Default for 640x480 camera
        
    def initialize(self) -> bool:
        """Initialize all system components"""
        
        print("Initializing Robotic Arm Sorting System...")
        
        # Connect to robotic arm
        if not self.arm.connect():
            print("Failed to connect to robotic arm")
            return False
        
        # Move to home position
        print("Moving to home position...")
        if not self.arm.move_to_home():
            print("Failed to move to home position")
            return False
        
        # Initialize camera
        print("Initializing camera...")
        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isOpened():
            print("Failed to open camera")
            return False
        
        # Set camera resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Update pickup zone center
        width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.pickup_zone_center = (width // 2, height // 2)
        
        print("System initialized successfully!")
        return True
    
    def shutdown(self):
        """Shutdown all system components"""
        print("Shutting down system...")
        
        if self.arm.connected:
            self.arm.move_to_home()
            self.arm.disconnect()
        
        if self.camera is not None:
            self.camera.release()
        
        cv2.destroyAllWindows()
        print("System shutdown complete")
    
    def pixel_to_world(self, pixel_x: int, pixel_y: int) -> tuple:
        """
        Convert pixel coordinates to world coordinates
        
        Args:
            pixel_x, pixel_y: Pixel coordinates in image
            
        Returns:
            (x, y, z) world coordinates in mm
        """
        # Center the coordinates
        dx = pixel_x - self.pickup_zone_center[0]
        dy = self.pickup_zone_center[1] - pixel_y  # Flip Y axis
        
        # Convert to mm
        x = dx / self.pixels_per_mm
        y = dy / self.pixels_per_mm
        z = 0  # Object on work surface
        
        return (x, y, z)
    
    def sort_by_color(self, object_info: Dict) -> tuple:
        """Determine target zone based on object color"""
        color = object_info['color']
        if color in self.sorting_zones:
            return self.sorting_zones[color]
        return self.sorting_zones['red']  # Default zone
    
    def sort_by_shape(self, object_info: Dict) -> tuple:
        """Determine target zone based on object shape"""
        shape = object_info['shape']
        if shape in self.sorting_zones:
            return self.sorting_zones[shape]
        return self.sorting_zones['circle']  # Default zone
    
    def sort_objects(self, sort_mode: str = 'color', max_objects: int = 10, 
                     display: bool = True) -> int:
        """
        Main sorting routine
        
        Args:
            sort_mode: 'color' or 'shape'
            max_objects: Maximum number of objects to sort
            display: Show camera feed with detections
            
        Returns:
            Number of objects sorted
        """
        if not self.arm.connected or self.camera is None:
            print("System not initialized")
            return 0
        
        sorted_count = 0
        
        print(f"Starting sorting mode: {sort_mode}")
        print("Press 'q' to quit, 's' to skip current object")
        
        while sorted_count < max_objects:
            # Capture frame
            ret, frame = self.camera.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Detect objects
            objects = self.detector.detect_objects(frame)
            
            # Draw detections
            if display:
                display_frame = self.detector.draw_detections(frame, objects)
                cv2.imshow('Robotic Arm Sorting System', display_frame)
            
            # Process keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                continue
            
            # Sort the first detected object
            if len(objects) > 0:
                obj = objects[0]
                
                print(f"\nDetected: {obj['color']} {obj['shape']}")
                
                # Get object position in world coordinates
                cx, cy = obj['centroid']
                pickup_pos = self.pixel_to_world(cx, cy)
                
                print(f"Pickup position: {pickup_pos}")
                
                # Determine target zone
                if sort_mode == 'color':
                    target_pos = self.sort_by_color(obj)
                else:
                    target_pos = self.sort_by_shape(obj)
                
                print(f"Target position: {target_pos}")
                
                # Execute pick and place
                print("Picking object...")
                if self.arm.pick_object(*pickup_pos):
                    print("Placing object...")
                    if self.arm.place_object(*target_pos):
                        sorted_count += 1
                        print(f"Successfully sorted object {sorted_count}/{max_objects}")
                    else:
                        print("Failed to place object")
                else:
                    print("Failed to pick object")
                
                # Return to home position
                self.arm.move_to_home()
                time.sleep(1)
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.1)
        
        print(f"\nSorting complete! Sorted {sorted_count} objects.")
        return sorted_count
    
    def calibrate_camera(self, known_width: float = None) -> bool:
        """
        Interactive camera calibration routine
        
        Args:
            known_width: Known width of reference object in mm (if None, will prompt)
            
        Returns:
            True if calibration successful
        """
        print("\n=== Camera Calibration ===")
        print("Place a reference object of known size in view")
        print("Press 'c' to capture, 'q' to quit")
        
        while True:
            ret, frame = self.camera.read()
            if not ret:
                return False
            
            cv2.imshow('Calibration', frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                return False
            elif key == ord('c'):
                # Detect reference object
                objects = self.detector.detect_objects(frame)
                if len(objects) > 0:
                    obj = objects[0]
                    # Calculate pixels per mm based on known object size
                    # This is simplified - real calibration would be more sophisticated
                    bbox = obj['bbox']
                    pixel_width = bbox[2]
                    
                    if known_width is None:
                        known_width = float(input("Enter object width in mm: "))
                    
                    self.pixels_per_mm = pixel_width / known_width
                    
                    print(f"Calibration complete: {self.pixels_per_mm:.2f} pixels/mm")
                    cv2.destroyWindow('Calibration')
                    return True
                else:
                    print("No object detected, try again")
        
        return False
    
    def run_interactive_mode(self):
        """Run system in interactive mode for testing"""
        print("\n=== Interactive Mode ===")
        print("Commands:")
        print("  1 - Sort by color")
        print("  2 - Sort by shape")
        print("  c - Calibrate camera")
        print("  h - Home position")
        print("  q - Quit")
        
        while True:
            ret, frame = self.camera.read()
            if not ret:
                break
            
            objects = self.detector.detect_objects(frame)
            display_frame = self.detector.draw_detections(frame, objects)
            
            cv2.putText(display_frame, f"Objects detected: {len(objects)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Interactive Mode', display_frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('1'):
                cv2.destroyWindow('Interactive Mode')
                self.sort_objects(sort_mode='color', max_objects=5)
            elif key == ord('2'):
                cv2.destroyWindow('Interactive Mode')
                self.sort_objects(sort_mode='shape', max_objects=5)
            elif key == ord('c'):
                cv2.destroyWindow('Interactive Mode')
                self.calibrate_camera()
            elif key == ord('h'):
                self.arm.move_to_home()

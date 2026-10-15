"""
Object Detection Module for Robotic Arm Sorting System

This module uses OpenCV to detect and classify objects based on:
- Color (red, green, blue, yellow)
- Shape (circle, square, triangle, rectangle)
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict


class ObjectDetector:
    """Detects and classifies objects using computer vision"""
    
    def __init__(self):
        # Define color ranges in HSV color space
        self.color_ranges = {
            'red': [(0, 100, 100), (10, 255, 255), (160, 100, 100), (180, 255, 255)],
            'green': [(40, 50, 50), (80, 255, 255)],
            'blue': [(90, 50, 50), (130, 255, 255)],
            'yellow': [(20, 100, 100), (30, 255, 255)]
        }
        
        self.min_area = 500  # Minimum contour area to consider
        self.max_area = 50000  # Maximum contour area to consider
        
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in the frame
        
        Args:
            frame: BGR image from camera
            
        Returns:
            List of detected objects with properties
        """
        objects = []
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detect objects for each color
        for color_name, ranges in self.color_ranges.items():
            if color_name == 'red':
                # Red wraps around in HSV, need two ranges
                mask1 = cv2.inRange(hsv, ranges[0], ranges[1])
                mask2 = cv2.inRange(hsv, ranges[2], ranges[3])
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                mask = cv2.inRange(hsv, ranges[0], ranges[1])
            
            # Clean up the mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if self.min_area < area < self.max_area:
                    # Get object properties
                    obj = self._analyze_contour(contour, color_name, frame)
                    if obj:
                        objects.append(obj)
        
        return objects
    
    def _analyze_contour(self, contour, color: str, frame: np.ndarray) -> Dict:
        """Analyze a contour to determine shape and position"""
        
        # Calculate moments for centroid
        M = cv2.moments(contour)
        if M['m00'] == 0:
            return None
            
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        
        # Approximate the contour to detect shape
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
        
        # Determine shape
        vertices = len(approx)
        shape = self._classify_shape(vertices, contour)
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        return {
            'color': color,
            'shape': shape,
            'centroid': (cx, cy),
            'bbox': (x, y, w, h),
            'area': cv2.contourArea(contour),
            'contour': contour
        }
    
    def _classify_shape(self, vertices: int, contour) -> str:
        """Classify shape based on number of vertices and circularity"""
        
        if vertices == 3:
            return 'triangle'
        elif vertices == 4:
            # Check if it's square-like
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 0.8 <= aspect_ratio <= 1.2:
                return 'square'
            else:
                return 'rectangle'
        elif vertices > 6:
            # Check circularity
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if circularity > 0.7:
                    return 'circle'
        
        return 'unknown'
    
    def draw_detections(self, frame: np.ndarray, objects: List[Dict]) -> np.ndarray:
        """Draw detected objects on the frame"""
        
        output = frame.copy()
        
        for obj in objects:
            # Draw contour
            cv2.drawContours(output, [obj['contour']], -1, (0, 255, 0), 2)
            
            # Draw centroid
            cx, cy = obj['centroid']
            cv2.circle(output, (cx, cy), 5, (0, 0, 255), -1)
            
            # Draw bounding box
            x, y, w, h = obj['bbox']
            cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Add label
            label = f"{obj['color']} {obj['shape']}"
            cv2.putText(output, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return output
    
    def get_pixel_to_world_transform(self, camera_height: float, 
                                     focal_length: float) -> np.ndarray:
        """
        Calculate transformation matrix from pixel coordinates to world coordinates
        
        Args:
            camera_height: Height of camera above work surface (mm)
            focal_length: Camera focal length in pixels
            
        Returns:
            Transformation matrix
        """
        # Simplified perspective transform
        # In a real system, this would use camera calibration
        scale = camera_height / focal_length
        return np.array([[scale, 0, 0],
                        [0, scale, 0],
                        [0, 0, 1]])

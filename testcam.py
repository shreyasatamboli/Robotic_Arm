"""
Object Detection Module for Robotic Arm Sorting System (standalone version)

This module uses OpenCV to detect and classify objects based on:
- Color (red, green, blue, yellow)
- Shape (circle, square, triangle, rectangle)

Run it directly to see live detections from a webcam in a window:

    python object_detector_standalone.py
    python object_detector_standalone.py --camera 1 --width 1280 --height 720
    python object_detector_standalone.py --lock

Press q or Esc in the window to quit.

Requires: pip install opencv-python numpy
"""

import argparse
import sys
import time
from typing import List, Tuple, Dict

import cv2
import numpy as np


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


# ---------------------------------------------------------------------------
# Standalone runner: shows detections in a window (replaces any serial output)
# ---------------------------------------------------------------------------

WINDOW_NAME = "Object Detector"
PANEL_WIDTH = 450
LINE_H = 22
CAMERA_HEIGHT_CM = 61.0  # Assumed camera height in cm
SCALE_FACTOR = 0.5     # Calibration factor to scale down calculated size by 2


def add_info_panel(frame: np.ndarray, objects: List[Dict], fps: float, transform_matrix: np.ndarray) -> np.ndarray:
    """Return the frame with a fixed-width side panel listing every detection,
    including calculated real-world physical dimensions (length and width in cm)."""
    h = frame.shape[0]
    panel = np.zeros((h, PANEL_WIDTH, 3), np.uint8)

    max_rows = max((h - 10) // LINE_H - 2, 1)
    lines = [f"Objects: {len(objects)}   FPS: {fps:.1f}", f"Cam Height: {CAMERA_HEIGHT_CM} cm  |  q / Esc to quit", ""]

    for i, obj in enumerate(objects[:max_rows], start=1):
        cx, cy = obj['centroid']
        _, _, w_px, h_px = obj['bbox']

        # Calculate physical dimensions using pixel-to-world transform matrix
        world_dim = transform_matrix @ np.array([w_px, h_px, 1.0])
        width_cm = world_dim[0]
        length_cm = world_dim[1]

        # Store calculated dimensions back in object dictionary
        obj['width_cm'] = width_cm
        obj['length_cm'] = length_cm

        lines.append(
            f"{i}. {obj['color']} {obj['shape']}  {length_cm:.1f}x{width_cm:.1f}cm  px=({cx},{cy})"
        )

    if len(objects) > max_rows:
        lines.append(f"... and {len(objects) - max_rows} more")

    for i, text in enumerate(lines):
        cv2.putText(panel, text, (8, 22 + i * LINE_H),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    return np.hstack([frame, panel])


def lock_camera(cap: cv2.VideoCapture) -> None:
    """Try to disable autofocus and auto white balance so colors stay stable.
    Not every driver honors this; auto-exposure is backend-specific, so it is
    left alone here."""
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_AUTO_WB, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Live color/shape detection window")
    parser.add_argument("--camera", type=int, default=2, help="camera index (default 0)")
    parser.add_argument("--width", type=int, default=1280, help="capture width")
    parser.add_argument("--height", type=int, default=720, help="capture height")
    parser.add_argument("--focal-length", type=float, default=800.0,
                        help="camera focal length in pixels (default 800.0)")
    parser.add_argument("--lock", action="store_true",
                        help="try to disable autofocus and auto white balance")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Could not open camera {args.camera}. Try --camera 1 or check that "
              f"no other program is using it.", file=sys.stderr)
        return 1

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    if args.lock:
        lock_camera(cap)

    detector = ObjectDetector()

    # Get raw transform matrix and apply 0.5 scale factor to scale dimensions down by 2
    raw_transform = detector.get_pixel_to_world_transform(
        camera_height=CAMERA_HEIGHT_CM,
        focal_length=args.focal_length
    )
    transform_matrix = raw_transform * SCALE_FACTOR

    fps = 0.0
    last = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Failed to read a frame from the camera.", file=sys.stderr)
                break

            objects = detector.detect_objects(frame)
            output = detector.draw_detections(frame, objects)

            # Draw calculated length and width on the video frame overlay
            for obj in objects:
                x, y, w_px, h_px = obj['bbox']
                world_dim = transform_matrix @ np.array([w_px, h_px, 1.0])
                w_cm, l_cm = world_dim[0], world_dim[1]
                dim_label = f"{l_cm:.1f}x{w_cm:.1f}cm"
                cv2.putText(output, dim_label, (x, y + h_px + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            # Smoothed FPS
            now = time.time()
            inst = 1.0 / max(now - last, 1e-6)
            fps = inst if fps == 0.0 else 0.9 * fps + 0.1 * inst
            last = now

            output = add_info_panel(output, objects, fps, transform_matrix)
            cv2.imshow(WINDOW_NAME, output)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):  # q or Esc
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
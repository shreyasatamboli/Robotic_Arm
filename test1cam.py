"""
Object Detection Module for Robotic Arm Sorting System (standalone version)

This module uses OpenCV to detect and classify objects based on:
- Color (red, green, blue, yellow)
- Shape (circle, square, triangle, rectangle)

Run it directly to see live detections from a webcam in a window, with each
object's length, width and position in centimetres on your workspace board:

    python object_detector_standalone.py                 # first run: click the 4 board corners
    python object_detector_standalone.py --recalibrate   # redo the corner clicks
    python object_detector_standalone.py --board-length 50 --board-width 27.5

Keys: c = recalibrate, q / Esc = quit.

Requires: pip install opencv-python numpy
"""

import argparse
import json
import sys
import time
from typing import List, Tuple, Dict, Optional

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
# Standalone runner: live detection with real-world (cm) measurements
#
# Pixels are converted to centimetres with a homography computed from the four
# corners of the taped board, whose real size is known. This replaces the
# camera-height / focal-length estimate: it needs neither, and it also corrects
# for a camera that is not perfectly square to the table.
# ---------------------------------------------------------------------------

WINDOW_NAME = "Object Detector"
PANEL_WIDTH = 450
LINE_H = 22
FONT = cv2.FONT_HERSHEY_SIMPLEX
DEFAULT_CALIB_FILE = "workspace_calibration.json"


# ---- calibration helpers ---------------------------------------------------

def save_calibration(path: str, frame_size: Tuple[int, int],
                     board_cm: Tuple[float, float], corners_px: np.ndarray) -> None:
    data = {"frame_size": list(frame_size), "board_cm": list(board_cm),
            "corners_px": np.asarray(corners_px).tolist()}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_calibration(path: str, frame_size: Tuple[int, int],
                     board_cm: Tuple[float, float]) -> Optional[np.ndarray]:
    """Return saved corners if the file matches this resolution and board size."""
    try:
        with open(path) as f:
            data = json.load(f)
        if (tuple(data["frame_size"]) == tuple(frame_size)
                and np.allclose(data["board_cm"], board_cm)):
            return np.array(data["corners_px"], np.float32)
    except (OSError, ValueError, KeyError):
        pass
    return None


def build_homography(corners_px: np.ndarray, board_cm: Tuple[float, float]):
    """Homography from image pixels to board centimetres (and its inverse).
    Corner 1 is the board origin, corner 1->2 is the x axis (board length)."""
    L, W = board_cm
    dst = np.array([[0, 0], [L, 0], [L, W], [0, W]], np.float32)
    H = cv2.getPerspectiveTransform(np.asarray(corners_px, np.float32), dst)
    return H, np.linalg.inv(H)


def transform_points(H: np.ndarray, pts) -> np.ndarray:
    pts = np.asarray(pts, np.float32).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(pts, H).reshape(-1, 2)


def describe_calibration(corners: np.ndarray,
                         board_cm: Tuple[float, float]) -> Tuple[str, str]:
    """Report the cm-per-pixel along each board side and flag inconsistencies.
    Returns (full console text, short line for the side panel)."""
    L, W = board_cm
    side = lambda a, b: float(np.linalg.norm(corners[a] - corners[b]))
    s_long = L / ((side(0, 1) + side(3, 2)) / 2)
    s_short = W / ((side(1, 2) + side(0, 3)) / 2)
    diff = abs(s_long - s_short) / ((s_long + s_short) / 2) * 100
    text = (f"Calibrated: {s_long:.4f} cm/px along the {L:g} cm side, "
            f"{s_short:.4f} cm/px along the {W:g} cm side")
    if diff > 5:
        text += (f"\nWARNING: the two scales differ by {diff:.1f}%. Re-click the "
                 f"corners (press c) or check the board dimensions.")
    return text, f"Scale: {s_long:.4f} / {s_short:.4f} cm/px"


def pick_corners(frame: np.ndarray, board_cm: Tuple[float, float]) -> Optional[np.ndarray]:
    """Show a still frame; the user clicks the 4 board corners in order.
    Returns a 4x2 float32 array of pixel coordinates, or None if cancelled."""
    L, W = board_cm
    prompts = [
        f"Click corner 1 (start of a {L:g} cm side)",
        f"Click corner 2 (end of that {L:g} cm side)",
        f"Click corner 3 (end of the {W:g} cm side)",
        "Click corner 4 (the last corner)",
    ]
    fh, fw = frame.shape[:2]
    points: List[Tuple[int, int]] = []

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4 and x < fw and y < fh:
            points.append((x, y))

    cv2.setMouseCallback(WINDOW_NAME, on_mouse)
    message = ""
    result = None
    while True:
        canvas = frame.copy()
        for i, p in enumerate(points, start=1):
            cv2.circle(canvas, p, 5, (0, 0, 255), -1)
            cv2.putText(canvas, str(i), (p[0] + 8, p[1] - 8), FONT, 0.7,
                        (0, 0, 255), 2, cv2.LINE_AA)
        if len(points) > 1:
            cv2.polylines(canvas, [np.array(points, np.int32).reshape(-1, 1, 2)],
                          len(points) == 4, (0, 255, 255), 1)

        lines = ["CALIBRATION", prompts[len(points)] if len(points) < 4
                 else "Enter = accept", "u = undo   r = reset   Esc = cancel", ""]
        if message:
            lines.append(message)
        cv2.imshow(WINDOW_NAME, add_info_panel(canvas, lines))

        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            break
        elif key == ord('u') and points:
            points.pop()
            message = ""
        elif key == ord('r'):
            points.clear()
            message = ""
        elif key in (13, 10, 32) and len(points) == 4:
            pts = np.array(points, np.float32)
            if cv2.isContourConvex(pts.reshape(-1, 1, 2)):
                result = pts
                break
            message = "Corners are not in order. Press r and click around the board."

    cv2.setMouseCallback(WINDOW_NAME, lambda *args: None)
    return result


# ---- measurement helpers ---------------------------------------------------

def measure_object_cm(contour, H: np.ndarray) -> Dict:
    """Map the contour onto the board plane (cm) and fit the minimum-area
    rotated rectangle there. Length = long side, width = short side."""
    pts_cm = transform_points(H, contour)
    rect = cv2.minAreaRect(pts_cm)
    w, h = rect[1]
    return {'length_cm': max(w, h), 'width_cm': min(w, h), 'rect_cm': rect}


def add_info_panel(frame: np.ndarray, lines: List[str]) -> np.ndarray:
    """Return the frame with a fixed-width side panel of text lines.
    The panel sits beside the image, so it never covers the workspace."""
    h = frame.shape[0]
    panel = np.zeros((h, PANEL_WIDTH, 3), np.uint8)
    max_rows = max((h - 10) // LINE_H, 1)
    for i, text in enumerate(lines[:max_rows]):
        cv2.putText(panel, text, (8, 22 + i * LINE_H), FONT, 0.45,
                    (255, 255, 255), 1, cv2.LINE_AA)
    return np.hstack([frame, panel])


def lock_camera(cap: cv2.VideoCapture) -> None:
    """Try to disable autofocus and auto white balance so colors stay stable.
    Not every driver honors this; auto-exposure is backend-specific, so it is
    left alone here."""
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_AUTO_WB, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Live color/shape detection window")
    parser.add_argument("--camera", type=int, default=2, help="camera index (default 2)")
    parser.add_argument("--width", type=int, default=1280, help="capture width")
    parser.add_argument("--height", type=int, default=720, help="capture height")
    parser.add_argument("--lock", action="store_true",
                        help="try to disable autofocus and auto white balance")
    parser.add_argument("--board-length", type=float, default=50.0,
                        help="long side of the taped board in cm (default 50)")
    parser.add_argument("--board-width", type=float, default=27.5,
                        help="short side of the taped board in cm (default 27.5)")
    parser.add_argument("--calib-file", default=DEFAULT_CALIB_FILE,
                        help="where the corner calibration is saved/loaded")
    parser.add_argument("--recalibrate", action="store_true",
                        help="ignore any saved calibration and click the corners again")
    parser.add_argument("--edge-margin", type=float, default=30.0,
                        help="ignore detections whose centre is closer than this many "
                             "pixels to the board edge (this removes the blue tape)")
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

    board_cm = (args.board_length, args.board_width)
    detector = ObjectDetector()
    cv2.namedWindow(WINDOW_NAME)

    try:
        # Let auto-exposure settle, then use the real frame size
        ok, frame = False, None
        for _ in range(10):
            ok, frame = cap.read()
        if not ok or frame is None:
            print("Failed to read a frame from the camera.", file=sys.stderr)
            return 1
        frame_size = (frame.shape[1], frame.shape[0])

        corners = None if args.recalibrate else load_calibration(
            args.calib_file, frame_size, board_cm)
        if corners is None:
            corners = pick_corners(frame, board_cm)
            if corners is None:
                print("Calibration cancelled.", file=sys.stderr)
                return 1
            save_calibration(args.calib_file, frame_size, board_cm, corners)

        H, H_inv = build_homography(corners, board_cm)
        calib_text, scale_line = describe_calibration(corners, board_cm)
        print(calib_text)

        fps = 0.0
        last = time.time()

        while True:
            ok, frame = cap.read()
            if not ok:
                print("Failed to read a frame from the camera.", file=sys.stderr)
                break

            # Keep only objects inside the board (this also drops the blue tape,
            # whose centre lies on the board edge)
            quad = corners.reshape(-1, 1, 2).astype(np.float32)
            objects = [
                o for o in detector.detect_objects(frame)
                if cv2.pointPolygonTest(quad, (float(o['centroid'][0]),
                                               float(o['centroid'][1])), True)
                >= args.edge_margin
            ]

            output = detector.draw_detections(frame, objects)
            cv2.polylines(output, [corners.astype(np.int32).reshape(-1, 1, 2)],
                          True, (255, 255, 0), 1)

            lines = [f"Objects: {len(objects)}   FPS: {fps:.1f}", scale_line,
                     "c = recalibrate  |  q / Esc = quit", ""]
            for i, obj in enumerate(objects, start=1):
                m = measure_object_cm(obj['contour'], H)
                bx, by = transform_points(H, [obj['centroid']])[0]

                # Store results back on the object
                obj['length_cm'] = m['length_cm']
                obj['width_cm'] = m['width_cm']
                obj['board_xy_cm'] = (float(bx), float(by))

                # Draw the fitted rectangle (mapped back into the image)
                box_px = transform_points(H_inv, cv2.boxPoints(m['rect_cm']))
                cv2.polylines(output, [box_px.astype(np.int32).reshape(-1, 1, 2)],
                              True, (255, 0, 255), 2)
                x, y, w_px, h_px = obj['bbox']
                cv2.putText(output, f"{m['length_cm']:.1f}x{m['width_cm']:.1f}cm",
                            (x, y + h_px + 20), FONT, 0.5, (0, 255, 255), 1)

                lines.append(f"{i}. {obj['color']} {obj['shape']}  "
                             f"{m['length_cm']:.1f}x{m['width_cm']:.1f}cm  "
                             f"@({bx:.1f},{by:.1f})")

            # Smoothed FPS
            now = time.time()
            inst = 1.0 / max(now - last, 1e-6)
            fps = inst if fps == 0.0 else 0.9 * fps + 0.1 * inst
            last = now

            cv2.imshow(WINDOW_NAME, add_info_panel(output, lines))

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):  # q or Esc
                break
            if key == ord('c'):
                new_corners = pick_corners(frame, board_cm)
                if new_corners is not None:
                    corners = new_corners
                    save_calibration(args.calib_file, frame_size, board_cm, corners)
                    H, H_inv = build_homography(corners, board_cm)
                    calib_text, scale_line = describe_calibration(corners, board_cm)
                    print(calib_text)
                last = time.time()
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
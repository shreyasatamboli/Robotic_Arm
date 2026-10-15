#!/usr/bin/env python3
"""
Simulation Demo - Test the system without physical hardware

This script simulates the robotic arm and provides a visual demonstration
of the sorting system working with synthetic objects.
"""

import cv2
import numpy as np
import sys
import os
import time
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'software'))

from vision.object_detector import ObjectDetector


class VirtualWorkspace:
    """Create a virtual workspace with synthetic objects"""
    
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.objects = []
        
    def add_object(self, color: str, shape: str, position: tuple, size: int = 50):
        """Add a synthetic object to the workspace"""
        self.objects.append({
            'color': color,
            'shape': shape,
            'position': position,
            'size': size
        })
    
    def remove_object(self, index: int):
        """Remove an object from the workspace"""
        if 0 <= index < len(self.objects):
            self.objects.pop(index)
    
    def render(self) -> np.ndarray:
        """Render the workspace with all objects"""
        # Create white background
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        # Define BGR colors
        color_map = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255)
        }
        
        # Draw each object
        for obj in self.objects:
            color_bgr = color_map.get(obj['color'], (128, 128, 128))
            pos = obj['position']
            size = obj['size']
            
            if obj['shape'] == 'circle':
                cv2.circle(frame, pos, size//2, color_bgr, -1)
                cv2.circle(frame, pos, size//2, (0, 0, 0), 2)
                
            elif obj['shape'] == 'square':
                x, y = pos
                pt1 = (x - size//2, y - size//2)
                pt2 = (x + size//2, y + size//2)
                cv2.rectangle(frame, pt1, pt2, color_bgr, -1)
                cv2.rectangle(frame, pt1, pt2, (0, 0, 0), 2)
                
            elif obj['shape'] == 'triangle':
                x, y = pos
                pts = np.array([
                    [x, y - size//2],
                    [x - size//2, y + size//2],
                    [x + size//2, y + size//2]
                ], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(frame, [pts], color_bgr)
                cv2.polylines(frame, [pts], True, (0, 0, 0), 2)
        
        return frame


class SimulatedArm:
    """Simulate robotic arm movements"""
    
    def __init__(self):
        self.current_pos = (320, 400)  # Home position
        self.gripper_closed = False
        self.holding_object = None
        
    def move_to(self, position: tuple, duration: float = 1.0):
        """Simulate movement to position"""
        print(f"Moving to {position}...")
        time.sleep(duration)
        self.current_pos = position
        
    def pick(self, obj_index: int):
        """Simulate picking an object"""
        print(f"Picking object {obj_index}...")
        self.gripper_closed = True
        self.holding_object = obj_index
        time.sleep(0.5)
        
    def place(self):
        """Simulate placing an object"""
        print(f"Placing object...")
        self.gripper_closed = False
        result = self.holding_object
        self.holding_object = None
        time.sleep(0.5)
        return result


def create_demo_objects() -> List[Dict]:
    """Create a set of demo objects"""
    colors = ['red', 'green', 'blue', 'yellow']
    shapes = ['circle', 'square', 'triangle']
    
    objects = []
    
    # Create random objects
    for i in range(8):
        color = colors[i % len(colors)]
        shape = shapes[i % len(shapes)]
        x = 150 + (i % 4) * 100
        y = 150 + (i // 4) * 150
        
        objects.append({
            'color': color,
            'shape': shape,
            'position': (x, y),
            'size': 60
        })
    
    return objects


def draw_arm(frame: np.ndarray, arm_pos: tuple, gripper_closed: bool):
    """Draw a simple representation of the arm"""
    # Draw arm base
    cv2.circle(frame, (320, 480), 20, (100, 100, 100), -1)
    
    # Draw arm link
    cv2.line(frame, (320, 480), arm_pos, (100, 100, 100), 8)
    
    # Draw end effector
    color = (0, 200, 0) if gripper_closed else (200, 0, 0)
    cv2.circle(frame, arm_pos, 15, color, -1)
    cv2.circle(frame, arm_pos, 15, (0, 0, 0), 2)


def main():
    """Run simulation demo"""
    
    print("=" * 60)
    print("  Robotic Arm Sorting System - SIMULATION DEMO")
    print("=" * 60)
    print()
    print("This demo simulates the sorting system without hardware.")
    print()
    print("Controls:")
    print("  SPACE - Start/pause sorting")
    print("  r     - Reset and add new objects")
    print("  c     - Sort by color")
    print("  s     - Sort by shape")
    print("  q     - Quit")
    print()
    print("=" * 60)
    print()
    
    # Create virtual workspace
    workspace = VirtualWorkspace()
    
    # Create detector
    detector = ObjectDetector()
    
    # Create simulated arm
    arm = SimulatedArm()
    
    # Add initial objects
    demo_objects = create_demo_objects()
    for obj in demo_objects:
        workspace.add_object(obj['color'], obj['shape'], obj['position'], obj['size'])
    
    # Sorting state
    sorting_active = False
    sort_mode = 'color'
    current_object_idx = 0
    
    # Sorting zones
    zones_by_color = {
        'red': (120, 60),
        'green': (520, 60),
        'blue': (120, 420),
        'yellow': (520, 420)
    }
    
    zones_by_shape = {
        'circle': (120, 60),
        'square': (520, 60),
        'triangle': (320, 60)
    }
    
    print("Ready! Press SPACE to start sorting simulation...")
    
    while True:
        # Render workspace
        frame = workspace.render()
        
        # Detect objects (for visualization)
        detected = detector.detect_objects(frame)
        
        # Draw detections
        for det in detected:
            x, y, w, h = det['bbox']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 255), 2)
            label = f"{det['color']} {det['shape']}"
            cv2.putText(frame, label, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        # Draw arm
        draw_arm(frame, arm.current_pos, arm.gripper_closed)
        
        # Draw sorting zones
        zones = zones_by_color if sort_mode == 'color' else zones_by_shape
        for zone_name, zone_pos in zones.items():
            cv2.circle(frame, zone_pos, 30, (200, 200, 200), 2)
            cv2.putText(frame, zone_name, (zone_pos[0]-20, zone_pos[1]+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
        
        # Draw info
        status = "SORTING" if sorting_active else "PAUSED"
        cv2.putText(frame, f"Status: {status}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"Mode: {sort_mode.upper()}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"Objects: {len(workspace.objects)}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Show frame
        cv2.imshow('Simulation Demo', frame)
        
        # Handle keyboard input
        key = cv2.waitKey(50) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '):
            sorting_active = not sorting_active
            if sorting_active:
                print(f"\nStarting {sort_mode} sorting...")
            else:
                print("Paused")
        elif key == ord('r'):
            # Reset
            workspace.objects.clear()
            demo_objects = create_demo_objects()
            for obj in demo_objects:
                workspace.add_object(obj['color'], obj['shape'], obj['position'], obj['size'])
            arm.current_pos = (320, 400)
            arm.holding_object = None
            current_object_idx = 0
            print("Reset workspace")
        elif key == ord('c'):
            sort_mode = 'color'
            print("Sorting mode: COLOR")
        elif key == ord('s'):
            sort_mode = 'shape'
            print("Sorting mode: SHAPE")
        
        # Perform sorting if active
        if sorting_active and len(workspace.objects) > 0 and arm.holding_object is None:
            # Pick next object
            obj = workspace.objects[0]
            
            # Move to object
            arm.move_to(obj['position'], 0.5)
            
            # Pick
            arm.pick(0)
            
            # Determine target zone
            if sort_mode == 'color':
                target_zone = zones_by_color.get(obj['color'], (320, 240))
            else:
                target_zone = zones_by_shape.get(obj['shape'], (320, 240))
            
            # Move to zone
            arm.move_to(target_zone, 0.5)
            
            # Place
            workspace.remove_object(0)
            arm.place()
            
            # Return home
            arm.move_to((320, 400), 0.5)
            
            print(f"Sorted {obj['color']} {obj['shape']}")
            
            # Stop if no more objects
            if len(workspace.objects) == 0:
                sorting_active = False
                print("\nAll objects sorted! Press 'r' to reset.")
    
    cv2.destroyAllWindows()
    print("\nSimulation complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""
Robotic Arm Controller Module

Handles communication with Arduino firmware and provides high-level
control interface for the robotic arm.
"""

import serial
import time
import numpy as np
from typing import Tuple, Optional


class RoboticArmController:
    """Controller for 5-DOF robotic arm via serial communication"""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 9600):
        """
        Initialize robotic arm controller
        
        Args:
            port: Serial port for Arduino connection
            baudrate: Communication speed
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.connected = False
        
        # Current joint angles (degrees)
        self.current_angles = [90, 90, 90, 90, 90]
        
        # Physical parameters (in mm)
        self.link_lengths = [100, 150, 150, 100, 50]  # Link lengths for each joint
        
    def connect(self) -> bool:
        """
        Connect to the robotic arm via serial port
        
        Returns:
            True if connection successful
        """
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Wait for Arduino to reset
            
            # Check if Arduino is ready
            response = self.serial.readline().decode().strip()
            if response == "READY":
                self.connected = True
                print(f"Connected to robotic arm on {self.port}")
                return True
            else:
                print(f"Unexpected response: {response}")
                return False
                
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the robotic arm"""
        if self.serial and self.connected:
            self.serial.close()
            self.connected = False
            print("Disconnected from robotic arm")
    
    def move_to_angles(self, angles: list) -> bool:
        """
        Move arm to specified joint angles
        
        Args:
            angles: List of 5 angles in degrees [base, shoulder, elbow, wrist, gripper]
            
        Returns:
            True if command successful
        """
        if not self.connected:
            print("Not connected to robotic arm")
            return False
        
        if len(angles) != 5:
            print("Error: Must provide exactly 5 angles")
            return False
        
        # Validate angles
        for angle in angles:
            if not 0 <= angle <= 180:
                print(f"Error: Angle {angle} out of range (0-180)")
                return False
        
        # Send command
        command = f"SERVO,{angles[0]},{angles[1]},{angles[2]},{angles[3]},{angles[4]}\n"
        self.serial.write(command.encode())
        
        # Wait for response
        response = self.serial.readline().decode().strip()
        
        if response == "OK":
            self.current_angles = angles
            return True
        else:
            print(f"Error from Arduino: {response}")
            return False
    
    def move_to_home(self) -> bool:
        """Move arm to home position (all angles at 90 degrees)"""
        if not self.connected:
            return False
        
        self.serial.write(b"HOME\n")
        response = self.serial.readline().decode().strip()
        
        if response == "OK":
            self.current_angles = [90, 90, 90, 90, 90]
            return True
        return False
    
    def get_status(self) -> Optional[list]:
        """Get current joint angles from the arm"""
        if not self.connected:
            return None
        
        self.serial.write(b"STATUS\n")
        response = self.serial.readline().decode().strip()
        
        if response.startswith("STATUS:"):
            angles_str = response.split(':')[1]
            angles = [int(a) for a in angles_str.split(',')]
            self.current_angles = angles
            return angles
        return None
    
    def pick_object(self, x: float, y: float, z: float) -> bool:
        """
        Pick up object at specified position
        
        Args:
            x, y, z: Position in mm (workspace coordinates)
            
        Returns:
            True if successful
        """
        # Calculate inverse kinematics
        angles = self.inverse_kinematics(x, y, z)
        
        if angles is None:
            print("Position out of reach")
            return False
        
        # Move to position with gripper open
        pick_angles = angles + [180]  # Open gripper
        if not self.move_to_angles(pick_angles):
            return False
        
        time.sleep(0.5)
        
        # Close gripper
        pick_angles[4] = 30  # Close gripper
        if not self.move_to_angles(pick_angles):
            return False
        
        time.sleep(0.5)
        
        # Lift object
        angles_lift = self.inverse_kinematics(x, y, z + 50)
        if angles_lift:
            lift_angles = angles_lift + [30]  # Keep gripper closed
            self.move_to_angles(lift_angles)
        
        return True
    
    def place_object(self, x: float, y: float, z: float) -> bool:
        """
        Place object at specified position
        
        Args:
            x, y, z: Position in mm (workspace coordinates)
            
        Returns:
            True if successful
        """
        # Calculate inverse kinematics
        angles = self.inverse_kinematics(x, y, z + 50)
        
        if angles is None:
            print("Position out of reach")
            return False
        
        # Move to position above target with gripper closed
        place_angles = angles + [30]  # Closed gripper
        if not self.move_to_angles(place_angles):
            return False
        
        time.sleep(0.5)
        
        # Lower to target position
        angles_lower = self.inverse_kinematics(x, y, z)
        if angles_lower:
            lower_angles = angles_lower + [30]
            self.move_to_angles(lower_angles)
            
            time.sleep(0.5)
            
            # Open gripper
            lower_angles[4] = 180  # Open gripper
            if not self.move_to_angles(lower_angles):
                return False
        else:
            print("Failed to calculate lower position")
            return False
        
        time.sleep(0.5)
        
        return True
    
    def inverse_kinematics(self, x: float, y: float, z: float) -> Optional[list]:
        """
        Calculate joint angles for desired end-effector position
        
        Args:
            x, y, z: Target position in mm
            
        Returns:
            List of joint angles [base, shoulder, elbow, wrist] or None if unreachable
        """
        # Simplified 3D inverse kinematics for a 5-DOF arm
        # This is a basic implementation - real systems would use more sophisticated algorithms
        
        # Base angle (rotation around vertical axis)
        base_angle = np.degrees(np.arctan2(y, x))
        
        # Distance in XY plane
        r = np.sqrt(x*x + y*y)
        
        # Adjust for wrist length
        r_adj = r - self.link_lengths[3]
        z_adj = z - self.link_lengths[0]
        
        # Distance to target
        d = np.sqrt(r_adj*r_adj + z_adj*z_adj)
        
        # Check if reachable
        l1 = self.link_lengths[1]  # Shoulder to elbow
        l2 = self.link_lengths[2]  # Elbow to wrist
        
        if d > (l1 + l2) or d < abs(l1 - l2):
            return None  # Target unreachable
        
        # Elbow angle (using cosine law)
        cos_elbow = (l1*l1 + l2*l2 - d*d) / (2 * l1 * l2)
        cos_elbow = np.clip(cos_elbow, -1, 1)
        elbow_angle = 180 - np.degrees(np.arccos(cos_elbow))
        
        # Shoulder angle
        alpha = np.arctan2(z_adj, r_adj)
        beta = np.arccos(np.clip((l1*l1 + d*d - l2*l2) / (2 * l1 * d), -1, 1))
        shoulder_angle = 90 - np.degrees(alpha + beta)
        
        # Wrist angle (keep end-effector horizontal)
        wrist_angle = 90 - (shoulder_angle - elbow_angle)
        
        # Ensure angles are within valid range
        base_angle = np.clip(base_angle + 90, 0, 180)
        shoulder_angle = np.clip(shoulder_angle, 0, 180)
        elbow_angle = np.clip(elbow_angle, 0, 180)
        wrist_angle = np.clip(wrist_angle, 0, 180)
        
        return [int(base_angle), int(shoulder_angle), int(elbow_angle), int(wrist_angle)]
    
    def forward_kinematics(self, angles: list) -> Tuple[float, float, float]:
        """
        Calculate end-effector position from joint angles
        
        Args:
            angles: List of joint angles [base, shoulder, elbow, wrist]
            
        Returns:
            (x, y, z) position in mm
        """
        # Convert angles to radians
        base_rad = np.radians(angles[0] - 90)
        shoulder_rad = np.radians(90 - angles[1])
        elbow_rad = np.radians(angles[2] - 180)
        wrist_rad = np.radians(angles[3])
        
        # Calculate position
        l0 = self.link_lengths[0]
        l1 = self.link_lengths[1]
        l2 = self.link_lengths[2]
        l3 = self.link_lengths[3]
        
        # Height
        z = l0 + l1 * np.sin(shoulder_rad) + l2 * np.sin(shoulder_rad + elbow_rad)
        
        # Horizontal distance from base
        r = l1 * np.cos(shoulder_rad) + l2 * np.cos(shoulder_rad + elbow_rad) + l3
        
        # X and Y coordinates
        x = r * np.cos(base_rad)
        y = r * np.sin(base_rad)
        
        return (x, y, z)

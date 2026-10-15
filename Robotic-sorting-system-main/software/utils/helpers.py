"""
Utility functions for the robotic arm sorting system
"""

import json
import numpy as np
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        return {}


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """Save configuration to JSON file"""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to save config: {e}")
        return False


def deg_to_rad(degrees: float) -> float:
    """Convert degrees to radians"""
    return degrees * np.pi / 180.0


def rad_to_deg(radians: float) -> float:
    """Convert radians to degrees"""
    return radians * 180.0 / np.pi


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def interpolate(start: float, end: float, t: float) -> float:
    """Linear interpolation between start and end"""
    return start + (end - start) * t


def calculate_distance(p1: tuple, p2: tuple) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


class Logger:
    """Simple logging utility"""
    
    def __init__(self, log_file: str = None, verbose: bool = True):
        self.log_file = log_file
        self.verbose = verbose
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        log_line = f"[{level}] {message}"
        
        if self.verbose:
            print(log_line)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_line + '\n')
            except Exception as e:
                print(f"Failed to write to log file: {e}")
    
    def info(self, message: str):
        """Log info message"""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Log warning message"""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """Log error message"""
        self.log(message, "ERROR")


def validate_position(x: float, y: float, z: float, 
                     workspace_limits: Dict[str, tuple]) -> bool:
    """
    Validate if position is within workspace limits
    
    Args:
        x, y, z: Position coordinates
        workspace_limits: Dict with 'x', 'y', 'z' keys containing (min, max) tuples
        
    Returns:
        True if position is valid
    """
    if 'x' in workspace_limits:
        x_min, x_max = workspace_limits['x']
        if not (x_min <= x <= x_max):
            return False
    
    if 'y' in workspace_limits:
        y_min, y_max = workspace_limits['y']
        if not (y_min <= y <= y_max):
            return False
    
    if 'z' in workspace_limits:
        z_min, z_max = workspace_limits['z']
        if not (z_min <= z <= z_max):
            return False
    
    return True


def create_trajectory(start_angles: list, end_angles: list, 
                     steps: int = 10) -> list:
    """
    Create smooth trajectory between two joint configurations
    
    Args:
        start_angles: Starting joint angles
        end_angles: Target joint angles
        steps: Number of interpolation steps
        
    Returns:
        List of intermediate joint configurations
    """
    trajectory = []
    
    for i in range(steps + 1):
        t = i / steps
        intermediate = [
            interpolate(start, end, t)
            for start, end in zip(start_angles, end_angles)
        ]
        trajectory.append(intermediate)
    
    return trajectory

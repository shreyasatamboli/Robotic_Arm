#!/usr/bin/env python3
"""
Example: Test robotic arm control without vision

This example demonstrates the arm control system in isolation.
Use this to test arm movements and kinematics.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'software'))

from control.arm_controller import RoboticArmController


def main():
    """Test robotic arm control"""
    
    print("=" * 50)
    print("  Robotic Arm Control Test")
    print("=" * 50)
    print()
    
    # Get serial port from user
    port = input("Enter serial port (default: /dev/ttyUSB0): ").strip()
    if not port:
        port = '/dev/ttyUSB0'
    
    # Initialize controller
    arm = RoboticArmController(port=port)
    
    try:
        # Connect to arm
        print("\nConnecting to robotic arm...")
        if not arm.connect():
            print("Failed to connect. Please check:")
            print("  - Arduino is connected to the correct port")
            print("  - Firmware is uploaded to Arduino")
            print("  - No other program is using the serial port")
            return 1
        
        print("Connected successfully!")
        print()
        
        # Test sequence
        print("Running test sequence...")
        print()
        
        # Test 1: Home position
        print("Test 1: Moving to home position")
        arm.move_to_home()
        time.sleep(2)
        
        # Test 2: Individual joint movements
        print("Test 2: Individual joint movements")
        
        print("  - Moving base")
        arm.move_to_angles([45, 90, 90, 90, 90])
        time.sleep(1)
        arm.move_to_angles([135, 90, 90, 90, 90])
        time.sleep(1)
        arm.move_to_angles([90, 90, 90, 90, 90])
        time.sleep(1)
        
        print("  - Moving shoulder")
        arm.move_to_angles([90, 60, 90, 90, 90])
        time.sleep(1)
        arm.move_to_angles([90, 120, 90, 90, 90])
        time.sleep(1)
        arm.move_to_angles([90, 90, 90, 90, 90])
        time.sleep(1)
        
        print("  - Moving elbow")
        arm.move_to_angles([90, 90, 60, 90, 90])
        time.sleep(1)
        arm.move_to_angles([90, 90, 120, 90, 90])
        time.sleep(1)
        arm.move_to_angles([90, 90, 90, 90, 90])
        time.sleep(1)
        
        print("  - Testing gripper")
        arm.move_to_angles([90, 90, 90, 90, 180])  # Open
        time.sleep(1)
        arm.move_to_angles([90, 90, 90, 90, 30])   # Close
        time.sleep(1)
        arm.move_to_angles([90, 90, 90, 90, 90])   # Middle
        time.sleep(1)
        
        # Test 3: Pick and place simulation
        print("Test 3: Pick and place simulation")
        
        print("  - Moving to pickup position")
        if arm.pick_object(150, 0, 0):
            print("  - Pick successful!")
            time.sleep(1)
            
            print("  - Moving to place position")
            if arm.place_object(150, 100, 0):
                print("  - Place successful!")
            else:
                print("  - Place failed")
        else:
            print("  - Pick failed")
        
        time.sleep(1)
        
        # Test 4: Get status
        print("Test 4: Getting arm status")
        status = arm.get_status()
        if status:
            print(f"  Current angles: {status}")
        
        # Return to home
        print("\nReturning to home position")
        arm.move_to_home()
        time.sleep(2)
        
        print("\nAll tests complete!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Disconnect
        arm.disconnect()
        print("Disconnected")


if __name__ == '__main__':
    sys.exit(main())

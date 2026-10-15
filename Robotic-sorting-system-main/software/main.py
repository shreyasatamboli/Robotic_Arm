"""
Main entry point for the Robotic Arm Sorting System

Usage:
    python main.py [options]
    
Options:
    --port PORT         Serial port for robotic arm (default: /dev/ttyUSB0)
    --camera ID         Camera device ID (default: 0)
    --mode MODE         Sorting mode: 'color' or 'shape' (default: color)
    --count N           Number of objects to sort (default: 10)
    --interactive       Run in interactive mode
    --calibrate         Run camera calibration
"""

import sys
import argparse
from sorting_system import SortingSystem


def main():
    """Main entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Robotic Arm Sorting System with Computer Vision'
    )
    
    parser.add_argument(
        '--port',
        type=str,
        default='/dev/ttyUSB0',
        help='Serial port for robotic arm (default: /dev/ttyUSB0)'
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device ID (default: 0)'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['color', 'shape'],
        default='color',
        help='Sorting mode: color or shape (default: color)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=10,
        help='Number of objects to sort (default: 10)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--calibrate',
        action='store_true',
        help='Run camera calibration'
    )
    
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Disable camera display window'
    )
    
    args = parser.parse_args()
    
    # Create sorting system
    print("=" * 50)
    print("  Robotic Arm Sorting System")
    print("  Computer Vision Object Sorting")
    print("=" * 50)
    print()
    
    system = SortingSystem(arm_port=args.port, camera_id=args.camera)
    
    try:
        # Initialize system
        if not system.initialize():
            print("Failed to initialize system")
            return 1
        
        print()
        
        # Run appropriate mode
        if args.calibrate:
            print("Running camera calibration...")
            system.calibrate_camera()
            
        elif args.interactive:
            print("Starting interactive mode...")
            system.run_interactive_mode()
            
        else:
            print(f"Starting automatic sorting: {args.mode} mode")
            print(f"Target: {args.count} objects")
            print()
            
            sorted_count = system.sort_objects(
                sort_mode=args.mode,
                max_objects=args.count,
                display=not args.no_display
            )
            
            print()
            print(f"Session complete: {sorted_count} objects sorted")
        
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
        # Always shutdown cleanly
        system.shutdown()


if __name__ == '__main__':
    sys.exit(main())

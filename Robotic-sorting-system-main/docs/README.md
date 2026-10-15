# Robotic Arm Sorting System

A complete 5-DOF (Degree of Freedom) robotic arm system with computer vision capabilities for identifying, sorting, and placing objects based on color and shape.

## Features

- **5-DOF Robotic Arm Control**: Full control of base, shoulder, elbow, wrist, and gripper joints
- **Computer Vision**: Real-time object detection using OpenCV
- **Color Detection**: Identifies red, green, blue, and yellow objects
- **Shape Recognition**: Detects circles, squares, triangles, and rectangles
- **Automated Sorting**: Sorts objects into designated zones based on color or shape
- **Serial Communication**: Arduino firmware with robust command protocol
- **Inverse Kinematics**: Automatic calculation of joint angles for target positions
- **Interactive Mode**: Manual control and testing interface

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Control Software                       │
│                      (Python)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Vision     │  │   Control    │  │    Utils     │  │
│  │   System     │  │   System     │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────┬────────────────┬──────────────────────────┘
             │                │
      Camera │                │ Serial
             │                │
         ┌───▼────┐      ┌────▼─────┐
         │        │      │          │
         │ Camera │      │ Arduino  │
         │        │      │ Firmware │
         └────────┘      └────┬─────┘
                              │
                         ┌────▼─────────┐
                         │   Servos     │
                         │ (5-DOF Arm)  │
                         └──────────────┘
```

## Hardware Requirements

### Robotic Arm
- 5 Servo Motors (SG90 or similar)
  - Base rotation
  - Shoulder
  - Elbow
  - Wrist
  - Gripper
- Arduino Uno/Mega
- Power supply for servos (5-6V, 2A minimum)

### Vision System
- USB Camera (640x480 minimum resolution)
- Adequate lighting for color detection

### Connections

Arduino Pin Assignments:
- Pin 3: Base servo
- Pin 5: Shoulder servo
- Pin 6: Elbow servo
- Pin 9: Wrist servo
- Pin 10: Gripper servo

## Software Requirements

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- opencv-python >= 4.5.0
- numpy >= 1.19.0
- pyserial >= 3.5

### Arduino IDE
- Arduino IDE 1.8.x or newer
- Servo library (included with Arduino IDE)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/varolkan/Robotic-arm-sorting-system.git
cd Robotic-arm-sorting-system
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Upload Arduino Firmware
1. Open `firmware/robotic_arm/robotic_arm.ino` in Arduino IDE
2. Select your Arduino board and port
3. Upload the firmware

### 4. Configure the System
Edit `config/config.json` to match your hardware setup:
- Serial port
- Camera device ID
- Workspace dimensions
- Color ranges

## Usage

### Quick Start

1. **Connect Hardware**
   - Connect Arduino to computer via USB
   - Connect camera to computer
   - Power on servos

2. **Run the System**
   ```bash
   cd software
   python main.py --interactive
   ```

### Command Line Options

```bash
# Sort by color
python main.py --mode color --count 10

# Sort by shape
python main.py --mode shape --count 5

# Interactive mode
python main.py --interactive

# Calibrate camera
python main.py --calibrate

# Specify serial port and camera
python main.py --port /dev/ttyUSB0 --camera 0
```

### Interactive Mode Commands

When running in interactive mode:
- `1` - Start sorting by color
- `2` - Start sorting by shape
- `c` - Calibrate camera
- `h` - Move to home position
- `q` - Quit

### Testing Individual Components

**Test Vision System Only:**
```bash
cd examples
python test_vision.py
```

**Test Robotic Arm Only:**
```bash
cd examples
python test_arm.py
```

## Configuration

### Camera Calibration

1. Run calibration mode:
   ```bash
   python main.py --calibrate
   ```

2. Place a reference object of known size in view
3. Press 'c' to capture
4. Enter the object's actual width in millimeters

### Color Range Adjustment

Edit `config/config.json` to adjust HSV color ranges for better detection in your lighting conditions:

```json
"color_ranges": {
    "red": {
        "lower1": [0, 100, 100],
        "upper1": [10, 255, 255]
    }
}
```

### Sorting Zones

Define where objects should be placed in `config/config.json`:

```json
"sorting_zones": {
    "by_color": {
        "red": [200, 100, 0],
        "green": [200, -100, 0]
    }
}
```

Coordinates are in millimeters from the robot base.

## System Workflow

1. **Initialization**
   - Connect to Arduino
   - Initialize camera
   - Move arm to home position

2. **Object Detection**
   - Capture camera frame
   - Process image with OpenCV
   - Detect objects by color and shape
   - Calculate object position

3. **Sorting Decision**
   - Determine target zone based on:
     - Color (red, green, blue, yellow)
     - Shape (circle, square, triangle)

4. **Pick and Place**
   - Calculate inverse kinematics
   - Move to object position
   - Close gripper to pick
   - Move to target zone
   - Open gripper to place
   - Return to home position

5. **Repeat**
   - Continue until target count reached

## API Reference

### RoboticArmController

```python
from control.arm_controller import RoboticArmController

arm = RoboticArmController(port='/dev/ttyUSB0')
arm.connect()
arm.move_to_home()
arm.pick_object(x=150, y=0, z=0)
arm.place_object(x=200, y=100, z=0)
```

### ObjectDetector

```python
from vision.object_detector import ObjectDetector

detector = ObjectDetector()
objects = detector.detect_objects(frame)
# Returns: [{'color': 'red', 'shape': 'circle', 'centroid': (x, y), ...}]
```

### SortingSystem

```python
from sorting_system import SortingSystem

system = SortingSystem()
system.initialize()
system.sort_objects(sort_mode='color', max_objects=10)
system.shutdown()
```

## Troubleshooting

### Arduino Connection Issues
- Check serial port: `ls /dev/tty*` (Linux/Mac) or Device Manager (Windows)
- Ensure no other program is using the port
- Verify firmware is uploaded correctly
- Check baudrate matches (9600)

### Camera Not Found
- List cameras: `ls /dev/video*` (Linux)
- Try different camera IDs (0, 1, 2)
- Check camera permissions
- Test with: `python examples/test_vision.py`

### Poor Object Detection
- Adjust lighting conditions
- Calibrate color ranges in config
- Ensure good contrast between objects and background
- Adjust min/max area thresholds

### Incorrect Kinematics
- Verify link lengths in config match physical arm
- Calibrate camera position
- Check workspace limits
- Validate pixel-to-world transformation

## Project Structure

```
Robotic-arm-sorting-system/
├── firmware/
│   └── robotic_arm/
│       └── robotic_arm.ino      # Arduino firmware
├── software/
│   ├── vision/
│   │   └── object_detector.py   # Computer vision module
│   ├── control/
│   │   └── arm_controller.py    # Arm control module
│   ├── utils/
│   │   └── helpers.py           # Utility functions
│   ├── sorting_system.py        # Main sorting system
│   └── main.py                  # Entry point
├── config/
│   └── config.json              # Configuration file
├── examples/
│   ├── test_vision.py           # Vision test script
│   └── test_arm.py              # Arm test script
├── docs/
│   └── README.md                # This file
├── requirements.txt             # Python dependencies
└── .gitignore
```

## Development

### Adding New Colors

1. Determine HSV range for the color
2. Add to `color_ranges` in `object_detector.py`
3. Add sorting zone in `config.json`

### Adding New Shapes

1. Implement detection logic in `_classify_shape()` method
2. Add sorting zone in `config.json`

### Customizing Motion

- Adjust `MOVE_DELAY` in Arduino firmware for speed
- Modify trajectory planning in `arm_controller.py`
- Update `pick_object()` and `place_object()` methods

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- OpenCV community for computer vision tools
- Arduino community for firmware examples
- Robotics community for kinematics algorithms

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Note**: This is an educational project demonstrating robotic manipulation and computer vision. Actual performance depends on hardware quality, calibration, and environmental conditions.

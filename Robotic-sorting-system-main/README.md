# Robotic Arm Sorting System

A complete 5-DOF (Degree of Freedom) robotic arm system with computer vision capabilities for identifying, sorting, and placing objects based on color and shape.

![System Overview](https://img.shields.io/badge/Arduino-Firmware-00979D?style=flat&logo=arduino&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=flat&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=flat&logo=opencv&logoColor=white)

## 🤖 Overview

This project implements a complete robotic arm sorting system that combines:
- **Arduino-based firmware** for precise servo control
- **Python control software** for high-level coordination
- **OpenCV computer vision** for real-time object detection
- **Inverse kinematics** for position control

The system can detect objects by color (red, green, blue, yellow) and shape (circle, square, triangle), then automatically pick and sort them into designated zones.

## ✨ Features

- 5-DOF robotic arm control (base, shoulder, elbow, wrist, gripper)
- Real-time object detection and classification
- Color-based sorting (red, green, blue, yellow)
- Shape-based sorting (circle, square, triangle, rectangle)
- Automated pick-and-place operations
- Interactive control mode
- Camera calibration utilities
- Configurable workspace and sorting zones

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/varolkan/Robotic-arm-sorting-system.git
cd Robotic-arm-sorting-system

# Install Python dependencies
pip install -r requirements.txt

# Upload Arduino firmware
# Open firmware/robotic_arm/robotic_arm.ino in Arduino IDE and upload
```

### Usage

```bash
# Interactive mode
cd software
python main.py --interactive

# Automatic sorting by color
python main.py --mode color --count 10

# Automatic sorting by shape
python main.py --mode shape --count 5
```

## 📁 Project Structure

```
├── firmware/robotic_arm/       # Arduino firmware for servo control
├── software/
│   ├── vision/                 # Computer vision (OpenCV)
│   ├── control/                # Robotic arm controller
│   ├── utils/                  # Utility functions
│   ├── sorting_system.py       # Main sorting logic
│   └── main.py                 # Entry point
├── config/                     # Configuration files
├── examples/                   # Test scripts
├── docs/                       # Comprehensive documentation
└── requirements.txt            # Python dependencies
```

## 🔧 Hardware Requirements

- Arduino Uno/Mega
- 5x Servo Motors (SG90 or similar)
- USB Camera (640x480+)
- Power supply (5-6V, 2A+)

## 📖 Documentation

For detailed documentation, see [docs/README.md](docs/README.md)

Topics covered:
- Hardware setup and wiring
- Software installation
- Camera calibration
- Configuration options
- API reference
- Troubleshooting

## 🎯 System Workflow

1. **Initialize** - Connect to Arduino and camera
2. **Detect** - Identify objects using computer vision
3. **Calculate** - Determine target position using inverse kinematics
4. **Pick** - Move arm to object and close gripper
5. **Sort** - Place object in appropriate zone
6. **Repeat** - Continue for next object

## 🧪 Testing

Test individual components:

```bash
# Test vision system only
cd examples
python test_vision.py

# Test robotic arm only
python test_arm.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with Arduino, Python, and OpenCV. Developed as a demonstration of robotic manipulation and computer vision integration.

---

**Note**: This is an educational project. Performance depends on hardware quality, calibration, and environmental conditions.
# Quick Start Guide

Get your robotic arm sorting system running in minutes!

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Arduino Uno or Mega
- [ ] 5 servo motors (SG90 recommended)
- [ ] USB camera
- [ ] Power supply (5-6V, 2A+)
- [ ] Computer with Python 3.7+
- [ ] USB cable for Arduino

## Step 1: Hardware Setup (10 minutes)

### Connect Servos to Arduino

```
Servo Pin Connections:
Base     → Pin 3
Shoulder → Pin 5
Elbow    → Pin 6
Wrist    → Pin 9
Gripper  → Pin 10
```

**Power:**
- Connect all servo power (red wires) to external 5-6V supply
- Connect all servo ground (brown/black) to power supply AND Arduino GND
- ⚠️ DO NOT power servos from Arduino 5V pin!

**See [docs/HARDWARE_SETUP.md](docs/HARDWARE_SETUP.md) for detailed wiring diagrams**

### Mount Camera

- Position 30-50cm above workspace
- Point straight down
- Ensure good lighting

## Step 2: Software Setup (5 minutes)

### Install Python Dependencies

```bash
cd Robotic-arm-sorting-system
pip install -r requirements.txt
```

Required packages:
- opencv-python
- numpy
- pyserial

### Upload Arduino Firmware

1. Open Arduino IDE
2. File → Open → `firmware/robotic_arm/robotic_arm.ino`
3. Tools → Board → Select your Arduino
4. Tools → Port → Select correct port
5. Click Upload button

Wait for "Upload complete" message.

## Step 3: Test Hardware (5 minutes)

### Test Servos

```bash
cd examples
python test_arm.py
```

This will:
- Connect to Arduino
- Move each joint individually
- Test the gripper
- Run a pick-and-place sequence

**Expected:** Arm moves smoothly through test sequence.

### Test Camera

```bash
python test_vision.py
```

This will:
- Open camera feed
- Detect colored objects
- Show detections in real-time

**Expected:** Colored objects are detected and labeled.

Controls:
- `q` - Quit
- `s` - Save screenshot

## Step 4: Run Simulation (2 minutes)

Test the complete system without hardware:

```bash
python demo_simulation.py
```

Controls:
- `SPACE` - Start/pause sorting
- `c` - Sort by color
- `s` - Sort by shape
- `r` - Reset workspace
- `q` - Quit

**Expected:** Virtual objects are sorted into zones.

## Step 5: Configure System (5 minutes)

Edit `config/config.json`:

1. **Serial Port** - Set your Arduino port:
   ```json
   "port": "/dev/ttyUSB0"  // Linux/Mac
   "port": "COM3"          // Windows
   ```

2. **Camera ID** - Set camera device:
   ```json
   "device_id": 0  // Usually 0, try 1 or 2 if issues
   ```

3. **Workspace** - Adjust for your setup:
   ```json
   "workspace_limits": {
       "x": [-300, 300],
       "y": [-300, 300],
       "z": [0, 400]
   }
   ```

## Step 6: Calibrate Camera (5 minutes)

```bash
cd software
python main.py --calibrate
```

1. Place a reference object (known size)
2. Press `c` to capture
3. Enter object width in millimeters
4. System calculates pixels-per-mm ratio

## Step 7: Run the System!

### Interactive Mode (Recommended for First Run)

```bash
python main.py --interactive
```

Commands:
- `1` - Sort by color
- `2` - Sort by shape
- `c` - Calibrate camera
- `h` - Home position
- `q` - Quit

### Automatic Sorting

**Sort by color:**
```bash
python main.py --mode color --count 10
```

**Sort by shape:**
```bash
python main.py --mode shape --count 5
```

## Common Issues

### "Failed to connect to robotic arm"
- Check USB cable
- Verify serial port in config
- Ensure Arduino is powered
- Close Arduino IDE Serial Monitor

### "Failed to open camera"
- Try different camera ID (0, 1, 2)
- Check USB connection
- Verify camera permissions
- Test with `test_vision.py`

### Servos jittery or not moving
- Check power supply (needs 2-3A)
- Verify common ground
- Add capacitor across power supply
- Check servo connections

### Poor object detection
- Improve lighting
- Use neutral background
- Adjust color ranges in config
- Run camera calibration

## Next Steps

1. **Tune Color Detection** - Adjust HSV ranges in config for your lighting
2. **Define Sorting Zones** - Set optimal positions for your workspace
3. **Adjust Speed** - Modify `MOVE_DELAY` in firmware for faster/slower motion
4. **Add Objects** - Test with various colored/shaped items
5. **Experiment** - Try different sorting strategies!

## Getting Help

- **Detailed Docs**: [docs/README.md](docs/README.md)
- **Hardware Guide**: [docs/HARDWARE_SETUP.md](docs/HARDWARE_SETUP.md)
- **GitHub Issues**: Report problems or ask questions

## Quick Reference Commands

```bash
# Test individual components
python examples/test_arm.py      # Test robotic arm
python examples/test_vision.py   # Test camera/vision
python examples/demo_simulation.py  # Run simulation

# Run the system
cd software
python main.py --interactive     # Interactive mode
python main.py --mode color      # Sort by color
python main.py --mode shape      # Sort by shape
python main.py --calibrate       # Calibrate camera
```

## Safety Tips

- Always supervise the system
- Keep fingers away from moving arm
- Use appropriate power supply
- Secure all wiring
- Have emergency stop ready

---

**Congratulations!** Your robotic arm sorting system is ready to use! 🎉

For advanced features and customization, see the full documentation in [docs/README.md](docs/README.md).

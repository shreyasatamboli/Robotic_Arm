# Hardware Setup Guide

## Components List

### Robotic Arm
- 5x Servo Motors (SG90 or MG90S recommended)
  - Base rotation servo
  - Shoulder servo
  - Elbow servo
  - Wrist servo
  - Gripper servo
- Robotic arm mechanical structure or 3D printed parts
- M3 screws and standoffs for assembly

### Electronics
- Arduino Uno or Arduino Mega
- Power supply: 5-6V DC, 2A minimum (3A recommended)
- USB cable for Arduino programming and communication
- Breadboard (optional, for prototyping)
- Jumper wires

### Vision System
- USB Webcam (minimum 640x480 resolution)
- USB extension cable (if needed)
- Camera mount or tripod
- Good lighting source (LED panel recommended)

### Workspace
- Flat work surface (minimum 50cm x 50cm)
- Colored objects for sorting (red, green, blue, yellow)
- Objects with different shapes (circles, squares, triangles)
- Background mat (neutral color recommended)

## Wiring Diagram

```
Arduino Uno/Mega                    Servo Motors
┌────────────────┐                  
│                │                  Base Servo
│  Digital Pin 3 ├─────────────────► Signal (Yellow/White)
│                │                  
│  Digital Pin 5 ├─────────────────► Shoulder Servo Signal
│                │                  
│  Digital Pin 6 ├─────────────────► Elbow Servo Signal
│                │                  
│  Digital Pin 9 ├─────────────────► Wrist Servo Signal
│                │                  
│ Digital Pin 10 ├─────────────────► Gripper Servo Signal
│                │                  
│      5V/VCC    ├───┬──────────────► All Servos VCC (Red)
│                │   │              
│       GND      ├───┴──────────────► All Servos GND (Brown/Black)
│                │                  
│  USB Port      ├──── To Computer
└────────────────┘                  

Power Supply (5-6V, 2A+)
┌────────────────┐
│      +         ├──────────────────► Servo VCC (Power Rail)
│      -         ├──────────────────► Servo GND (Power Rail)
└────────────────┘

Note: For Arduino Uno with 5 servos, external power is REQUIRED!
Connect power supply negative to Arduino GND for common ground.
```

## Detailed Pin Connections

### Servo Wire Colors (Standard)
- **Brown/Black**: Ground (GND)
- **Red**: Power (VCC, 5-6V)
- **Orange/Yellow/White**: Signal (PWM)

### Arduino to Servo Connections

| Arduino Pin | Servo Joint | Servo Signal Wire |
|-------------|-------------|-------------------|
| Digital 3   | Base        | Orange/Yellow     |
| Digital 5   | Shoulder    | Orange/Yellow     |
| Digital 6   | Elbow       | Orange/Yellow     |
| Digital 9   | Wrist       | Orange/Yellow     |
| Digital 10  | Gripper     | Orange/Yellow     |

**Power Connections:**
- All servo RED wires → External 5-6V power supply positive
- All servo BROWN/BLACK wires → External power supply negative AND Arduino GND

⚠️ **Important**: Do NOT power servos from Arduino 5V pin - it cannot supply enough current!

## Power Supply Setup

### Option 1: Dedicated DC Power Supply (Recommended)
1. Use a 5V or 6V DC power adapter (2-3A)
2. Connect positive to servo VCC rail
3. Connect negative to servo GND rail and Arduino GND
4. This ensures stable power for all servos

### Option 2: Battery Pack
1. Use 4x AA batteries (6V) or dedicated LiPo battery
2. Add a voltage regulator if needed
3. Connect as above with common ground

## Camera Setup

### Mounting
1. Mount camera above the workspace
2. Height: 30-50cm above work surface
3. Angle: Pointing straight down for best results
4. Ensure entire sorting area is visible

### Connection
1. Connect USB camera to computer
2. Use USB extension cable if needed
3. Verify camera is recognized: `ls /dev/video*` (Linux)

## Lighting

Good lighting is crucial for color detection:
1. Use diffuse lighting (avoid harsh shadows)
2. LED panel lights work well
3. Avoid colored lights (use white/daylight)
4. Position lights to minimize glare on objects

## Workspace Layout

```
                Camera (mounted above)
                       |
                       v
    ╔══════════════════════════════════╗
    ║                                  ║
    ║  [Zone 3]     [Pickup]  [Zone 4]║
    ║                                  ║
    ║              [Robot]             ║
    ║                                  ║
    ║  [Zone 1]              [Zone 2] ║
    ║                                  ║
    ╚══════════════════════════════════╝
           Work Surface (50x50cm)

Robot Position: Center of workspace
Pickup Zone: In front of robot (camera field of view)
Sorting Zones: Four corners or as configured
```

## Assembly Steps

### 1. Assemble Robotic Arm
1. Follow mechanical assembly instructions for your arm kit
2. Attach servos at each joint
3. Ensure smooth movement and no binding
4. Test range of motion before wiring

### 2. Wire Servos to Arduino
1. Connect signal wires to Arduino digital pins
2. Create common power rail for all servo VCC wires
3. Create common ground rail for all servo GND wires
4. Connect Arduino GND to ground rail (common ground)

### 3. Connect Power Supply
1. Connect external power to servo power rail
2. Double-check polarity (+ and -)
3. Verify voltage is 5-6V
4. Ensure power supply can provide 2-3A

### 4. Program Arduino
1. Connect Arduino to computer via USB
2. Open `firmware/robotic_arm/robotic_arm.ino`
3. Select correct board and port in Arduino IDE
4. Upload firmware
5. Open serial monitor to verify "READY" message

### 5. Setup Camera
1. Mount camera above workspace
2. Connect to computer
3. Adjust position and angle
4. Test with `examples/test_vision.py`

### 6. Configure System
1. Edit `config/config.json`
2. Set correct serial port
3. Set correct camera ID
4. Adjust workspace dimensions

## Testing

### Pre-flight Checks
- [ ] All servos connected properly
- [ ] External power supply connected
- [ ] Common ground established
- [ ] Arduino programmed with firmware
- [ ] Camera positioned and connected
- [ ] Python dependencies installed
- [ ] Config file updated

### System Tests
1. Test Arduino connection:
   ```bash
   cd examples
   python test_arm.py
   ```

2. Test camera and vision:
   ```bash
   python test_vision.py
   ```

3. Test complete system:
   ```bash
   cd software
   python main.py --interactive
   ```

## Troubleshooting

### Servos Not Moving
- Check power supply voltage and current
- Verify servo signal wire connections
- Confirm common ground between Arduino and power supply
- Test servos individually

### Jittery Servo Movement
- Power supply current insufficient
- Add capacitor (1000µF) across power supply
- Check for loose connections
- Reduce movement speed in firmware

### Arduino Resets When Servos Move
- External power supply required
- Increase power supply current capacity
- Ensure common ground

### Camera Not Detected
- Check USB connection
- Try different USB ports
- Verify camera ID in config
- Test camera independently

### Poor Object Detection
- Improve lighting
- Adjust color ranges in config
- Use neutral background
- Calibrate camera

## Safety Notes

⚠️ **Important Safety Guidelines**:
- Never power servos directly from Arduino 5V pin
- Ensure power supply polarity is correct
- Keep fingers clear of moving arm
- Secure all wiring to prevent snagging
- Use appropriate wire gauge for current
- Add emergency stop button for safety
- Supervise system during operation

## Maintenance

- Regularly check for loose screws
- Clean servo gears if movement becomes rough
- Verify wire connections periodically
- Update calibration as needed
- Keep workspace clean and organized

---

**Need Help?**

If you encounter issues not covered here:
1. Check the main documentation in `docs/README.md`
2. Review troubleshooting section
3. Open an issue on GitHub with:
   - Hardware setup description
   - Error messages or symptoms
   - Photos of your setup (if relevant)

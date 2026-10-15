/*
 * 5-DOF Robotic Arm Sorting System - Firmware
 * 
 * This firmware controls a 5 Degree-of-Freedom robotic arm using servo motors.
 * It receives commands via serial communication from the control software.
 * 
 * Hardware:
 * - 5 Servo motors (base, shoulder, elbow, wrist, gripper)
 * - Arduino board (Uno/Mega recommended)
 * 
 * Command Protocol:
 * - Format: "SERVO,angle,angle,angle,angle,angle\n"
 * - Example: "SERVO,90,45,120,60,30\n"
 * - Each angle is in degrees (0-180)
 */

#include <Servo.h>

// Define servo pins
#define BASE_PIN 3
#define SHOULDER_PIN 5
#define ELBOW_PIN 6
#define WRIST_PIN 9
#define GRIPPER_PIN 10

// Define servo objects
Servo baseServo;
Servo shoulderServo;
Servo elbowServo;
Servo wristServo;
Servo gripperServo;

// Current servo positions
int basePos = 90;
int shoulderPos = 90;
int elbowPos = 90;
int wristPos = 90;
int gripperPos = 90;

// Movement speed control (delay in ms)
#define MOVE_DELAY 15

// Buffer for serial communication
String inputBuffer = "";
boolean stringComplete = false;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Attach servos to pins
  baseServo.attach(BASE_PIN);
  shoulderServo.attach(SHOULDER_PIN);
  elbowServo.attach(ELBOW_PIN);
  wristServo.attach(WRIST_PIN);
  gripperServo.attach(GRIPPER_PIN);
  
  // Move to home position
  moveToHome();
  
  Serial.println("READY");
}

void loop() {
  // Check for serial commands
  if (stringComplete) {
    processCommand(inputBuffer);
    inputBuffer = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputBuffer += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void processCommand(String command) {
  command.trim();
  
  if (command.startsWith("SERVO")) {
    // Parse servo angles
    int angles[5];
    int startIdx = 6; // Skip "SERVO,"
    int angleIdx = 0;
    
    for (int i = 0; i < 5; i++) {
      int commaIdx = command.indexOf(',', startIdx);
      if (commaIdx == -1 && i < 4) {
        Serial.println("ERROR:Invalid command format");
        return;
      }
      
      String angleStr;
      if (commaIdx == -1) {
        angleStr = command.substring(startIdx);
      } else {
        angleStr = command.substring(startIdx, commaIdx);
      }
      
      angles[i] = angleStr.toInt();
      startIdx = commaIdx + 1;
    }
    
    // Validate angles
    for (int i = 0; i < 5; i++) {
      if (angles[i] < 0 || angles[i] > 180) {
        Serial.println("ERROR:Angle out of range");
        return;
      }
    }
    
    // Move servos smoothly
    moveSmoothly(angles[0], angles[1], angles[2], angles[3], angles[4]);
    Serial.println("OK");
    
  } else if (command.equals("HOME")) {
    moveToHome();
    Serial.println("OK");
    
  } else if (command.equals("STATUS")) {
    Serial.print("STATUS:");
    Serial.print(basePos);
    Serial.print(",");
    Serial.print(shoulderPos);
    Serial.print(",");
    Serial.print(elbowPos);
    Serial.print(",");
    Serial.print(wristPos);
    Serial.print(",");
    Serial.println(gripperPos);
    
  } else if (command.equals("PING")) {
    Serial.println("PONG");
    
  } else {
    Serial.println("ERROR:Unknown command");
  }
}

void moveSmoothly(int base, int shoulder, int elbow, int wrist, int gripper) {
  // Calculate number of steps needed
  int maxSteps = max(max(max(max(
    abs(base - basePos),
    abs(shoulder - shoulderPos)),
    abs(elbow - elbowPos)),
    abs(wrist - wristPos)),
    abs(gripper - gripperPos));
  
  // Move in small increments
  for (int step = 0; step <= maxSteps; step++) {
    if (basePos != base) {
      int newPos = map(step, 0, maxSteps, basePos, base);
      baseServo.write(newPos);
    }
    if (shoulderPos != shoulder) {
      int newPos = map(step, 0, maxSteps, shoulderPos, shoulder);
      shoulderServo.write(newPos);
    }
    if (elbowPos != elbow) {
      int newPos = map(step, 0, maxSteps, elbowPos, elbow);
      elbowServo.write(newPos);
    }
    if (wristPos != wrist) {
      int newPos = map(step, 0, maxSteps, wristPos, wrist);
      wristServo.write(newPos);
    }
    if (gripperPos != gripper) {
      int newPos = map(step, 0, maxSteps, gripperPos, gripper);
      gripperServo.write(newPos);
    }
    delay(MOVE_DELAY);
  }
  
  // Update positions
  basePos = base;
  shoulderPos = shoulder;
  elbowPos = elbow;
  wristPos = wrist;
  gripperPos = gripper;
}

void moveToHome() {
  moveSmoothly(90, 90, 90, 90, 90);
}

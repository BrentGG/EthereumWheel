#include <AccelStepper.h>

// Define the stepper motor connections
#define STEP_PIN 2
#define DIR_PIN 3

// Create an instance of AccelStepper
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

// Variable to store the motor state (on/off)
bool motorOn = false;

void setup() {
  // Set the maximum speed and acceleration for the stepper motor
  stepper.setMaxSpeed(1000.0);
  stepper.setAcceleration(500.0);

  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  // Check if data is available on the serial port
  if (Serial.available() > 0) {
    // Read the incoming line from the serial port
    String input = Serial.readStringUntil('\n');
    
    // Find the first space separating the speed and chaos factor values
    int firstSpaceIndex = input.indexOf(' ');

    // Find the second space separating the chaos factor and motor state values
    int secondSpaceIndex = input.indexOf(' ', firstSpaceIndex + 1);

    // Extract the three values as strings
    String speedStr = input.substring(0, firstSpaceIndex);
    String chaosFactorStr = input.substring(firstSpaceIndex + 1, secondSpaceIndex);
    String motorStateStr = input.substring(secondSpaceIndex + 1);

    // Convert the strings to integers
    int speedPercentage = speedStr.toInt();
    int chaosFactor = chaosFactorStr.toInt();
    int motorState = motorStateStr.toInt();

    // Make sure the speed and chaos factor percentages are within the valid range (0 to 100)
    speedPercentage = constrain(speedPercentage, 0, 100);
    chaosFactor = constrain(chaosFactor, 0, 100);

    // Convert the percentages to values between 0 and the maximum speed/acceleration
    float targetSpeed = map(speedPercentage, 0, 100, 0, stepper.maxSpeed());
    float targetChaosFactor = map(chaosFactor, 0, 100, 0, stepper.maxSpeed());

    // Set the target speed and acceleration (chaos factor) for the stepper motor
    stepper.setSpeed(targetSpeed);
    stepper.setAcceleration(targetChaosFactor);

    // Set the motor state (on/off)
    motorOn = (motorState == 1);

    // Map the speed percentage to the number of steps (0 to 7)
    int stepsToTake = map(speedPercentage, 0, 100, 0, 7);

    // Make the motor take the mapped number of steps if motorOn is true
    if (motorOn) {
      stepper.move(stepsToTake);
      stepper.runToPosition();  // Move the motor to the new position
    }
  }
}

#include <AccelStepper.h>

// Define the stepper motor connections
#define STEP_PIN 2
#define DIR_PIN 3

// Create an instance of AccelStepper
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

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
    // Read the incoming value from the serial port
    int speedPercentage = Serial.parseInt();

    // Make sure the speed percentage is within the valid range (0 to 100)
    speedPercentage = constrain(speedPercentage, 0, 100);

    // Convert the speed percentage to a value between 0 and the maximum speed
    float targetSpeed = map(speedPercentage, 0, 100, 0, stepper.maxSpeed());

    // Set the target speed for the stepper motor
    stepper.setSpeed(targetSpeed);
  }

  // Update the stepper motor
  stepper.runSpeed();
}


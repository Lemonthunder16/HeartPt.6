#include <PulseSensorPlayground.h>

const int PulseWire = A0;  
const int LED = LED_BUILTIN;
int Threshold = 550;  

PulseSensorPlayground pulseSensor;

void setup() {   
    Serial.begin(115200);  
    pulseSensor.analogInput(PulseWire);
    pulseSensor.blinkOnPulse(LED);
    pulseSensor.setThreshold(Threshold);

    if (pulseSensor.begin()) {
        Serial.println("Pulse Sensor Initialized!");  
    }
}

void loop() {
    if (pulseSensor.sawStartOfBeat()) {  
        int myBPM = pulseSensor.getBeatsPerMinute();  

        Serial.print(myBPM);  
        Serial.println();   
    }

    delay(100);  // Adjust if needed
}

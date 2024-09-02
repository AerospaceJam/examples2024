#include <Arduino.h>
#define DECODE_NEC
#include <IRremote.hpp>

#define IR_PIN 6
#define ENABLE_LED_FEEDBACK false

int val;
unsigned long lastCommandTime = 0;
const unsigned long debounceDelay = 300; // Adjust as needed

void setup() {
    Serial.begin(9600);
    while (!Serial);
    pinMode(LED_BUILTIN, OUTPUT);
    IrReceiver.begin(IR_PIN, ENABLE_LED_FEEDBACK);
    Serial.println("Ready to receive IR commands.");
}

void flashLED(int times, int duration = 250) {
    for (int i = 0; i < times; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(duration);
        digitalWrite(LED_BUILTIN, LOW);
        delay(duration);
    }
}

void loop() {
    if (IrReceiver.decode()) {
        unsigned long currentTime = millis();

        if (IrReceiver.decodedIRData.protocol == UNKNOWN) {
            Serial.println(F("Received noise or an unknown (or not yet enabled) protocol"));
            IrReceiver.printIRResultRawFormatted(&Serial, true);
        } else {
            if (currentTime - lastCommandTime > debounceDelay) {
                val = IrReceiver.decodedIRData.command & 0x0F;
                Serial.print("Got value: ");
                Serial.println(val);
                flashLED(val);
                lastCommandTime = currentTime;
            }
            IrReceiver.printIRResultShort(&Serial);
            IrReceiver.printIRSendUsage(&Serial);
        }

        Serial.println();
        IrReceiver.resume();
    }
}

#include <IRremote.h>

#define IR_RECEIVER 2
#define RELAY_PIN 4

#define OPCODE_RELAY '0'
#define RELAY_TIME_DELAY 500
#define RESERVED_COMMAND 0x95

IRrecv receiver(IR_RECEIVER); 
decode_results results;

int incomingCommand = 0;
char incomingChar = 0;
unsigned long relay_millis_received = 0;
unsigned int relay_time_delay = 500;


// HOW IT WORKS:
// Serial is set to 250000 baud.
// When it receives IR signals it sends them via serial
// To send commands, send via serial, format commands is a char: command,length
//      Supported commands: 0 - enables relay

void setup() 
{
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, 1);

  Serial.begin(250000);

  receiver.enableIRIn(); // start receiving signals
}

void loop() 
{
  // Get 
  if(receiver.decode()) 
  {
    incomingCommand = receiver.decodedIRData.decodedRawData;
    if(incomingCommand==RESERVED_COMMAND){
        relay_millis_received = millis();
    }else{
        Serial.println(incomingCommand, HEX);
    }
    receiver.resume();
  }

  if(Serial.available() > 0){
    String recstr = Serial.readString();
    recstr.trim();
    sscanf(recstr.c_str(), "%c,%d",&incomingChar,&relay_time_delay);
    if(incomingChar == OPCODE_RELAY){
      relay_millis_received = millis();
    }
  }

  if(relay_millis_received != 0){
    if(millis() - relay_millis_received < relay_time_delay){
      digitalWrite(RELAY_PIN, 0);
    }else{
      digitalWrite(RELAY_PIN, 1);
      relay_millis_received = 0;
      relay_time_delay = RELAY_TIME_DELAY;
    }
  }
 
}

#include <Servo.h>
int pin_az=7;
int pin_el=8;
const int piezzo = 12;

char Serial_data_in[8];
const int N_char_serial = 8;
const int PIN_built_in_LED = 13;
int AZ_target = 90;
int EL_target = 90;
int EL = 90;
int AZ = 90;

Servo servo_az;
Servo servo_el;

void setup(){
  servo_az.attach(pin_az,550,2300);
  servo_el.attach(pin_el,650,2300);
  Serial.begin(57600);
  pinMode(PIN_built_in_LED, OUTPUT);
  pinMode(piezzo, OUTPUT);
}

static inline int8_t sgn(int val) {
 if (val < 0) return -1;
 if (val==0) return 0;
 return 1;
}

void loop(){
  if (Serial.available() > 0){
    int ii=0;
    digitalWrite(PIN_built_in_LED, HIGH);
    while (Serial.available() > 0) {
      Serial_data_in[ii]= Serial.read();
      ii++;
    }
    if (Serial_data_in[0] == 'R'){
    Serial.print("E");
    Serial.print(EL/100);
    Serial.print(EL%100/10);
    Serial.print(EL%10);
    Serial.print("A");
    Serial.print(AZ/100);
    Serial.print(AZ%100/10);
    Serial.print(AZ%10);
    digitalWrite(PIN_built_in_LED, LOW);
    }
    if (Serial_data_in[0]=='E' && Serial_data_in[4]=='A'){
    Serial.print("OK");
    EL_target = 100*((int)Serial_data_in[1]-48)+10*((int)Serial_data_in[2]-48)+((int)Serial_data_in[3]-48);
    AZ_target = 100*((int)Serial_data_in[5]-48)+10*((int)Serial_data_in[6]-48)+((int)Serial_data_in[7]-48);
    }
    else if(Serial_data_in[0] != 'E' && Serial_data_in[0] != 'R'){
    Serial.print("ERROR");
    tone(piezzo, 740); // Send 1KHz sound signal...
    delay(100);        // ...for 1 sec
    noTone(piezzo);     // Stop sound... 
    tone(piezzo, 1480); // Send 1KHz sound signal...
    delay(100);        // ...for 1 sec
    noTone(piezzo);     // Stop sound... 
    }
  AZ = AZ + sgn(int(AZ_target-AZ));
  EL = EL + sgn(int(EL_target-EL));
  servo_el.write(EL);
  servo_az.write(AZ);
  delay(10);
  }
  AZ = AZ + sgn(int(AZ_target-AZ));
  EL = EL + sgn(int(EL_target-EL));
  servo_el.write(EL);
  servo_az.write(AZ);
  delay(10);
}

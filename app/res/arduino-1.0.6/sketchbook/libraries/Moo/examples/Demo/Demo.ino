
#include "moo.h"                 //Scheduler
moo myOS;                        //Create istance

//LED variables
const byte LED10 = 10;
const byte LED11 = 11;
byte LEDstatus = 0;
byte LEDstatu2 = 0;

//Setup
void setup() {
    myOS.begin(); //Initialize scheduler
    //Setup pins
    pinMode(LED10,OUTPUT);
    pinMode(LED11,OUTPUT);
    //Add tasks
    myOS.addTask(flashLed, myOS.convertMs(1000));
   myOS.addTask(flashLed2,myOS.convertMs(300));
}

//Main loop
void loop() {


//EMPTY


}


//Task1
void flashLed() {
    LEDstatus ^= 1;
    digitalWrite(LED10, LEDstatus);
}

//Task2
void flashLed2(){
    LEDstatu2 ^= 1;
    digitalWrite(LED11, LEDstatu2);
}

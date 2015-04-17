/******************************************************************
 *                    Definition of variables                     *
 ******************************************************************/

/* Bauderate of the Bluetooth*/
#define BQ_ZUM_BLUETOOTH                       19200


/******************************************************************
 *                             Setup                              *
 ******************************************************************/

void setup() {
  
  /* Open the Bluetooth Serial and empty it */
  Serial.begin(BQ_ZUM_BLUETOOTH);  
  Serial.flush();     
  
}


/******************************************************************
 *                       Main program loop                        *
 ******************************************************************/

void loop() {
 
   /* If there is something in the Bluetooth serial port */
  if (Serial.available() > 0) { 
    Serial.print(Serial.read()); 
    Serial.flush();
  }
}  
  

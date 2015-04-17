/*
  Renacuajo
 */
#include <Servo.h>

Servo left; 
Servo right; 

void setup() {
  left.attach(12); 
  right.attach(13); 
      
  //forward: 
  left.write(0); 
  right.write(180);
  delay(1300); 
  
  for (int i=0; i<2;i++){
    //left
    left.write(180); 
    right.write(180);
    delay(300); 
     //forward: 
    left.write(0); 
    right.write(180);
    delay(300); 
  } 
  
  //stop & think
  left.write(0); 
  right.write(180);
  delay(10); 
  
     //left
    left.write(180); 
    right.write(180);
    delay(2900); 
    
    //forward: 
  left.write(0); 
  right.write(180);
  delay(800); 


     //right
    left.write(0); 
    right.write(0);
    delay(4400); 
 
 
 
  //stop & think
  left.write(0); 
  right.write(180);
  delay(10); 
  
  //backwards: 
  left.write(180); 
  right.write(0);
  delay(500); 
      //right
  left.write(0); 
  right.write(0);
  delay(480); 
  
     //backwards: 
  left.write(180); 
  right.write(0);
  delay(1000); 
    
    
  left.detach(); 
  right.detach();
}

// the loop routine runs over and over again forever:
void loop() {
}

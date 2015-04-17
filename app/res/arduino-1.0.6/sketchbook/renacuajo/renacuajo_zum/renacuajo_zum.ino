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
  delay(1200); 
  
  for (int i=0; i<2;i++){
    //left
    left.write(180); 
    right.write(180);
    delay(300); 
     //forward: 
    left.write(0); 
    right.write(180);
    delay(200); 
  } 
  
  //stop & think
  left.write(0); 
  right.write(180);
  delay(10); 
  
     //left
    left.write(180); 
    right.write(180);
    delay(2200); 
    
    //forward: 
  left.write(0); 
  right.write(180);
  delay(700); 


     //right
    left.write(0); 
    right.write(0);
    delay(3300); 
 
 
 
  //stop & think
  left.write(0); 
  right.write(180);
  delay(10); 
  
  //backwards: 
  left.write(180); 
  right.write(0);
  delay(350); 
      //right
  left.write(0); 
  right.write(0);
  delay(350); 
  
     //backwards: 
  left.write(180); 
  right.write(0);
  delay(1200); 
    
    
  left.detach(); 
  right.detach();
}

// the loop routine runs over and over again forever:
void loop() {
}

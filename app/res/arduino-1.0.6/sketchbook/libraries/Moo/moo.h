/*
	moo.h
    2014 pighixxx & bq
*/

#ifndef moo_H
#define moo_H


//Library version
#define moo_VERSION 110


//Arduino <=0023 or Arduino >=100
#if defined(ARDUINO) && (ARDUINO >= 100)
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

//Check compatibility
#if defined (__AVR_ATmega8__) || defined (__AVR_ATmega8A__)
#error This MCU is not supported!
#endif


//constants
const uint8_t PAUSED = 0;
const uint8_t SCHEDULED = 1; //0b00000001
const uint8_t SCHEDULED_IMMEDIATESTART = 5; //0b00000101
const uint8_t IMMEDIATESTART = SCHEDULED_IMMEDIATESTART; 
const uint8_t ONETIME = 2;



//class
class moo {
	public: 
		//Public
		moo();
        void begin(uint16_t resetTimeout = 0);
		uint8_t addTask(void (*)(void), unsigned long, uint8_t taskStatus = SCHEDULED);
		uint8_t removeTask(void (*)(void));
		uint8_t pauseTask(void (*)(void));
        uint8_t restartTask(void (*)(void));
		uint8_t modifyTask(void (*)(void), unsigned long, uint8_t oneTimeTask = NULL);
		uint8_t getTaskStatus(void (*)(void));
        uint32_t convertMs(uint32_t);
        void haltScheduler(void);
		void restartScheduler(void);
        void reset(void);
	private:
        //Private
        void setWDT();
        uint8_t setTask(void (*)(void), uint8_t, unsigned long taskInterval = NULL);
};


#endif

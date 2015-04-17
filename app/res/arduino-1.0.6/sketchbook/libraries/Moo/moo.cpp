/*
    moo.h
    2014 pighixxx & bq
*/

//Required libs
#include "moo.h"
#include <avr/wdt.h>
#include <avr/interrupt.h>

//Global settings
const uint8_t MAX_TASKS = 9;                    
#ifdef SIXTYFOUR_MATH
volatile unsigned long long _ticksCounter = 0;  
#else
volatile unsigned long _ticksCounter = 0; 
#endif
//Mac Interval
#define MAX_TASK_INTERVAL 225000UL

//Tasks variables
struct moo_core {
    void (*taskPointer)(void); 
    volatile unsigned long userTasksInterval; 

#ifdef SIXTYFOUR_MATH
    volatile unsigned long long plannedTask;
#else
    volatile unsigned long plannedTask;
#endif
    volatile uint8_t taskIsActive;
};
moo_core tasks[MAX_TASKS];
volatile uint8_t _numTasks; 
volatile uint8_t _initialized;
volatile uint16_t _wdtResetTimeout;
volatile uint8_t _taskIsRunning;
volatile uint16_t _maxTimeouts;

//Class constructor
moo::moo(void) {
	_initialized = 0;
}

//Class initialization
void moo::begin(uint16_t resetTimeout) {
	_wdtResetTimeout = resetTimeout;
    setWDT();
	_initialized = 1;
	_numTasks = 0;
	_taskIsRunning = 0;
}

//Add a task
uint8_t moo::addTask(void (*userTask)(void), unsigned long taskInterval, uint8_t taskStatus) {
	if ((_initialized == 0) || (_numTasks == MAX_TASKS)) {
		return 1; 
	}

	if ((taskInterval < 1) || (taskInterval > MAX_TASK_INTERVAL)) { 
		taskInterval = 1; 
	}

    if (taskStatus > SCHEDULED_IMMEDIATESTART) { 
        taskStatus = SCHEDULED;
    }
    SREG &= ~(1<<SREG_I);
	tasks[_numTasks].taskPointer = *userTask;
	tasks[_numTasks].taskIsActive = taskStatus & 0b00000011;
	tasks[_numTasks].userTasksInterval = taskInterval;
	tasks[_numTasks].plannedTask = _ticksCounter + ((taskStatus & 0b00000100)? 0 : taskInterval);
	_numTasks++;
    SREG |= (1<<SREG_I);
    return 0;
}

//Pause a task
uint8_t moo::pauseTask(void (*userTask)(void)) {
    return (setTask(userTask, 0));
}            
	
//Restart a task
uint8_t moo::restartTask(void (*userTask)(void)) {
    return (setTask(userTask, 1));
}

//Modify a task
uint8_t moo::modifyTask(void (*userTask)(void), unsigned long taskInterval, uint8_t oneTimeTask) {
    if ((oneTimeTask < SCHEDULED) && (oneTimeTask > ONETIME)) {
        oneTimeTask = NULL;
    }

	if ((taskInterval < 1) || (taskInterval > MAX_TASK_INTERVAL)) { 
		taskInterval = 1; 
	}
    SREG &= ~(1<<SREG_I);
    uint8_t tempI = 0;
    uint8_t _done = 1;
	do {
		if (tasks[tempI].taskPointer == *userTask) { 
            tasks[tempI].userTasksInterval = taskInterval;
            if (oneTimeTask != NULL) {
                tasks[tempI].taskIsActive = oneTimeTask;
            }
            tasks[tempI].plannedTask = _ticksCounter + taskInterval;
            _numTasks++;
            break;
            _done = 0;
        }
        tempI++;
    } while (tempI < _numTasks);
    SREG |= (1<<SREG_I); 
	return _done;
}

//Manage status
uint8_t moo::setTask(void (*userTask)(void), uint8_t tempStatus, unsigned long taskInterval) {
    if ((_initialized == 0) || (_numTasks == 0)) {
		return 1;
	}
    SREG &= ~(1<<SREG_I);
	uint8_t tempI = 0;
	do {
        if (tasks[tempI].taskPointer == *userTask) {
            tasks[tempI].taskIsActive = tempStatus;
            if (tempStatus == SCHEDULED) { 
				if (taskInterval == NULL) {
					tasks[_numTasks].plannedTask = _ticksCounter + tasks[tempI].userTasksInterval;
				} else {
					tasks[_numTasks].plannedTask = _ticksCounter + taskInterval;
				}
			}
            break;
        } else {
            tempI++;
    }
	} while (tempI < _numTasks);
    SREG |= (1<<SREG_I);
    return 0;
}    

//Remove a task
uint8_t moo::removeTask(void (*userTask)(void)) {
	if ((_initialized == 0) || (_numTasks == 0)) {
		return 1;
	}
    SREG &= ~(1<<SREG_I);
	uint8_t tempI = 0;
	do {
		if (tasks[tempI].taskPointer == *userTask) {
            if ((tempI + 1) == _numTasks) { 
                _numTasks--;
            } else if (_numTasks > 1) {
                for (uint8_t tempJ = tempI; tempJ < _numTasks; tempJ++) {
                    tasks[tempJ].taskPointer = tasks[tempJ + 1].taskPointer;
                    tasks[tempJ].taskIsActive = tasks[tempJ + 1].taskIsActive;
                    tasks[tempJ].userTasksInterval = tasks[tempJ + 1].userTasksInterval;
                    tasks[tempJ].plannedTask = tasks[tempJ + 1].plannedTask;
                }
                _numTasks -= 1;
            } else {
                _numTasks = 0;
            }
			break;
		} else {
			tempI++;
		}
	} while (tempI < _numTasks);
    SREG |= (1<<SREG_I); 
    return 0;
}

//Check if a task is running
uint8_t moo::getTaskStatus(void (*userTask)(void)) {
	if ((_initialized == 0) || (_numTasks == 0)) {
		return -1;
	}
    uint8_t tempJ = 255;
    SREG &= ~(1<<SREG_I); 
	uint8_t tempI = 0;
	do {
		if (tasks[tempI].taskPointer == *userTask) {
            tempJ = tasks[tempI].taskIsActive; 
            break;
        }
        tempI++;
    } while (tempI < _numTasks);
    SREG |= (1<<SREG_I);
    return tempJ;
}

//Convert in ticks
uint32_t moo::convertMs(uint32_t tempMs) {
    if (tempMs < 16) {
        return 1;
    }
	tempMs = tempMs >> 4;
    if (tempMs > MAX_TASK_INTERVAL) {
        return MAX_TASK_INTERVAL;
    } else {
        return tempMs;
    }
}

//Reset MCU
void moo::reset(void) {
    wdt_disable();
    wdt_enable(WDTO_30MS);
    while(1){}; //wait for reset
}

ISR(WDT_vect, ISR_NOBLOCK) {
	_ticksCounter++;
    if (_wdtResetTimeout ) {
        _WD_CONTROL_REG |= (1<<WDIE); 
        if (_taskIsRunning) {
            _maxTimeouts--;
            if (_maxTimeouts == 0) {
                _WD_CONTROL_REG &= ~(1<<WDIE);
            }
            return;
        }
    }
    //Scheduler	
	uint8_t tempI = 0;	
	do {
		if (tasks[tempI].taskIsActive > 0 ) { 
            
#ifdef SIXTYFOUR_MATH
			if (_ticksCounter > tasks[tempI].plannedTask) { 
#else
            if ((long)(_ticksCounter - tasks[tempI].plannedTask) >=0) { 
#endif
				_maxTimeouts = _wdtResetTimeout;
				_taskIsRunning = 1;
				tasks[tempI].taskPointer();
				_taskIsRunning = 0;
                if (tasks[tempI].taskIsActive == ONETIME) { 
                    if ((tempI + 1) == _numTasks) { 
                        _numTasks--;
                    } else if (_numTasks > 1) {
                        for (uint8_t tempJ = tempI; tempJ < _numTasks; tempJ++) {
                            tasks[tempJ].taskPointer = tasks[tempJ + 1].taskPointer;
                            tasks[tempJ].taskIsActive = tasks[tempJ + 1].taskIsActive;
                            tasks[tempJ].userTasksInterval = tasks[tempJ + 1].userTasksInterval;
                            tasks[tempJ].plannedTask = tasks[tempJ + 1].plannedTask;
                        }
                        _numTasks -= 1;
                    } else {
                        _numTasks = 0;
                    }
                } else {
                    tasks[tempI].plannedTask = _ticksCounter + tasks[tempI].userTasksInterval;
                }
			}
		}
	tempI++;
	} while (tempI < _numTasks);
}

/* 
****************
THIS IS THE CORE
****************
*/

//Set the WatchDog Timer
void moo::setWDT() {
    MCUSR = 0; 
    wdt_disable(); 
    SREG &= ~(1<<SREG_I); 
    byte _tempI = (1<<WDIE);
    if (_wdtResetTimeout) {
        _tempI |= (1<<WDE);
    } 
    _WD_CONTROL_REG = ((1<<_WD_CHANGE_BIT) | (1<<WDE));
    _WD_CONTROL_REG = _tempI;
    SREG |= (1<<SREG_I);
}

//Halt scheduler
void moo::haltScheduler() {
    SREG &= ~(1<<SREG_I);     
    wdt_disable(); 
    SREG |= (1<<SREG_I);
}

//Restart scheduler
void moo::restartScheduler() {
	if (_initialized) {
		setWDT();
	}
}

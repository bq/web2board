/* A simple ADC example that checks the analog reading on ADC0 and turns
 * an LED on if the reading is higher than a threshold value and turns if
 * off if it is under that value. */
#include <avr/io.h>
#include <stdint.h>
#include <util/delay.h>

/* Which analog pin we want to read from.  The pins are labeled "ADC0"
 * "ADC1" etc on the pinout in the data sheet.  In this case ADC_PIN
 * being 0 means we want to use ADC0.  On the ATmega328P this is also
 * the same as pin PC0 */
#define ADC_PIN			0
 
/* Just the pin we are going to be connecting the LED to PB0 is the same
 * as PIN0 but since we will be using PORTB it makes sense to use the 
 * name PB0 */
#define	LED_PIN		        DDB5
 
/* The ADC value we will consider the cutoff point for turning the LED
 * on or off.  The ADC we are using is 10-bits so can be a value from
 * 0 to 1023.  The value 0 means that there is no voltage on the ADC pin
 * and the value 1023 means the voltage has reached the voltage on the 
 * AREF pin. */
#define ADC_THRESHOLD	250
 
/* This function just keeps the reading code out of the loop itself.
 * It takes the analog pin number as a parameter and returns the
 * analog reading on that pin as a result.
 *
 * Look for its definition below main. */
uint16_t adc_read(uint8_t adcx);
 
int main(void) {
 
	/* Enable the ADC */
	ADCSRA |= _BV(ADEN);
 
	/* Set the LED pin as an output. */
	DDRB  |= _BV(LED_PIN);
 
 
	/* continually check if the ADC value is greater than the
	 * defined ADC_THRESHOLD value above.  If it is turn the LED on,
	 * if it isn't turn it off. */
	for (;;) {
 
		if (adc_read(ADC_PIN) > ADC_THRESHOLD)
			PORTB |= _BV(LED_PIN);
		else
			PORTB &= ~_BV(LED_PIN);
 
           _delay_ms(500);

    }
 
}
 
uint16_t adc_read(uint8_t adcx) {
	/* adcx is the analog pin we want to use.  ADMUX's first few bits are
	 * the binary representations of the numbers of the pins so we can
	 * just 'OR' the pin's number with ADMUX to select that pin.
	 * We first zero the four bits by setting ADMUX equal to its higher
	 * four bits. */
	ADMUX	&=	0xf0;
	ADMUX	|=	adcx;
 
	/* This starts the conversion. */
	ADCSRA |= _BV(ADSC);
 
	/* This is an idle loop that just wait around until the conversion
	 * is finished.  It constantly checks ADCSRA's ADSC bit, which we just
	 * set above, to see if it is still set.  This bit is automatically
	 * reset (zeroed) when the conversion is ready so if we do this in
	 * a loop the loop will just go until the conversion is ready. */
	while ( (ADCSRA & _BV(ADSC)) );
 
	/* Finally, we return the converted value to the calling function. */
	return ADC;
}

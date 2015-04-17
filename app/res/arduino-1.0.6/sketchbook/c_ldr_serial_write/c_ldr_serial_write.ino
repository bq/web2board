/* A simple ADC example that checks the analog reading on ADC0 and turns
 * an LED on if the reading is higher than a threshold value and turns if
 * off if it is under that value. */
#include <avr/io.h>
#include <stdint.h>
#include <util/delay.h>
#define BAUD 57600
#include <util/setbaud.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <stdbool.h>
#include <errno.h>


#define UINT16_MAX (65535U)
#define ADC_PIN			0
  
static void usart_init(void);
 
static void usart_tx(char c);
 
static void usart_puts(const char *s);
static bool str_to_uint16(const char *str, uint16_t *res);

/* This function just keeps the reading code out of the loop itself.
 * It takes the analog pin number as a parameter and returns the
 * analog reading on that pin as a result.
 *
 * Look for its definition below main. */
uint16_t adc_read(uint8_t adcx);
 
int main(void) {
 
	/* Enable the ADC */
	ADCSRA |= _BV(ADEN); 
         int i=0;
         char *str;
        usart_init();

	for (;;) {
          //usart_puts("hola");
          //itoa(i,str,10);
          //usart_puts(str);
          //itoa(adc_read(ADC_PIN),str,10);
          //usart_puts(str);
          //sprintf(str, "%u",  adc_read(ADC_PIN));
          //uint16_t analogValue = adc_read(ADC_PIN);
          //str[0]= (analogValue>>8);
          //str[1]= analogValue;
          uint16_t value=0x34EF;//adc_read(ADC_PIN);
          unsigned char buf[2];
buf[0] = (value >> 8); // 0x0A comes first
buf[1] = value;
          usart_puts(buf);
          usart_puts("\n");
          _delay_ms(1000);
          i++;  
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

static void usart_init(void)
{
    UBRR0H = UBRRH_VALUE;
    UBRR0L = UBRRL_VALUE;
#if USE_2X
    UCSR0A |= _BV(U2X0);
#else
    UCSR0A &= ~_BV(U2X0);
#endif
}
 
static void usart_tx(char c) {
    while(!(UCSR0A & _BV(UDRE0)));
    UDR0 = c;
}
 
static void usart_puts(const char *s)
{
    while(*s != '\0')
    {
        usart_tx(*s++);
    }
}


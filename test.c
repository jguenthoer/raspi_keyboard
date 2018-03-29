#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pigpio.h>

#define clock 15
#define data 23
#define bitmask 0x80

void isr_send(GPIO, level, tick, userdata)
{
	int tx = *userdata[0] & bitmask;
	tx = tx > 0;
	gpiowrite(data, tx); // write bit on falling edge
	end = gpioTick() - *userdata[2]; // timing for test
	*userdata[2] = gpioTick();
	*userdata[0] = *userdata[0] << 1; // shiftregister shift left
	*userdata[1] ++; //increase counter
	printf("Bit %s, Time %s, Counter %s", tx, end);
}


int send(command)
{
	gpioSetMode(data, PI_OUTPUT); // set data as output
	int userdata[2] = {0, 0, 0}; // [0]=shiftregister, [1]=counter, [2]=tick(only for test)
	userdata[0] = command;
	userdata[2] = gpioTick();
	gpioSetISRFuncEx(clock, 0, 50000, isr_send(), &userdata); // set interrupt for sending on falling edge
	gpioWrite(data, 1); // pull data high -> ready to send
	while (userdata[1]<8)
	{
		// wait for send to finish
		gpioSleep(PI_TIME_RELATIVE, 0, 400);
	}
	gpioSetISRFuncEx(clock, 0, 0, isr_send(), &userdata); //deregister ISR
	return 0;
	
}

int main()
{
	gpioInitialise();
	gpioSetMode(clock, PI_INPUT); //set clock as input
	gpioSetMode(data, PI_OUTPUT); // set data as output
	gpioSetPullUpDown(clock, PI_PUD_DOWN); // init pulldown for clock
	
	// check modelnumber for test
	gpioWrite(data, 0);
	gpioSleep(PI_TIME_RELATIVE, 2, 0);
	send(0x14);
	gpioSleep(PI_TIME_RELATIVE, 0, 1000);
	//model = receive();
	//printf("Modelnummer: %x \n", model);
	gpioTerminate();
}


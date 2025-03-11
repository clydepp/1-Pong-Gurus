#include "system.h"
#include "altera_up_avalon_accelerometer_spi.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_timer.h"
#include "altera_avalon_pio_regs.h"
#include "sys/alt_irq.h"
#include <stdlib.h>
#include <stdint.h>
#include "alt_types.h"
#include "sys/times.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>

// Define ADXL345 register addresses
#define DEVID_REGISTER        0x00
#define POWER_CTL_REGISTER    0x2D
#define DATA_FORMAT_REGISTER  0x31
#define BW_RATE_REGISTER      0x2C

#define OFFSET -32
#define PWM_PERIOD 16
#define NUM_TAPS 49 //5
#define CHARLIM 256    // Maximum character length of what the user places in memory.  Increase to allow longer sequences
#define QUITLETTER '~' // Letter to kill all processing

alt_8 pwm = 0;
alt_u8 led;
int level;

//float coefficients[NUM_TAPS] ={ 0.004641, 0.007377, -0.002408, -0.007110, 0.003266, 0.000061, -0.009358, 0.003975, 0.004379, -0.013316, 0.003048, 0.011436, -0.017929, -0.001074, 0.022260, -0.022477, -0.010874, 0.039597, -0.026322, -0.033757, 0.075199, -0.028898, -0.120355, 0.287922, 0.636863, 0.287922, -0.120355, -0.028898, 0.075199, -0.033757, -0.026322, 0.039597, -0.010874, -0.022477, 0.022260, -0.001074, -0.017929, 0.011436, 0.003048, -0.013316, 0.004379, 0.003975, -0.009358, 0.000061, 0.003266, -0.007110, -0.002408, 0.007377, 0.004641 };
    //coefficients given by Matlab
int16_t coefficients[NUM_TAPS] = { 152, 242, -79, -233, 107, 2, -307, 130, 143, -436, 100, 375, -587, -35, 729, -737, -356, 1298, -863, -1106, 2464, -947, -3944, 9435, 20869, 9435, -3944, -947, 2464, -1106, -863, 1298, -356, -737, 729, -35, -587, 375, 100, -436, 143, 130, -307, 2, 107, -233, -79, 242, 152 };

void led_write(alt_u8 led_pattern) {
    IOWR(LED_BASE, 0, led_pattern);
}

int32_t fir_filter(int16_t current_reading){
    static int16_t history[NUM_TAPS] = {0}; // Circular buffer to store the history of inputs
    static int index = 0;                // Current index in the circular buffer

    int32_t result = 0; //use large result to prevent overflow

    // Update the circular buffer with the current reading
    history[index] = current_reading;

    // Perform the convolution
    for (int i = 0; i < NUM_TAPS; i++) {
        int tap_index = (index - i + NUM_TAPS) % NUM_TAPS; // Circular indexing
        result += coefficients[i] * history[tap_index];
    }

    // Move to the next position in the circular buffer
    index = (index + 1) % NUM_TAPS;

    result = result >> 15; //divide by 2^15 for q1.15 fixed point representation
    return (int16_t)result; //cast back to 16 bit int
}

//filtered output
void convert_filter_read(alt_32 acc_read, int * level, alt_u8 * led) {
    acc_read += OFFSET;
    acc_read = fir_filter(acc_read);
    alt_u8 val = (acc_read >> 6) & 0x07;
    * led = (8 >> val) | (8 << (8 - val));
    * level = (acc_read >> 1) & 0x1f;
}

//non filtered output
void convert_read(alt_32 acc_read, int * level, alt_u8 * led) {
    acc_read += OFFSET;
    alt_u8 val = (acc_read >> 6) & 0x07;
    * led = (8 >> val) | (8 << (8 - val));
    * level = (acc_read >> 1) & 0x1f;
}

//void sys_timer_isr() {
//    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);
//
//    if (pwm < abs(level)) {
//
//        if (level < 0) {
//            led_write(led << 1);
//        } else {
//            led_write(led >> 1);
//        }
//
//    } else {
//        led_write(led);
//    }
//
//    if (pwm > PWM_PERIOD) {
//        pwm = 0;
//    } else {
//        pwm++;
//    }
//
//}

//void timer_init(void * isr) {
//
//    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0003);
//    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);
//    IOWR_ALTERA_AVALON_TIMER_PERIODL(TIMER_BASE, 0x0900);
//    IOWR_ALTERA_AVALON_TIMER_PERIODH(TIMER_BASE, 0x0000);
//    alt_irq_register(TIMER_IRQ, 0, isr);
//    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0007);
//
//}

int main() {

	alt_32 x_read;
    alt_up_accelerometer_spi_dev *acc_dev;
    acc_dev = alt_up_accelerometer_spi_open_dev("/dev/accelerometer_spi");
    if (acc_dev == NULL) {
        printf("Failed to open accelerometer device\n");
        return 1;
    }

//    timer_init(sys_timer_isr);

//    int x_read;
    while (1) {
//        if (alt_up_accelerometer_spi_read_x_axis(acc_dev, &x_read) == 0) {
        	alt_up_accelerometer_spi_read_x_axis(acc_dev, & x_read);
        	convert_filter_read(x_read, & level, & led);
            printf("Filtered X-axis data: 0x%04X\n", x_read);
//        } else {
//            printf("Failed to read X-axis data\n");
//        }

        usleep(1000); // 100 ms delay
    }

    return 0;
}

#include "system.h"
#include "altera_up_avalon_accelerometer_spi.h"
#include <stdio.h>

// Define ADXL345 register addresses
#define DEVID_REGISTER        0x00
#define POWER_CTL_REGISTER    0x2D
#define DATA_FORMAT_REGISTER  0x31
#define BW_RATE_REGISTER      0x2C



int main() {

    alt_up_accelerometer_spi_dev *acc_dev;
    acc_dev = alt_up_accelerometer_spi_open_dev("/dev/accelerometer_spi");
    if (acc_dev == NULL) {
        printf("Failed to open accelerometer device\n");
        return 1;
    }

    int x_read;
    while (1) {
        if (alt_up_accelerometer_spi_read_x_axis(acc_dev, &x_read) == 0) {
            printf("Raw X-axis data: 0x%04X\n", x_read);
        } else {
            printf("Failed to read X-axis data\n");
        }

        usleep(100000); // 100 ms delay
    }

    return 0;
}

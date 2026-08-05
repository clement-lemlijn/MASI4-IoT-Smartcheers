#include <stdio.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/uart.h"


#define UART_PORT UART_NUM_1

#define UART_TX_PIN GPIO_NUM_4
#define UART_RX_PIN GPIO_NUM_5


void uart_init(void)
{
    uart_config_t config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };


    uart_param_config(
        UART_PORT,
        &config
    );


    uart_set_pin(
        UART_PORT,
        UART_TX_PIN,
        UART_RX_PIN,
        UART_PIN_NO_CHANGE,
        UART_PIN_NO_CHANGE
    );


    uart_driver_install(
        UART_PORT,
        2048,
        0,
        0,
        NULL,
        0
    );
}



void app_main(void)
{
    printf("ESP32-H2 UART SENDER\n");


    uart_init();


    while(1)
    {

        char msg[] = "Hello world from H2\n";


        uart_write_bytes(
            UART_PORT,
            msg,
            strlen(msg)
        );


        printf("Sent : %s", msg);


        vTaskDelay(
            pdMS_TO_TICKS(1000)
        );
    }
}
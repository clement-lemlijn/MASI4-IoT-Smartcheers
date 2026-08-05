#include <stdio.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_adc/adc_oneshot.h"
#include "driver/gpio.h"
#include "rom/ets_sys.h"

#define SOUND_CHANNEL   ADC_CHANNEL_0   // GPIO1
#define DHT_GPIO        GPIO_NUM_10     // ← plus de conflit avec la LED RGB

static const char *TAG = "SENSORS";

// ========== DHT11 ==========
static esp_err_t dht11_read(float *temperature, float *humidity)
{
    uint8_t data[5] = {0};
    int i, j;

    gpio_set_direction(DHT_GPIO, GPIO_MODE_OUTPUT);
    gpio_set_level(DHT_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(20));
    gpio_set_level(DHT_GPIO, 1);
    ets_delay_us(30);
    gpio_set_direction(DHT_GPIO, GPIO_MODE_INPUT);

    int timeout = 0;
    while (gpio_get_level(DHT_GPIO) == 1) {
        if (++timeout > 100) return ESP_FAIL;
        ets_delay_us(1);
    }
    timeout = 0;
    while (gpio_get_level(DHT_GPIO) == 0) {
        if (++timeout > 100) return ESP_FAIL;
        ets_delay_us(1);
    }
    timeout = 0;
    while (gpio_get_level(DHT_GPIO) == 1) {
        if (++timeout > 100) return ESP_FAIL;
        ets_delay_us(1);
    }

    for (j = 0; j < 5; j++) {
        for (i = 0; i < 8; i++) {
            timeout = 0;
            while (gpio_get_level(DHT_GPIO) == 0) {
                if (++timeout > 100) return ESP_FAIL;
                ets_delay_us(1);
            }

            ets_delay_us(30);

            if (gpio_get_level(DHT_GPIO) == 1) {
                data[j] |= (1 << (7 - i));
            }

            timeout = 0;
            while (gpio_get_level(DHT_GPIO) == 1) {
                if (++timeout > 100) return ESP_FAIL;
                ets_delay_us(1);
            }
        }
    }

    if (data[4] != ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) {
        return ESP_FAIL;
    }

    *humidity    = data[0] + data[1] * 0.1f;
    *temperature = data[2] + data[3] * 0.1f;

    return ESP_OK;
}

void app_main(void)
{
    // --- ADC Sound Sensor ---
    adc_oneshot_unit_handle_t adc_handle;
    adc_oneshot_unit_init_cfg_t init_cfg = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_cfg, &adc_handle));

    adc_oneshot_chan_cfg_t chan_cfg = {
        .bitwidth = ADC_BITWIDTH_12,
        .atten = ADC_ATTEN_DB_12
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, SOUND_CHANNEL, &chan_cfg));

    // --- GPIO DHT11 ---
    gpio_reset_pin(DHT_GPIO);

    float temperature = 0, humidity = 0;
    int raw_sound;

    while (1) {
        long sum = 0;
        for (int i = 0; i < 32; i++) {
            adc_oneshot_read(adc_handle, SOUND_CHANNEL, &raw_sound);
            sum += raw_sound;
        }
        int sound_level = sum >> 5;

        if (dht11_read(&temperature, &humidity) == ESP_OK) {
            printf("Son: %4d | Temp: %.1f °C | Hum: %.1f %%\n",
                   sound_level, temperature, humidity);
        } else {
            printf("Son: %4d | Erreur lecture DHT11\n", sound_level);
        }

        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}

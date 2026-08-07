/*
 * OpenThread Router (jamais Leader) + Sensors
 * Temp/Humidity + Sound -> UDP Leader
 */

#include <stdio.h>
#include <string.h>

#include "sdkconfig.h"

#include "esp_err.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_openthread.h"
#include "esp_openthread_cli.h"
#include "esp_openthread_lock.h"
#include "esp_openthread_netif_glue.h"
#include "esp_openthread_types.h"
#include "esp_ot_config.h"
#include "esp_vfs_eventfd.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "nvs_flash.h"

#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "rom/ets_sys.h"

#include "openthread/instance.h"
#include "openthread/thread.h"
#include "openthread/ip6.h"
#include "openthread/udp.h"
#include "openthread/thread_ftd.h"

#define TAG "ot_sensor_router"
#define DEVICE_ID "esp32h2-102"

// ================= THREAD DATASET =================

static const char *THREAD_DATASET_HEX =
"0e080000000000010000000300000f4a0300000e35060004001fffe00208fdd2268ccf5c3c1a0708fd98867160c9fd5905103cfa545443917a8a19c20c45861f784a030f4f70656e5468726561642d34386339010248c90410f9d3cc0c80b6814babc34b148f3522b30c0402a0f7f8";

#define SENSOR_UDP_PORT 1234

// Poids de leader volontairement très bas : ce device peut être
// Router mais perdra toujours l'élection Leader face au device
// dédié (leader weight 200). Le défaut OpenThread est 64.
#define LOCAL_LEADER_WEIGHT 0


// ================= CAPTEURS =================

#define SOUND_CHANNEL ADC_CHANNEL_0
#define DHT_GPIO GPIO_NUM_10


static adc_oneshot_unit_handle_t adc_handle;


// ================= UDP =================

static otUdpSocket udp_socket;


// Convertit le dataset hex en TLV
static bool load_dataset(otInstance *instance)
{
    otOperationalDatasetTlvs dataset;

    size_t len = strlen(THREAD_DATASET_HEX) / 2;

    if(len > OT_OPERATIONAL_DATASET_MAX_LENGTH)
        return false;

    for(size_t i = 0; i < len; i++)
    {
        unsigned int value;
        sscanf(&THREAD_DATASET_HEX[i*2], "%02x", &value);
        dataset.mTlvs[i] = value;
    }

    dataset.mLength = len;

    otError err = otDatasetSetActiveTlvs(instance, &dataset);

    if(err != OT_ERROR_NONE)
    {
        ESP_LOGE(TAG,"Dataset error %d",err);
        return false;
    }

    return true;
}


// ================= DHT11 =================

static esp_err_t dht11_read(float *temperature,float *humidity)
{
    uint8_t data[5]={0};

    gpio_set_direction(DHT_GPIO, GPIO_MODE_OUTPUT);
    gpio_set_level(DHT_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(20));

    gpio_set_level(DHT_GPIO, 1);
    ets_delay_us(30);

    gpio_set_direction(DHT_GPIO, GPIO_MODE_INPUT);

    int timeout=0;

    while(gpio_get_level(DHT_GPIO))
    {
        if(++timeout>100)
            return ESP_FAIL;
        ets_delay_us(1);
    }

    while(!gpio_get_level(DHT_GPIO))
    {
        if(++timeout>200)
            return ESP_FAIL;
        ets_delay_us(1);
    }

    while(gpio_get_level(DHT_GPIO))
    {
        if(++timeout>300)
            return ESP_FAIL;
        ets_delay_us(1);
    }

    for(int j=0;j<5;j++)
    {
        for(int i=0;i<8;i++)
        {
            timeout=0;

            while(!gpio_get_level(DHT_GPIO))
            {
                if(++timeout>100)
                    return ESP_FAIL;
                ets_delay_us(1);
            }

            ets_delay_us(30);

            if(gpio_get_level(DHT_GPIO))
                data[j] |= (1<<(7-i));

            while(gpio_get_level(DHT_GPIO))
                ets_delay_us(1);
        }
    }

    if(data[4] != ((data[0]+data[1]+data[2]+data[3]) & 0xff))
        return ESP_FAIL;

    *humidity=data[0];
    *temperature=data[2];

    return ESP_OK;
}


// ================= UDP SEND =================

static void send_sensor_data(otInstance *instance, float temp, float hum, int sound)
{
    char payload[80];

    snprintf(payload, sizeof(payload),
        "Device:%s,Temp:%.1f,Hum:%.1f,Son:%d",
        DEVICE_ID, temp, hum, sound);

    otMessage *msg = otUdpNewMessage(instance, NULL);

    if(!msg)
        return;

    otMessageAppend(msg, payload, strlen(payload));

    otMessageInfo info;
    memset(&info, 0, sizeof(info));

    // multicast Thread
    otIp6AddressFromString("ff02::1", &info.mPeerAddr);
    info.mPeerPort = SENSOR_UDP_PORT;

    otError err = otUdpSendDatagram(instance, msg, &info);

    if(err==OT_ERROR_NONE)
    {
        ESP_LOGI(TAG, "UDP sent: %s", payload);
    }
    else
    {
        ESP_LOGE(TAG, "UDP error %d", err);
        otMessageFree(msg);
    }
}


// ================= SENSOR TASK =================

static void sensor_task(void *arg)
{
    otInstance *instance = esp_openthread_get_instance();

    while(1)
    {
        otDeviceRole role = otThreadGetDeviceRole(instance);

        if(role==OT_DEVICE_ROLE_CHILD ||
           role==OT_DEVICE_ROLE_ROUTER ||
           role==OT_DEVICE_ROLE_LEADER)
        {
            break;
        }

        vTaskDelay(pdMS_TO_TICKS(500));
    }

    ESP_LOGI(TAG, "Thread connected");

    while(1)
    {
        float temp,hum;
        int raw;
        long sum=0;

        for(int i=0;i<32;i++)
        {
            adc_oneshot_read(adc_handle, SOUND_CHANNEL, &raw);
            sum+=raw;
        }

        int sound=sum>>5;

        if(dht11_read(&temp,&hum)==ESP_OK)
        {
            printf("Temp %.1f Hum %.1f Sound %d\n", temp, hum, sound);

            esp_openthread_lock_acquire(portMAX_DELAY);
            send_sensor_data(instance, temp, hum, sound);
            esp_openthread_lock_release();
        }

        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}


// ================= THREAD =================

static void ot_task_worker(void *arg)
{
    esp_openthread_platform_config_t config =
    {
        .radio_config = ESP_OPENTHREAD_DEFAULT_RADIO_CONFIG(),
        .host_config  = ESP_OPENTHREAD_DEFAULT_HOST_CONFIG(),
        .port_config  = ESP_OPENTHREAD_DEFAULT_PORT_CONFIG(),
    };

    ESP_ERROR_CHECK(esp_openthread_init(&config));

    otInstance *instance = esp_openthread_get_instance();

    load_dataset(instance);

    // Reste éligible Router (comportement par défaut), mais avec un
    // poids de leader minimal : il ne gagnera jamais l'élection Leader
    // face au device dédié tant que celui-ci est joignable.
    otThreadSetLocalLeaderWeight(instance, LOCAL_LEADER_WEIGHT);

    otIp6SetEnabled(instance, true);
    otThreadSetEnabled(instance, true);

    esp_netif_t *netif = esp_netif_new(
        &(esp_netif_config_t) ESP_NETIF_DEFAULT_OPENTHREAD());

    esp_netif_attach(netif, esp_openthread_netif_glue_init(&config));

#if CONFIG_OPENTHREAD_CLI
    esp_openthread_cli_init();
    esp_openthread_cli_create_task();
#endif

    esp_openthread_launch_mainloop();

    vTaskDelete(NULL);
}


// ================= MAIN =================

void app_main(void)
{
    esp_vfs_eventfd_config_t cfg = { .max_fds=3 };

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_vfs_eventfd_register(&cfg));

    adc_oneshot_unit_init_cfg_t adc_cfg = { .unit_id=ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&adc_cfg, &adc_handle));

    adc_oneshot_chan_cfg_t chan_cfg = {
        .bitwidth=ADC_BITWIDTH_12,
        .atten=ADC_ATTEN_DB_12
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, SOUND_CHANNEL, &chan_cfg));

    gpio_reset_pin(DHT_GPIO);

    xTaskCreate(ot_task_worker, "ot_worker", 10240, NULL, 5, NULL);
    xTaskCreate(sensor_task, "sensor", 4096, NULL, 4, NULL);
}
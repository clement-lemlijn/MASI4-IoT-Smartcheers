/*
 * Leader - Auto Thread + réception automatique des données capteurs
 * + Relais des données reçues (UDP/Thread) vers UART1 (vers ESP32 VROOM)
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

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
#include "nvs_flash.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "driver/gpio.h"
#include "driver/uart.h"

#include "openthread/cli.h"
#include "openthread/instance.h"
#include "openthread/logging.h"
#include "openthread/tasklet.h"
#include "openthread/udp.h"
#include "openthread/ip6.h"
#include "openthread/thread.h"
#include "openthread/dataset.h"
#include "openthread/thread_ftd.h"

#define TAG "ot_leader"

// ===== COLLE ICI TON DATASET (celui qui marchait) =====
static const char *THREAD_DATASET_HEX =
    "0e080000000000010000000300000f4a0300000e35060004001fffe00208fdd2268ccf5c3c1a0708fd98867160c9fd5905103cfa545443917a8a19c20c45861f784a030f4f70656e5468726561642d34386339010248c90410f9d3cc0c80b6814babc34b148f3522b30c0402a0f7f8";

#define SENSOR_UDP_PORT 1234

// ===== Config UART vers l'ESP32 VROOM =====
#define UART_PORT     UART_NUM_1
#define UART_TX_PIN   GPIO_NUM_4
#define UART_RX_PIN   GPIO_NUM_5

static otUdpSocket s_udp_socket;

static void uart_bridge_init(void)
{
    uart_config_t config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };

    uart_param_config(UART_PORT, &config);

    uart_set_pin(
        UART_PORT,
        UART_TX_PIN,
        UART_RX_PIN,
        UART_PIN_NO_CHANGE,
        UART_PIN_NO_CHANGE
    );

    uart_driver_install(UART_PORT, 2048, 0, 0, NULL, 0);

    ESP_LOGI(TAG, "UART bridge initialized (TX=%d, RX=%d)", UART_TX_PIN, UART_RX_PIN);
}

// Callback quand un message UDP arrive (données réelles du capteur via Thread)
static void handle_udp_receive(void *aContext, otMessage *aMessage, const otMessageInfo *aMessageInfo)
{
    char buf[128];
    int length = otMessageRead(aMessage, otMessageGetOffset(aMessage), buf, sizeof(buf) - 1);
    if (length > 0) {
        buf[length] = '\0';
        printf(">>> RECU: %s\n", buf);

        // Relais de la donnée réelle vers l'ESP32 VROOM via UART
        uart_write_bytes(UART_PORT, buf, length);
        uart_write_bytes(UART_PORT, "\n", 1);

        printf("Sent to UART: %s\n", buf);
    }
}

static void start_udp_receiver(otInstance *instance)
{
    otSockAddr bind_addr;
    memset(&bind_addr, 0, sizeof(bind_addr));
    bind_addr.mPort = SENSOR_UDP_PORT;

    otError err = otUdpOpen(instance, &s_udp_socket, handle_udp_receive, NULL);
    if (err != OT_ERROR_NONE) {
        ESP_LOGE(TAG, "otUdpOpen failed: %d", err);
        return;
    }

    err = otUdpBind(instance, &s_udp_socket, &bind_addr, OT_NETIF_THREAD_HOST);
    if (err != OT_ERROR_NONE) {
        ESP_LOGE(TAG, "otUdpBind failed: %d", err);
        return;
    }

    ESP_LOGI(TAG, "UDP receiver started on port %d", SENSOR_UDP_PORT);
}

static void apply_dataset_and_start(otInstance *instance)
{
    otOperationalDatasetTlvs dataset_tlvs;
    size_t len = strlen(THREAD_DATASET_HEX) / 2;

    for (size_t i = 0; i < len; i++) {
        unsigned int byte;
        sscanf(&THREAD_DATASET_HEX[i * 2], "%02x", &byte);
        dataset_tlvs.mTlvs[i] = (uint8_t)byte;
    }
    dataset_tlvs.mLength = len;

    otError err = otDatasetSetActiveTlvs(instance, &dataset_tlvs);
    if (err != OT_ERROR_NONE) {
        ESP_LOGE(TAG, "otDatasetSetActiveTlvs failed: %d", err);
        return;
    }

    otIp6SetEnabled(instance, true);
    otThreadSetLocalLeaderWeight(instance, 200);
    otThreadSetEnabled(instance, true);

    ESP_LOGI(TAG, "Thread started with hardcoded dataset");
}

static esp_netif_t *init_openthread_netif(const esp_openthread_platform_config_t *config)
{
    esp_netif_config_t cfg = ESP_NETIF_DEFAULT_OPENTHREAD();
    esp_netif_t *netif = esp_netif_new(&cfg);
    assert(netif != NULL);
    ESP_ERROR_CHECK(esp_netif_attach(netif, esp_openthread_netif_glue_init(config)));
    return netif;
}

static void ot_task_worker(void *aContext)
{
    esp_openthread_platform_config_t config = {
        .radio_config = ESP_OPENTHREAD_DEFAULT_RADIO_CONFIG(),
        .host_config  = ESP_OPENTHREAD_DEFAULT_HOST_CONFIG(),
        .port_config  = ESP_OPENTHREAD_DEFAULT_PORT_CONFIG(),
    };

    ESP_ERROR_CHECK(esp_openthread_init(&config));

    otInstance *instance = esp_openthread_get_instance();

    // Appliquer le dataset + démarrer Thread
    apply_dataset_and_start(instance);

    // Démarrer le récepteur UDP automatique (relaie ensuite vers UART)
    start_udp_receiver(instance);

#if CONFIG_OPENTHREAD_CLI
    esp_openthread_cli_init();
    esp_openthread_cli_create_task();
#endif

    esp_netif_t *openthread_netif = init_openthread_netif(&config);
    esp_netif_set_default_netif(openthread_netif);

    esp_openthread_launch_mainloop();

    // cleanup
    esp_openthread_netif_glue_deinit();
    esp_netif_destroy(openthread_netif);
    esp_vfs_eventfd_unregister();
    vTaskDelete(NULL);
}

void app_main(void)
{
    esp_vfs_eventfd_config_t eventfd_config = { .max_fds = 3 };

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_vfs_eventfd_register(&eventfd_config));

    // Initialise l'UART AVANT de lancer le worker Thread
    uart_bridge_init();

    xTaskCreate(ot_task_worker, "ot_leader", 10240, NULL, 5, NULL);
}
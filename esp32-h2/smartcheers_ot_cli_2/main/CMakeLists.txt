idf_component_register(SRCS "esp_ot_cli.c"
                       INCLUDE_DIRS "."
                       REQUIRES nvs_flash esp_event esp_netif openthread driver esp_adc)

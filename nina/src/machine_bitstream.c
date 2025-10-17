#if MICROPY_PY_MACHINE_BITSTREAM

#include "py/mpconfig.h"
#include "py/mphal.h"
#include <stdio.h>

#define TICKS_PER_US    64

struct gpio_nrfx_cfg {
    struct gpio_driver_config common;
    NRF_GPIO_Type *reg;
};

void machine_bitstream_high_low(mp_hal_pin_obj_t pin, uint32_t *timing_ns, const uint8_t *buf, size_t len) {
    // Convert ns to clock ticks [high_time_0, period_0, high_time_1, period_1].
    for (size_t i = 0; i < 4; ++i) {
        timing_ns[i] = timing_ns[i] * TICKS_PER_US / 1000;
        if (i % 2 == 1) {
            // Convert low_time to period (i.e. add high_time).
            timing_ns[i] += timing_ns[i - 1];
        }
    }

    mp_hal_pin_output(pin);

    NRF_GPIO_Type *reg = ((struct gpio_nrfx_cfg *)pin->port->config)->reg;
    uint32_t mask = (1UL << pin->pin);

    // Enable DWT in debug core
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    uint8_t retries=5;
    while (retries--) {
        uint32_t start = DWT->CYCCNT;
        uint32_t cycles = 0;
        uint32_t total_cycles = 0;

        for (size_t i = 0; i < len; ++i) {
            uint8_t b = buf[i];
            for (size_t j = 0; j < 8; ++j) {
                uint8_t bit = b >> 6 & 2;
                uint32_t *t = &timing_ns[bit];
                cycles = DWT->CYCCNT;
                reg->OUTSET |= mask;
                while (DWT->CYCCNT - cycles < t[0]) {
                        ;
                }
                reg->OUTCLR |= mask;
                while (DWT->CYCCNT - cycles < t[1]) {
                        ;
                }
                total_cycles += t[1];
            }
        }

        // If total time longer than 25%, resend the whole data.
        // Since we are likely to be interrupted by SoftDevice
        cycles = DWT->CYCCNT - start;
        if (cycles < (total_cycles * 5) / 4) {
            break;
        }
printf("WARNING: resend! cycles=%u, total_cycles=%u\n", cycles, total_cycles);
        // re-send need 300us delay
        mp_hal_delay_us(300);
    }
}

#endif // MICROPY_PY_MACHINE_BITSTREAM

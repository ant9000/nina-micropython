#if MICROPY_PY_MACHINE_BITSTREAM

#include "py/mpconfig.h"
#include "py/mphal.h"
#include <stdio.h>

#include <nrfx_systick.h>
#define MP_HAL_BITSTREAM_TICKS_OVERHEAD  (10)

void machine_bitstream_high_low(mp_hal_pin_obj_t pin, uint32_t *timing_ns, const uint8_t *buf, size_t len) {
    uint32_t us_to_ticks = SystemCoreClock / 1000000;
    // Convert ns to clock ticks [high_time_0, period_0, high_time_1, period_1].
    for (size_t i = 0; i < 4; ++i) {
        timing_ns[i] = timing_ns[i] * us_to_ticks / 1000;
        if (timing_ns[i] > (2 * MP_HAL_BITSTREAM_TICKS_OVERHEAD)) {
            timing_ns[i] -= MP_HAL_BITSTREAM_TICKS_OVERHEAD;
        }
        if (i % 2 == 1) {
            // Convert low_time to period (i.e. add high_time).
            timing_ns[i] += timing_ns[i - 1] - MP_HAL_BITSTREAM_TICKS_OVERHEAD;
        }
    }

    mp_hal_pin_output(pin);
    for (size_t i = 0; i < len; ++i) {
        uint8_t b = buf[i];
        for (size_t j = 0; j < 8; ++j) {
            uint8_t bit = b >> 6 & 2;
            uint32_t *t = &timing_ns[bit];
            uint32_t start = nrf_systick_val_get();
            mp_hal_pin_write(pin, 1);
            while ((NRF_SYSTICK_VAL_MASK & (start - nrf_systick_val_get())) < t[0]);
            b <<= 1;
            mp_hal_pin_write(pin, 0);
            while ((NRF_SYSTICK_VAL_MASK & (start - nrf_systick_val_get())) < t[1]);
        }
    }
}

#endif // MICROPY_PY_MACHINE_BITSTREAM

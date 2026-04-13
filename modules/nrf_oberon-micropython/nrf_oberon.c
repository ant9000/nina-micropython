#include "py/mpconfig.h"

#if defined(MODULE_NRF_OBERON_ENABLED) && MODULE_NRF_OBERON_ENABLED == 1

#include <string.h>

#include "py/misc.h"
#include "py/obj.h"
#include "py/runtime.h"

#include <ocrypto_version.h>
#include <ocrypto_ed25519.h>

#define OCRYPTO_VERSION_MAJOR  ((OCRYPTO_VERSION_NUMBER & 0xFF000000) >> 24)
#define OCRYPTO_VERSION_MINOR  ((OCRYPTO_VERSION_NUMBER & 0x00FF0000) >> 16)
#define OCRYPTO_VERSION_PATCH  ((OCRYPTO_VERSION_NUMBER & 0x0000FFFF) >>  8)

static mp_obj_t nrf_oberon_ed25519_public_key(mp_obj_t seed_in) {
    mp_buffer_info_t seed;
    mp_get_buffer_raise(seed_in, &seed, MP_BUFFER_READ);
    if(seed.len != ocrypto_ed25519_SECRET_KEY_BYTES){
        mp_raise_ValueError(MP_ERROR_TEXT("Seed has the wrong size"));
    }

    uint8_t pk[ocrypto_ed25519_PUBLIC_KEY_BYTES];
    ocrypto_ed25519_public_key(pk, seed.buf);

    return mp_obj_new_bytes(pk, ocrypto_ed25519_PUBLIC_KEY_BYTES);
}
static MP_DEFINE_CONST_FUN_OBJ_1(nrf_oberon_ed25519_public_key_fun_obj, nrf_oberon_ed25519_public_key);

static mp_obj_t nrf_oberon_ed25519_sign(mp_obj_t seed_in, mp_obj_t publickey_in, mp_obj_t message_in) {
    mp_buffer_info_t seed;
    mp_get_buffer_raise(seed_in, &seed, MP_BUFFER_READ);
    if(seed.len != ocrypto_ed25519_SECRET_KEY_BYTES){
        mp_raise_ValueError(MP_ERROR_TEXT("Seed has the wrong size"));
    }
    mp_buffer_info_t pub;
    mp_get_buffer_raise(publickey_in, &pub, MP_BUFFER_READ);
    if(pub.len != ocrypto_ed25519_PUBLIC_KEY_BYTES){
        mp_raise_ValueError(MP_ERROR_TEXT("Public key has the wrong size"));
    }
    mp_buffer_info_t data;
    mp_get_buffer_raise(message_in, &data, MP_BUFFER_READ);

    vstr_t vstr;
    vstr_init_len(&vstr, ocrypto_ed25519_BYTES);
    ocrypto_ed25519_sign((uint8_t*)vstr.buf, data.buf, data.len, seed.buf, pub.buf);

    return mp_obj_new_bytes_from_vstr(&vstr);
}
static MP_DEFINE_CONST_FUN_OBJ_3(nrf_oberon_ed25519_sign_fun_obj, nrf_oberon_ed25519_sign);

static mp_obj_t nrf_oberon_ed25519_verify(mp_obj_t publickey_in, mp_obj_t signature_in, mp_obj_t message_in) {
    mp_buffer_info_t pub;
    mp_get_buffer_raise(publickey_in, &pub, MP_BUFFER_READ);
    if(pub.len != ocrypto_ed25519_PUBLIC_KEY_BYTES){
        mp_raise_ValueError(MP_ERROR_TEXT("Public key has the wrong size"));
    }
    mp_buffer_info_t sig;
    mp_get_buffer_raise(signature_in, &sig, MP_BUFFER_READ);
    if(sig.len != ocrypto_ed25519_BYTES){
        mp_raise_ValueError(MP_ERROR_TEXT("Signature has the wrong size"));
    }
    mp_buffer_info_t data;
    mp_get_buffer_raise(message_in, &data, MP_BUFFER_READ);

    if (ocrypto_ed25519_verify(sig.buf, data.buf, data.len, pub.buf) == 0) {
        return mp_const_true;
    }
    return mp_const_false;
}
static MP_DEFINE_CONST_FUN_OBJ_3(nrf_oberon_ed25519_verify_fun_obj, nrf_oberon_ed25519_verify);


static const mp_obj_tuple_t nrf_oberon_version_obj = {
    {&mp_type_tuple},
    3,
    {
        MP_OBJ_NEW_SMALL_INT(OCRYPTO_VERSION_MAJOR),
        MP_OBJ_NEW_SMALL_INT(OCRYPTO_VERSION_MINOR),
        MP_OBJ_NEW_SMALL_INT(OCRYPTO_VERSION_PATCH)
    }
};

static const mp_rom_map_elem_t nrf_oberon_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__),                  MP_ROM_QSTR(MP_QSTR_nrf_oberon)                          },
    { MP_ROM_QSTR(MP_QSTR_version),                   MP_ROM_PTR(&nrf_oberon_version_obj)                      },

    { MP_ROM_QSTR(MP_QSTR_ed25519_public_key),        MP_ROM_PTR(&nrf_oberon_ed25519_public_key_fun_obj)       },
    { MP_ROM_QSTR(MP_QSTR_ed25519_sign),              MP_ROM_PTR(&nrf_oberon_ed25519_sign_fun_obj)             },
    { MP_ROM_QSTR(MP_QSTR_ed25519_verify),            MP_ROM_PTR(&nrf_oberon_ed25519_verify_fun_obj)           },
};

static MP_DEFINE_CONST_DICT(
    mp_module_nrf_oberon_globals,
    nrf_oberon_globals_table
    );

const mp_obj_module_t mp_module_nrf_oberon = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_nrf_oberon_globals,
};

MP_REGISTER_MODULE(MP_QSTR_nrf_oberon, mp_module_nrf_oberon);

#endif /* defined(MODULE_NRF_OBERON_ENABLED) && MODULE_NRF_OBERON_ENABLED == 1 */

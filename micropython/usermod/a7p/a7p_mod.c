/* MicroPython User C Module (usermod) wrapping nanopb encode/decode for the
 * a7p profedit_Payload message -- the usermod counterpart of
 * ../../natmod/../src/a7p_mp.c. Same logic, different wiring: this uses the
 * standard module-registration API (py/runtime.h, MP_REGISTER_MODULE)
 * because it's compiled directly into the firmware, not loaded from a
 * separate .mpy via py/dynruntime.h.
 *
 * As in a7p_mp.c, this only ever touches the caller-supplied buffer through
 * pointers handed to pb_decode()/pb_encode()/a7p_validate() -- see that
 * file's header comment for the zero-copy rationale, which applies
 * identically here.
 */
#include "py/obj.h"
#include "py/runtime.h"

#include "profedit.pb.h"
#include "pb_decode.h"
#include "pb_encode.h"
#include "a7p_layout.h"
#include "a7p_validate_err.h"

static mp_obj_t a7p_decode(mp_obj_t buf_obj, mp_obj_t data_obj) {
    mp_buffer_info_t buf_info;
    mp_get_buffer_raise(buf_obj, &buf_info, MP_BUFFER_WRITE);
    if (buf_info.len < A7P_PAYLOAD_SIZE) {
        mp_raise_ValueError(MP_ERROR_TEXT("a7p: buffer too small for Payload"));
    }

    mp_buffer_info_t data_info;
    mp_get_buffer_raise(data_obj, &data_info, MP_BUFFER_READ);

    profedit_Payload *payload = (profedit_Payload *)buf_info.buf;
    pb_istream_t stream = pb_istream_from_buffer((const pb_byte_t *)data_info.buf, data_info.len);
    bool ok = pb_decode(&stream, &profedit_Payload_msg, payload);
    return mp_obj_new_bool(ok);
}
static MP_DEFINE_CONST_FUN_OBJ_2(a7p_decode_obj, a7p_decode);

static mp_obj_t a7p_encode(mp_obj_t buf_obj) {
    mp_buffer_info_t buf_info;
    mp_get_buffer_raise(buf_obj, &buf_info, MP_BUFFER_READ);
    if (buf_info.len < A7P_PAYLOAD_SIZE) {
        mp_raise_ValueError(MP_ERROR_TEXT("a7p: buffer too small for Payload"));
    }
    const profedit_Payload *payload = (const profedit_Payload *)buf_info.buf;

    size_t enc_size;
    if (!pb_get_encoded_size(&enc_size, &profedit_Payload_msg, payload)) {
        mp_raise_ValueError(MP_ERROR_TEXT("a7p: failed to size-encode Payload"));
    }

    uint8_t *scratch = m_malloc(enc_size);
    pb_ostream_t stream = pb_ostream_from_buffer(scratch, enc_size);
    bool ok = pb_encode(&stream, &profedit_Payload_msg, payload);
    mp_obj_t result = MP_OBJ_NULL;
    if (ok) {
        result = mp_obj_new_bytes(scratch, stream.bytes_written);
    }
    /* Unlike a7p_mp.c's dynruntime.h m_free(ptr) (single-arg macro over
     * m_free_dyn), the real py/misc.h m_free() takes the allocation size. */
    m_free(scratch, enc_size);
    if (!ok) {
        mp_raise_ValueError(MP_ERROR_TEXT("a7p: failed to encode Payload"));
    }
    return result;
}
static MP_DEFINE_CONST_FUN_OBJ_1(a7p_encode_obj, a7p_encode);

static mp_obj_t a7p_validate_fn(mp_obj_t buf_obj) {
    mp_buffer_info_t buf_info;
    mp_get_buffer_raise(buf_obj, &buf_info, MP_BUFFER_READ);
    if (buf_info.len < A7P_PAYLOAD_SIZE) {
        mp_raise_ValueError(MP_ERROR_TEXT("a7p: buffer too small for Payload"));
    }
    int code = a7p_validate((const profedit_Payload *)buf_info.buf);
    return mp_obj_new_int(code);
}
static MP_DEFINE_CONST_FUN_OBJ_1(a7p_validate_obj, a7p_validate_fn);

static const mp_rom_map_elem_t a7p_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR__a7p) },
    { MP_ROM_QSTR(MP_QSTR_PAYLOAD_SIZE), MP_ROM_INT(A7P_PAYLOAD_SIZE) },
    { MP_ROM_QSTR(MP_QSTR_decode), MP_ROM_PTR(&a7p_decode_obj) },
    { MP_ROM_QSTR(MP_QSTR_encode), MP_ROM_PTR(&a7p_encode_obj) },
    { MP_ROM_QSTR(MP_QSTR_validate), MP_ROM_PTR(&a7p_validate_obj) },
};
static MP_DEFINE_CONST_DICT(a7p_module_globals, a7p_module_globals_table);

const mp_obj_module_t a7p_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&a7p_module_globals,
};

/* Registers as `_a7p` (leading underscore, like the natmod build) --
 * src/a7p.py's `import _a7p` works identically whether that name resolves
 * to the natmod .mpy or this compiled-in module. */
MP_REGISTER_MODULE(MP_QSTR__a7p, a7p_user_cmodule);

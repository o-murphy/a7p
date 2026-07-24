/* MicroPython dynamic native module (natmod) wrapping nanopb encode/decode
 * for the a7p profedit_Payload message.
 *
 * This file only ever touches the caller-supplied buffer through pointers
 * handed to pb_decode()/pb_encode() -- it never copies profedit_Payload into
 * an intermediate representation. The Python side (a7p.py) allocates that
 * buffer once and overlays a uctypes struct on it, so decode() fills the
 * same memory Python reads fields from, and encode() reads the same memory
 * Python just wrote fields into.
 */
#include "py/dynruntime.h"

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
    m_free(scratch);
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

/* Entry point, called when the module is imported. */
mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args) {
    MP_DYNRUNTIME_INIT_ENTRY

    mp_store_global(MP_QSTR_PAYLOAD_SIZE, mp_obj_new_int_from_uint(A7P_PAYLOAD_SIZE));
    mp_store_global(MP_QSTR_decode, MP_OBJ_FROM_PTR(&a7p_decode_obj));
    mp_store_global(MP_QSTR_encode, MP_OBJ_FROM_PTR(&a7p_encode_obj));
    mp_store_global(MP_QSTR_validate, MP_OBJ_FROM_PTR(&a7p_validate_obj));

    MP_DYNRUNTIME_INIT_EXIT
}

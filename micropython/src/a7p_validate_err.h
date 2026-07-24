/* Hand-maintained: error codes returned by a7p_validate() (a7p_validate.c).
 * Bounds/thresholds referenced by that logic live in the generated
 * a7p_validate.h (tools/gen_validate.py) -- this file is just the shape
 * (which check failed), which isn't derivable from the schema alone. */
#ifndef A7P_VALIDATE_ERR_H_INCLUDED
#define A7P_VALIDATE_ERR_H_INCLUDED

#include "profedit.pb.h"

enum {
    A7P_VALID = 0,
    A7P_ERR_NO_PROFILE,
    A7P_ERR_ZERO_X,
    A7P_ERR_ZERO_Y,
    A7P_ERR_SC_HEIGHT,
    A7P_ERR_R_TWIST,
    A7P_ERR_TWIST_DIR,
    A7P_ERR_C_MUZZLE_VELOCITY,
    A7P_ERR_C_ZERO_TEMPERATURE,
    A7P_ERR_C_T_COEFF,
    A7P_ERR_C_ZERO_DISTANCE_IDX,
    A7P_ERR_C_ZERO_AIR_TEMPERATURE,
    A7P_ERR_C_ZERO_AIR_PRESSURE,
    A7P_ERR_C_ZERO_AIR_HUMIDITY,
    A7P_ERR_C_ZERO_W_PITCH,
    A7P_ERR_C_ZERO_P_TEMPERATURE,
    A7P_ERR_B_DIAMETER,
    A7P_ERR_B_WEIGHT,
    A7P_ERR_B_LENGTH,
    A7P_ERR_BC_TYPE,
    A7P_ERR_COEF_ROWS_COUNT,
    A7P_ERR_COEF_ROWS_BC_CD_RANGE,
    A7P_ERR_COEF_ROWS_MV_RANGE,
    A7P_ERR_COEF_ROWS_MV_DUPLICATE,
    A7P_ERR_SWITCHES_C_IDX,
    A7P_ERR_SWITCHES_ZOOM,
    A7P_ERR_SWITCHES_RETICLE_IDX,
    A7P_ERR_SWITCHES_DISTANCE,
    A7P_ERR_SWITCHES_DISTANCE_FROM,
    A7P_ERR_DISTANCES_RANGE,
};

/* Returns A7P_VALID (0), or the first A7P_ERR_* code that failed. */
int a7p_validate(const profedit_Payload *payload);

#endif

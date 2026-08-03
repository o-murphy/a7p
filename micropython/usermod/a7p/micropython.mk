# Makefile fragment for Make-based ports (unix, stm32, samd, nrf, mimxrt,
# alif, renesas-ra, psoc-edge, ...). Point USER_C_MODULES at the *parent*
# directory (micropython/usermod), not this one -- Make's USER_C_MODULES
# support globs `*/micropython.mk` one level down:
#
#   cd micropython/ports/unix
#   make USER_C_MODULES=/path/to/a7p/micropython/usermod
#
# nanopb isn't vendored (see ../../natmod/Makefile's fetch-nanopb) -- this
# fetches the same pinned commit into the same shared ../../natmod/nanopb/
# the first time this file is parsed (a plain $(shell) guarded by a
# does-it-exist check, so it runs once regardless of which port/build
# invokes it), so USER_C_MODULES=... is the only step needed.

A7P_MOD_DIR := $(USERMOD_DIR)
A7P_MICROPYTHON_DIR := $(A7P_MOD_DIR)/../..
A7P_SRC_DIR := $(A7P_MICROPYTHON_DIR)/src
A7P_NANOPB_DIR := $(A7P_MICROPYTHON_DIR)/natmod/nanopb
A7P_NANOPB_REPO := https://github.com/nanopb/nanopb.git
A7P_NANOPB_COMMIT := $(shell cat $(A7P_MICROPYTHON_DIR)/NANOPB_COMMIT)

ifeq ($(wildcard $(A7P_NANOPB_DIR)/pb.h),)
$(info a7p: fetching nanopb into $(A7P_NANOPB_DIR) ...)
$(shell rm -rf $(A7P_NANOPB_DIR) \
    && git init -q $(A7P_NANOPB_DIR) \
    && git -C $(A7P_NANOPB_DIR) remote add origin $(A7P_NANOPB_REPO) \
    && git -C $(A7P_NANOPB_DIR) fetch -q --depth 1 origin $(A7P_NANOPB_COMMIT) \
    && git -C $(A7P_NANOPB_DIR) checkout -q FETCH_HEAD)
ifeq ($(wildcard $(A7P_NANOPB_DIR)/pb.h),)
$(error a7p: failed to fetch nanopb into $(A7P_NANOPB_DIR) -- check network access, or run \
    "git -C $(A7P_NANOPB_DIR) fetch --depth 1 origin $(A7P_NANOPB_COMMIT) && git -C $(A7P_NANOPB_DIR) checkout FETCH_HEAD" \
    manually to see the underlying error)
endif
endif

# Scanned for MP_QSTR_/MP_REGISTER_MODULE.
SRC_USERMOD_C += $(A7P_MOD_DIR)/a7p_mod.c

# Not MicroPython-specific -- not scanned.
SRC_USERMOD_LIB_C += $(A7P_SRC_DIR)/profedit.pb.c
SRC_USERMOD_LIB_C += $(A7P_SRC_DIR)/a7p_validate.c
SRC_USERMOD_LIB_C += $(A7P_SRC_DIR)/md5.c
SRC_USERMOD_LIB_C += $(A7P_NANOPB_DIR)/pb_common.c
SRC_USERMOD_LIB_C += $(A7P_NANOPB_DIR)/pb_decode.c
SRC_USERMOD_LIB_C += $(A7P_NANOPB_DIR)/pb_encode.c

CFLAGS_USERMOD += -I$(A7P_SRC_DIR) -I$(A7P_NANOPB_DIR)

# Same flags as natmod/Makefile -- see the comment there for why both are
# required (PB_BUFFER_ONLY/PB_WITHOUT_64BIT: no callback/64-bit fields in
# profedit.proto; -fno-short-enums: keeps enum layout 4 bytes wide on ARM
# toolchains that default to packing them into 1, matching a7p_layout.h).
CFLAGS_USERMOD += -DPB_BUFFER_ONLY=1 -DPB_WITHOUT_64BIT=1 -fno-short-enums

# CFLAGS_USERMOD above is appended to the global CFLAGS while py.mk is
# parsed (py.mk:69), which on most ports is late enough to be the last
# -f[no-]short-enums on the command line (GCC honors whichever comes last).
# It isn't on every port, though: nrf's own Makefile appends its
# per-MCU-series CFLAGS (including -fshort-enums, unconditionally, for the
# Cortex-M0 variant used by e.g. MICROBIT) *after* including py.mk, silently
# winning over ours for the entire build -- caught as a build failure (every
# _Static_assert in a7p_layout.h mismatching, the same fingerprint as the
# original short-enums bug) rather than a silent bad decode, but a build
# failure all the same. Force it back for exactly our own object files via
# a target-specific variable, the same pattern nrf's own Makefile uses for
# nlr%.o -- these are evaluated per-recipe, after the whole Makefile's global
# CFLAGS is accumulated, so -fno-short-enums here is guaranteed to be last
# regardless of what any port appends afterwards.
A7P_ALL_SRC_C := $(A7P_MOD_DIR)/a7p_mod.c $(SRC_USERMOD_LIB_C)
A7P_PATHFIX_C := $(patsubst $(USER_C_MODULES)/%.c,%.c,$(A7P_ALL_SRC_C))
A7P_OBJS := $(addprefix $(BUILD)/,$(A7P_PATHFIX_C:.c=.o))
$(A7P_OBJS): CFLAGS += -fno-short-enums

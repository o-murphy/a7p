# Builds the `_a7p` MicroPython dynamic native module (.mpy) -- nanopb
# encode/decode of the a7p profedit_Payload message, for zero-copy uctypes
# access from ../src/a7p.py.
#
# Requires a local MicroPython checkout (for mpy-cross, mpy_ld.py and
# py/dynruntime.mk) -- point MPY_DIR at it:
#
#   git clone https://github.com/micropython/micropython
#   (cd micropython/mpy-cross && make)
#   make MPY_DIR=/path/to/micropython ARCH=x64
#
# ARCH is one of: x86, x64, armv6m, armv7m, armv7emsp, armv7emdp, xtensa,
# xtensawin, rv32imc, rv64imc (see $(MPY_DIR)/py/dynruntime.mk).
#
# `make dist` (the default) additionally mpy-cross-compiles the pure-Python
# a7p_layout.py/a7p.py wrapper for the target arch and drops everything under
# build/$(ARCH)/: _a7p.mpy, a7p_layout.mpy, a7p.mpy -- copy all three to the
# device (`import a7p` pulls in the other two).

ARCH    ?= x64
MPY_DIR ?= micropython

SRC_DIR    = ../src
NANOPB_DIR = ../nanopb

# vpath so dynruntime.mk computes objects as $(BUILD)/foo.o (arch-local under
# build/$(ARCH)/), not $(BUILD)/../src/foo.o -- the latter would be shared
# across arches and break rebuilding for a second ARCH.
vpath %.c $(SRC_DIR) $(NANOPB_DIR)

MOD_BASE = _a7p
MOD      = $(MOD_BASE)_$(ARCH)
BUILD    = build/$(ARCH)

SRC = a7p_mp.c profedit.pb.c pb_common.c pb_decode.c pb_encode.c

CFLAGS_EXTRA += -I$(SRC_DIR) -I$(NANOPB_DIR)

# profedit.proto has no 64-bit or callback/pointer fields, and this module
# only ever decodes/encodes a single in-memory buffer, so PB_BUFFER_ONLY
# strips nanopb's callback-stream machinery and PB_WITHOUT_64BIT its 64-bit
# varint paths -- both otherwise-dead code here. src/a7p_layout.h's offset
# guards and tools/gen_layout.py's generated offsets are only valid for a
# build using these same flags; keep them in sync if this ever changes.
#
# -fno-short-enums is required, not optional: arm-none-eabi-gcc packs the
# DType/GType/TwistDir enums into 1 byte by default (they fit in uint8),
# while x86_64 gcc defaults to 4-byte enums -- silently shifting every field
# offset from switches_count onward on ARM builds. Pinning 4-byte enums here
# keeps the one generated a7p_layout.py valid across every ARCH. If this ever
# gets dropped, the _Static_assert guards in a7p_layout.h will fail the build
# (as they did when this was caught) rather than silently mis-mapping fields.
CFLAGS_EXTRA += -DPB_BUFFER_ONLY=1 -DPB_WITHOUT_64BIT=1 -fno-short-enums

# Link libgcc/libm for compiler helper routines (e.g. soft integer division on
# targets without hardware divide). nanopb itself needs no libc beyond
# memcpy/memset/memmove, which mpy_ld.py resolves internally without this.
LINK_RUNTIME = 1

ifeq ($(wildcard $(MPY_DIR)/py/dynruntime.mk),)
ifeq ($(filter clean,$(MAKECMDGOALS)),clean)
else
$(error MPY_DIR="$(MPY_DIR)" not found -- set MPY_DIR=/path/to/micropython, see natmod/README.md)
endif
else
include $(MPY_DIR)/py/dynruntime.mk
endif

# dynruntime.mk compiles with no -MMD, so .o files only depend on their .c
# file. Force a rebuild when the generated offset guards change.
$(SRC_O): $(SRC_DIR)/a7p_layout.h

MPY_CROSS ?= $(MPY_DIR)/mpy-cross/build/mpy-cross

.PHONY: dist
dist: all
	mv $(MOD).mpy $(BUILD)/_a7p.mpy
	$(MPY_CROSS) -march=$(ARCH) $(SRC_DIR)/a7p_layout.py -o $(BUILD)/a7p_layout.mpy
	$(MPY_CROSS) -march=$(ARCH) $(SRC_DIR)/a7p.py -o $(BUILD)/a7p.mpy
	@echo "--> $(BUILD)/_a7p.mpy"
	@echo "--> $(BUILD)/a7p_layout.mpy"
	@echo "--> $(BUILD)/a7p.mpy"

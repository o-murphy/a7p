# Builds the `_a7p` MicroPython dynamic native module (.mpy) -- nanopb
# encode/decode of the a7p profedit_Payload message, for zero-copy uctypes
# access from ../src/a7p.py.
#
# nanopb itself isn't vendored in this repo -- `make fetch-nanopb` clones the
# pinned commit into ./nanopb (gitignored) the first time, matching what
# ../src/profedit.pb.h/.pb.c were generated against.
#
# Requires a local MicroPython checkout (for mpy-cross, mpy_ld.py and
# py/dynruntime.mk) -- point MPY_DIR at it:
#
#   git clone https://github.com/micropython/micropython
#   (cd micropython/mpy-cross && make)
#   make fetch-nanopb
#   make MPY_DIR=/path/to/micropython ARCH=x64 dist
#
# ARCH is one of: x86, x64, armv6m, armv7m, armv7emsp, armv7emdp, xtensa,
# xtensawin, rv32imc, rv64imc (see $(MPY_DIR)/py/dynruntime.mk).
#
# `dist` (the default target) additionally mpy-cross-compiles the pure-Python
# a7p.py wrapper for the target arch and drops both under build/$(ARCH)/:
# _a7p.mpy (native) + a7p.mpy (wrapper) -- copy both to the device
# (`import a7p` pulls in `_a7p`).

ARCH    ?= x64
MPY_DIR ?= micropython

SRC_DIR = ../src

# nanopb: fetched, not vendored -- see fetch-nanopb below. Pinned to the
# commit ../src/profedit.pb.h/.pb.c were generated against (nanopb-1.0.0-dev,
# PB_PROTO_HEADER_VERSION 40); bump it only alongside re-running
# scripts/generate_proto.sh and tools/gen_layout.py. Read from ../NANOPB_COMMIT
# (a single source of truth also read by ../usermod/a7p/micropython.mk and
# ../usermod/a7p/micropython.cmake) rather than duplicated here.
NANOPB_DIR    ?= nanopb
NANOPB_REPO   ?= https://github.com/nanopb/nanopb.git
NANOPB_COMMIT ?= $(shell cat ../NANOPB_COMMIT)

.PHONY: fetch-nanopb
fetch-nanopb:
	rm -rf $(NANOPB_DIR)
	git init -q $(NANOPB_DIR)
	git -C $(NANOPB_DIR) remote add origin $(NANOPB_REPO)
	git -C $(NANOPB_DIR) fetch -q --depth 1 origin $(NANOPB_COMMIT)
	git -C $(NANOPB_DIR) checkout -q FETCH_HEAD
	@echo "--> $(NANOPB_DIR) @ $(NANOPB_COMMIT)"

ifeq ($(wildcard $(NANOPB_DIR)/pb.h),)
ifeq ($(filter clean fetch-nanopb,$(MAKECMDGOALS)),)
$(error nanopb not found at "$(NANOPB_DIR)" -- run: make fetch-nanopb)
endif
endif

# vpath so dynruntime.mk computes objects as $(BUILD)/foo.o (arch-local under
# build/$(ARCH)/), not $(BUILD)/../src/foo.o -- the latter would be shared
# across arches and break rebuilding for a second ARCH.
vpath %.c $(SRC_DIR) $(NANOPB_DIR)

MOD_BASE = _a7p
MOD      = $(MOD_BASE)_$(ARCH)
BUILD    = build/$(ARCH)

SRC = a7p_mp.c a7p_validate.c profedit.pb.c pb_common.c pb_decode.c pb_encode.c

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
# memcpy/memset/memmove -- recent mpy_ld.py (unreleased as of MicroPython
# v1.28.0) resolves those internally regardless of what's linked; see the
# libc.a block below for versions that don't.
LINK_RUNTIME = 1

ifeq ($(wildcard $(MPY_DIR)/py/dynruntime.mk),)
ifeq ($(filter clean fetch-nanopb,$(MAKECMDGOALS)),)
$(error MPY_DIR="$(MPY_DIR)" not found -- set MPY_DIR=/path/to/micropython, see ../README.md)
endif
else
include $(MPY_DIR)/py/dynruntime.mk
endif

# On MicroPython versions whose mpy_ld.py doesn't special-case memcpy/memset/
# memmove internally (this was caught building against a pinned v1.28.0 in
# CI -- x64/rv32imc/rv64imc worked, armv6m/armv7m/armv7emsp/armv7emdp/xtensa/
# xtensawin failed with "undefined symbol: memset/memcpy"), those have to be
# resolved by linking an actual libc. dynruntime.mk's own LINK_RUNTIME only
# does that for picolibc/musl targets (rv32imc/rv64imc here already get
# libc.a for free); plain newlib ARM/Xtensa targets only get libm.a. Link
# newlib's libc.a explicitly for those so this doesn't depend on exactly
# which MicroPython version MPY_DIR points at. Native x64/x86 (glibc) never
# needed this -- small/bounded memcpy/memset there get inlined by gcc without
# an external symbol.
ifneq ($(filter armv6m armv7m armv7emsp armv7emdp xtensa xtensawin,$(ARCH)),)
MPY_LD_FLAGS += -l$(realpath $(shell $(CROSS)gcc $(CFLAGS) --print-file-name=libc.a))
endif

# dynruntime.mk compiles with no -MMD, so .o files only depend on their .c
# file. Force a rebuild when the generated offset guards / validation bounds
# change.
$(SRC_O): $(SRC_DIR)/a7p_layout.h $(SRC_DIR)/a7p_validate.h $(SRC_DIR)/a7p_validate_err.h

MPY_CROSS ?= $(MPY_DIR)/mpy-cross/build/mpy-cross

.PHONY: dist
dist: all
	mv $(MOD).mpy $(BUILD)/_a7p.mpy
	$(MPY_CROSS) -march=$(ARCH) $(SRC_DIR)/a7p.py -o $(BUILD)/a7p.mpy
	@echo "--> $(BUILD)/_a7p.mpy"
	@echo "--> $(BUILD)/a7p.mpy"

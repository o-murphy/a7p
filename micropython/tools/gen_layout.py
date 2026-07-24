#!/usr/bin/env python3
"""Regenerates micropython/src/a7p_layout.h and a7p_layout.py.

The nanopb generator lays out `struct _profedit_Profile` (and its
siblings) itself -- field order, padding and the width of `pb_size_t`
all come from profedit.pb.h / pb.h, not from us. To expose that memory
zero-copy through uctypes we need the *exact* byte offset and size of
every field as the host C compiler sees it.

Rather than hand-computing (and hand-maintaining) those offsets, this
script compiles a tiny probe program against the real headers using
offsetof()/sizeof(), runs it, and emits:

  - src/a7p_layout.h  C offset/size constants + _Static_assert guards,
                      included by src/a7p_mp.c
  - src/a7p_layout.py Python uctypes descriptor, imported by src/a7p.py

nanopb itself isn't vendored in this repo (see natmod/Makefile's
fetch-nanopb target) -- run that first, or pass --nanopb-dir to point
at any local nanopb checkout with the same pb.h this was generated
against (PB_PROTO_HEADER_VERSION 40).

Re-run this after regenerating profedit.pb.h from proto/profedit.proto
(scripts/generate_proto.sh) or after changing the PB_* build flags in
natmod/Makefile, so both the C guard and the Python view stay in
lockstep with whatever the compiler actually did.

Usage: python3 micropython/tools/gen_layout.py [--cc CC] [--nanopb-dir DIR]
"""
import argparse
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MICROPYTHON_DIR = os.path.dirname(HERE)
SRC_DIR = os.path.join(MICROPYTHON_DIR, "src")
DEFAULT_NANOPB_DIR = os.path.join(MICROPYTHON_DIR, "natmod", "nanopb")

# Same defines/flags the natmod build compiles profedit.pb.c with -- must
# match or the offsets below won't match the real build.
#
# -fno-short-enums matters: arm-none-eabi-gcc defaults to packing profedit_DType/
# GType/TwistDir into a single byte (they each fit in uint8), while x86_64 gcc
# defaults to 4-byte (int-sized) enums. Left unpinned, the exact same struct
# has a different memory layout per target architecture, which is silently
# wrong for a zero-copy view. Pinning 4-byte enums everywhere keeps one
# generated layout valid across every arch natmod/Makefile can target -- this
# was caught in practice by the _Static_assert guards in a7p_layout.h failing
# an armv7m build compiled without this flag.
PB_DEFINES = ["-DPB_BUFFER_ONLY=1", "-DPB_WITHOUT_64BIT=1", "-fno-short-enums"]

# (struct, field) pairs to probe, grouped by struct. Order here becomes
# the order of the generated uctypes descriptors.
STRUCTS = {
    "profedit_Payload": ["has_profile", "profile"],
    "profedit_Profile": [
        "profile_name", "cartridge_name", "bullet_name",
        "short_name_top", "short_name_bot", "user_note",
        "zero_x", "zero_y", "sc_height", "r_twist",
        "c_muzzle_velocity", "c_zero_temperature", "c_t_coeff",
        "c_zero_distance_idx", "c_zero_air_temperature",
        "c_zero_air_pressure", "c_zero_air_humidity",
        "c_zero_w_pitch", "c_zero_p_temperature",
        "b_diameter", "b_weight", "b_length",
        "twist_dir", "bc_type",
        "switches_count", "switches",
        "distances_count", "distances",
        "coef_rows_count", "coef_rows",
        "caliber", "device_uuid",
    ],
    "profedit_SwPos": ["c_idx", "reticle_idx", "zoom", "distance", "distance_from"],
    "profedit_CoefRow": ["bc_cd", "mv"],
}

PROBE_TEMPLATE = """\
#include <stdio.h>
#include <stddef.h>
#include "profedit.pb.h"

#define SZ(st) printf("SIZE %s %zu\\n", #st, sizeof(st))
#define OFF(st, f) printf("FIELD %s.%s %zu %zu\\n", #st, #f, offsetof(st, f), sizeof(((st*)0)->f))

int main(void) {{
    SZ(profedit_Payload);
    SZ(profedit_Profile);
    SZ(profedit_SwPos);
    SZ(profedit_CoefRow);
{probes}
    return 0;
}}
"""


def build_probe_source():
    lines = []
    for struct, fields in STRUCTS.items():
        for f in fields:
            lines.append(f"    OFF({struct}, {f});")
    return PROBE_TEMPLATE.format(probes="\n".join(lines))


def run_probe(cc, nanopb_dir):
    if not os.path.exists(os.path.join(nanopb_dir, "pb.h")):
        sys.exit(
            f"error: no pb.h under {nanopb_dir!r} -- nanopb isn't vendored in this repo, "
            f"run `make -C {os.path.join(MICROPYTHON_DIR, 'natmod')} fetch-nanopb` first "
            f"(or pass --nanopb-dir)"
        )
    with tempfile.TemporaryDirectory() as tmp:
        probe_c = os.path.join(tmp, "probe.c")
        probe_bin = os.path.join(tmp, "probe")
        with open(probe_c, "w") as f:
            f.write(build_probe_source())
        cmd = [cc, "-std=c99", *PB_DEFINES, "-I", nanopb_dir, "-I", SRC_DIR,
               probe_c, os.path.join(SRC_DIR, "profedit.pb.c"), "-o", probe_bin]
        subprocess.run(cmd, check=True)
        out = subprocess.run([probe_bin], check=True, capture_output=True, text=True).stdout
    sizes = {}
    fields = {}
    for line in out.splitlines():
        parts = line.split()
        if parts[0] == "SIZE":
            sizes[parts[1]] = int(parts[2])
        elif parts[0] == "FIELD":
            struct, field = parts[1].split(".")
            fields.setdefault(struct, {})[field] = (int(parts[2]), int(parts[3]))
    return sizes, fields


UCTYPES_SCALAR = {4: "INT32", 2: "UINT16", 1: "UINT8"}


def gen_header(sizes, fields):
    out = []
    out.append("/* AUTO-GENERATED by micropython/tools/gen_layout.py -- do not edit by hand. */")
    out.append("#ifndef A7P_LAYOUT_H_INCLUDED")
    out.append("#define A7P_LAYOUT_H_INCLUDED")
    out.append("")
    out.append("#include <stddef.h>")
    out.append("")
    out.append(f"#define A7P_PAYLOAD_SIZE  {sizes['profedit_Payload']}u")
    out.append(f"#define A7P_PROFILE_SIZE  {sizes['profedit_Profile']}u")
    out.append(f"#define A7P_SWPOS_SIZE    {sizes['profedit_SwPos']}u")
    out.append(f"#define A7P_COEFROW_SIZE  {sizes['profedit_CoefRow']}u")
    out.append("")
    out.append("/* Guards against nanopb ever changing this layout under us (e.g. a proto")
    out.append(" * edit that flips pb_size_t width via PB_FIELD_32BIT). If one of these ever")
    out.append(" * fails, re-run gen_layout.py -- the Python uctypes view depends on these")
    out.append(" * exact offsets matching. */")
    for struct, f in fields.items():
        for name, (offset, size) in f.items():
            macro = f"A7P_CHECK_{struct}_{name}".upper()
            out.append(
                f"_Static_assert(offsetof({struct}, {name}) == {offset} && "
                f"sizeof((({struct}*)0)->{name}) == {size}, \"{macro}\");"
            )
    out.append("")
    out.append("#endif")
    return "\n".join(out) + "\n"


def gen_python(sizes, fields):
    import_line = "import uctypes"
    out = []
    out.append("# AUTO-GENERATED by micropython/tools/gen_layout.py -- do not edit by hand.")
    out.append(import_line)
    out.append("")
    out.append(f"PAYLOAD_SIZE = {sizes['profedit_Payload']}")
    out.append(f"PROFILE_SIZE = {sizes['profedit_Profile']}")
    out.append(f"SWPOS_SIZE = {sizes['profedit_SwPos']}")
    out.append(f"COEFROW_SIZE = {sizes['profedit_CoefRow']}")
    out.append("")

    def scalar_type(size):
        return UCTYPES_SCALAR[size]

    # SwPos: c_idx/reticle_idx/zoom/distance int32 + distance_from enum (uint32-sized in C,
    # but only values 0/1 are valid -- store/read as UINT32 to stay a faithful zero-copy view)
    out.append("SWPOS_DESC = {")
    for name, (off, size) in fields["profedit_SwPos"].items():
        ctype = "UINT32" if name == "distance_from" else scalar_type(size)
        out.append(f'    "{name}": uctypes.{ctype} | {off},')
    out.append("}")
    out.append("")

    out.append("COEFROW_DESC = {")
    for name, (off, size) in fields["profedit_CoefRow"].items():
        out.append(f'    "{name}": uctypes.{scalar_type(size)} | {off},')
    out.append("}")
    out.append("")

    string_fields = {"profile_name", "cartridge_name", "bullet_name", "short_name_top",
                      "short_name_bot", "user_note", "caliber", "device_uuid"}

    out.append("# byte offset/size of the fixed char[] string fields -- sliced directly out")
    out.append("# of the backing bytearray (also zero-copy: bytearray slicing is a copy in")
    out.append("# CPython but MicroPython's bytearray supports memoryview slices; callers")
    out.append("# that want to mutate in place should use Profile.set_str()).")
    out.append("PROFILE_STRINGS = {")
    # iterate in struct field order (not set order, which varies by hash seed
    # across runs -- this generator's output should be deterministic)
    for name in fields["profedit_Profile"]:
        if name not in string_fields:
            continue
        off, size = fields["profedit_Profile"][name]
        out.append(f'    "{name}": ({off}, {size}),')
    out.append("}")
    out.append("")

    out.append("# PROFILE_DESC covers every scalar/enum field plus the three repeated")
    out.append("# arrays (as uctypes ARRAY-of-struct / ARRAY-of-scalar) for true zero-copy")
    out.append("# field access. String fields are intentionally left out of this")
    out.append("# descriptor -- see PROFILE_STRINGS above -- since uctypes has no")
    out.append("# fixed-char-array-as-str type.")
    out.append("PROFILE_DESC = {")
    for name, (off, size) in fields["profedit_Profile"].items():
        if name in string_fields:
            continue
        if name == "switches":
            count = size // sizes["profedit_SwPos"]
            out.append(f'    "switches": ({off} | uctypes.ARRAY, {count}, SWPOS_DESC),')
        elif name == "coef_rows":
            count = size // sizes["profedit_CoefRow"]
            out.append(f'    "coef_rows": ({off} | uctypes.ARRAY, {count}, COEFROW_DESC),')
        elif name == "distances":
            count = size // 4
            out.append(f'    "distances": ({off} | uctypes.ARRAY, {count} | uctypes.INT32),')
        elif name in ("twist_dir", "bc_type"):
            out.append(f'    "{name}": uctypes.UINT32 | {off},')
        elif name in ("switches_count", "distances_count", "coef_rows_count"):
            out.append(f'    "{name}": uctypes.{scalar_type(size)} | {off},')
        else:
            out.append(f'    "{name}": uctypes.{scalar_type(size)} | {off},')
    out.append("}")
    out.append("")

    payload_profile_off, _ = fields["profedit_Payload"]["profile"]
    payload_has_off, _ = fields["profedit_Payload"]["has_profile"]
    out.append("# Payload = {has_profile: bool, profile: Profile} -- the wire envelope every")
    out.append("# .a7p file's protobuf body decodes into.")
    out.append("PAYLOAD_DESC = {")
    out.append(f'    "has_profile": uctypes.UINT8 | {payload_has_off},')
    out.append(f'    "profile": ({payload_profile_off}, PROFILE_DESC),')
    out.append("}")
    out.append(f"PAYLOAD_PROFILE_OFFSET = {payload_profile_off}")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cc", default=os.environ.get("CC", "cc"))
    ap.add_argument("--nanopb-dir", default=DEFAULT_NANOPB_DIR,
                     help="path to a nanopb checkout with pb.h (default: natmod/nanopb, "
                          "see natmod/Makefile's fetch-nanopb target)")
    args = ap.parse_args()

    sizes, fields = run_probe(args.cc, args.nanopb_dir)

    header_path = os.path.join(SRC_DIR, "a7p_layout.h")
    py_path = os.path.join(SRC_DIR, "a7p_layout.py")
    with open(header_path, "w") as f:
        f.write(gen_header(sizes, fields))
    with open(py_path, "w") as f:
        f.write(gen_python(sizes, fields))
    print(f"wrote {header_path}")
    print(f"wrote {py_path}")


if __name__ == "__main__":
    main()

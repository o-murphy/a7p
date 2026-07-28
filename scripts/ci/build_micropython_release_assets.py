#!/usr/bin/env python3
"""Assemble micropython/ natmod release assets from a set of built .mpy files.

Each input .mpy (e.g. micropython/natmod/build/x64/a7p.mpy, see
micropython/natmod/Makefile's `dist` target) gets copied out under a
unique, flat name derived from its own header -- GitHub release assets
can't be nested in directories, and every arch's build otherwise produces
the same "a7p.mpy" filename -- and a package.json is written referencing
them, using the schema proposed upstream for per-entry native code
compatibility tags:
  https://github.com/micropython/micropython/pull/19532
  https://github.com/micropython/micropython-lib/pull/1144

The version/arch/abi tag for each file is read straight out of its own
on-disk header -- no running MicroPython interpreter, and no need to trust
a build directory's naming -- mirroring the validation mp_raw_code_load()
does in py/persistentcode.c. The on-disk layout is NOT the same as
sys.implementation._mpy (see read_mpy_tag() below), but composes into the
same shape.

Mirrors ballistics-lab/micropython-bclibc's own tools/build_release_assets.py
(this project's micropython/ follows that project's design throughout, see
micropython/README.md), adapted for this module's own name (`a7p`).

By default `urls` entries use bare filenames (no repo/host baked in): mip
resolves relative URLs against wherever it fetched package.json *from*
(base_url = package_json_url.rpartition("/")[0] in _install_json), and every
asset a GitHub release publishes -- package.json included -- lives under the
exact same .../releases/download/<tag>/ path. That keeps this portable across
forks/renames. Pass --repo to get absolute github.com/... URLs instead.

Usage:
    build_micropython_release_assets.py --tag v0.3.0 --out-dir DIR \\
        micropython/natmod/build/*/a7p.mpy
"""

import argparse
import json
import os
import shutil

# Standalone on purpose: this runs on the CI host under plain CPython, not
# on a MicroPython device -- unlike tools/mpy_target_tag.py's target_tag()
# (which reads sys.implementation._mpy on-device), so it doesn't import
# that module and instead keeps its own copy of the tiny arch-index table.
#
# Index must match py/persistentcode.h MP_NATIVE_ARCH_* ordering (0 = NONE).
_ARCH = (
    None,
    "x86",
    "x64",
    "armv6",
    "armv6m",
    "armv7m",
    "armv7em",
    "armv7emsp",
    "armv7emdp",
    "xtensa",
    "xtensawin",
    "rv32imc",
    "rv64imc",
)

# On-disk header (4 raw bytes) - py/persistentcode.h / persistentcode.c:
#   byte 0: 'M'                    magic
#   byte 1: MPY_VERSION            (== sys.implementation._mpy & 0xFF)
#   byte 2: feature byte:
#             bits 0-1: sub-version
#             bits 2-6: arch (mask 0x2F, per MPY_FEATURE_DECODE_ARCH)
#             bit 6:    arch-flags-follow marker (MPY_FEATURE_ARCH_FLAGS)
#   byte 3: MP_SMALL_INT_BITS      word size of the *building* platform -
#                                  not part of sys.implementation._mpy at all
#   [if feature bit 6 set]: arch_flags as a variable-length uint
#     (MicroPython's own varint: big-endian 7-bit groups, MSB = continue)
_ARCH_FLAGS_BIT = 0x40


def _read_varint(f):
    unum = 0
    while True:
        b = f.read(1)
        if not b:
            raise ValueError("truncated .mpy file (arch-flags field cut off)")
        byte = b[0]
        unum = (unum << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return unum


def read_mpy_tag(path):
    """Parse a .mpy file's header, return the same info a device that could
    run this exact file would report as sys.implementation._mpy, plus the
    arch name (from this module's own _ARCH table above).
    """
    with open(path, "rb") as f:
        header = f.read(4)
        if len(header) < 4 or header[0:1] != b"M":
            raise ValueError("not a .mpy file (bad magic): {!r}".format(path))

        version = header[1]
        feat = header[2]

        subver = feat & 3
        arch_idx = (feat >> 2) & 0x2F

        arch_flags = 0
        if feat & _ARCH_FLAGS_BIT:
            arch_flags = _read_varint(f)

    if arch_idx >= len(_ARCH) or _ARCH[arch_idx] is None:
        raise ValueError(
            "{!r}: not a native module (arch index {})".format(path, arch_idx)
        )

    return {
        "mpy": version | (subver << 8) | (arch_idx << 10) | (arch_flags << 16),
        "version": version,
        "subver": subver,
        "arch": _ARCH[arch_idx],
        "arch_flags": arch_flags,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", required=True, help="release tag, e.g. v0.3.0")
    ap.add_argument(
        "--repo",
        default=None,
        help="owner/repo -- if given, urls are absolute github.com/.../releases/"
        "download/<tag>/<asset> links; if omitted (default), urls are bare "
        "asset filenames, resolved by mip relative to wherever it fetched "
        "package.json from",
    )
    ap.add_argument(
        "--out-dir", required=True, help="directory to write release assets into"
    )
    ap.add_argument(
        "mpy_files", nargs="+", metavar="FILE.mpy", help="built native .mpy files"
    )
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    urls = []
    seen = {}

    for src in args.mpy_files:
        info = read_mpy_tag(src)
        asset_name = f"a7p_{info['arch']}.native.mpy"

        if asset_name in seen:
            raise SystemExit(
                f"duplicate arch {info['arch']!r}: {seen[asset_name]} and {src} "
                f"both produced {asset_name}"
            )
        seen[asset_name] = src

        shutil.copy(src, os.path.join(args.out_dir, asset_name))

        tag = info["mpy"]
        if args.repo:
            url = f"https://github.com/{args.repo}/releases/download/{args.tag}/{asset_name}"
        else:
            url = asset_name
        urls.append(["a7p.mpy", url, tag])
        print(
            f"{info['arch']}: abi={info['version']}.{info['subver']} tag={tag} -> {asset_name}"
        )

    package_json = {
        "urls": urls,
        "version": args.tag.lstrip("v"),
    }
    package_json_path = os.path.join(args.out_dir, "package.json")
    with open(package_json_path, "w") as f:
        json.dump(package_json, f, indent=2)
        f.write("\n")
    print(f"wrote {package_json_path} with {len(urls)} entries")


if __name__ == "__main__":
    main()

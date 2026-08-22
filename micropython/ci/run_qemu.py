#!/usr/bin/env python3
"""Run a test suite against the ports/qemu firmware, over the raw REPL.

That port has no filesystem, so `open("go/assets/example.a7p", "rb")` --
which every suite here does at import time -- raises OSError before a single
assertion runs. Nothing needs mounting for the module itself: a usermod is
linked into the firmware, unlike the .mpy an equivalent natmod runner has to
serve.

So the fixture is pushed into the target's globals and `open` is shadowed for
exactly that one path, falling through to the builtin for anything else. That
keeps the suites unmodified -- they still spell the path the same way they do
on every other target.

Only test_a7p_core.py is run: test_a7p.py additionally *writes* a roundtrip
file, which would need a writable VFS rather than a read shim, and
test_validate.py reads its own assets. Both are covered on every other target
in this workflow.

Usage: run_qemu.py <firmware.elf> [--suite test_a7p_core.py]
"""
import argparse
import os
import sys

# pyboard.py lives in MicroPython's tools/. MPY_DIR wins over the local guess,
# which matches how this workflow checks MicroPython out beside the repo.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
_MPY_ROOT = os.environ.get("MPY_DIR") or os.path.join(_REPO, "mpy")
sys.path.insert(0, os.path.join(_MPY_ROOT, "tools"))

from pyboard import Pyboard  # noqa: E402

ASSET = "go/assets/example.a7p"


def read_file(path):
    with open(path, "rb") as f:
        return f.read()


def inject_asset(data):
    """Push the fixture and shadow open() for its path only.

    Sent as a handful of statements rather than one expression: the raw REPL
    buffers whatever it is handed, and the asset is several KB.
    """
    return (
        b"__asset = " + repr(data).encode() + b"\n"
        b"class _R:\n"
        b"  def __init__(s, d): s.d = d\n"
        b"  def read(s, *a): return s.d\n"
        b"  def close(s): pass\n"
        b"  def __enter__(s): return s\n"
        b"  def __exit__(s, *a): pass\n"
        b"_builtin_open = open\n"
        b"def open(p, m='r'):\n"
        b"  if p == " + repr(ASSET).encode() + b": return _R(__asset)\n"
        b"  return _builtin_open(p, m)\n"
        b"import gc; gc.collect()\n"
    )


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("firmware", help="path to firmware.elf")
    ap.add_argument("--suite", default="test_a7p_core.py")
    ap.add_argument("--machine", default="mps2-an385")
    args = ap.parse_args()

    tests = os.path.join(_REPO, "micropython", "tests")
    asset = read_file(os.path.join(_REPO, ASSET))
    suite = read_file(os.path.join(tests, args.suite))

    qemu_cmd = (
        "qemu-system-arm -machine %s -nographic -monitor null -semihosting "
        "-serial pty -kernel %s" % (args.machine, args.firmware)
    )
    print("[QEMU] %s" % qemu_cmd, flush=True)

    pyb = Pyboard("execpty:" + qemu_cmd)
    pyb.enter_raw_repl()
    try:
        print("[QEMU] injecting %s (%d bytes) ..." % (ASSET, len(asset)), flush=True)
        pyb.exec_(inject_asset(asset), timeout=60)

        print("[QEMU] running %s ..." % args.suite, flush=True)
        out = pyb.exec_(suite, timeout=600)
        text = out.decode(errors="replace")
        print(text, end="" if text.endswith("\n") else "\n", flush=True)
    finally:
        pyb.exit_raw_repl()
        pyb.close()

    # The suites signal success by printing OK rather than by exit status --
    # they are written to run under a plain interpreter too.
    if "OK" not in text:
        print("[QEMU] RESULT: FAILED", file=sys.stderr)
        return 1
    print("[QEMU] RESULT: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

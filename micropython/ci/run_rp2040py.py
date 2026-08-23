#!/usr/bin/env python3
"""Run a suite against the ports/rp2 firmware under the rp2040py emulator.

    python3 micropython/ci/run_rp2040py.py <firmware.uf2> [--suite test_a7p_core.py]

Unlike ci/run_qemu.py, this does not drive the raw REPL itself: rp2040py's
`micropython <file>` mode already pushes a script to the emulated device and
runs it in place. What it does need is the fixture, and that cannot ride along
as a file -- `rp2040py mklittlefs` only accepts .py/.mpy/.js, so a .a7p blob
has no way into the image. Same answer as run_qemu.py, then: the asset is
inlined into the script and open() is shadowed for that one path, falling
through to the builtin for everything else so the suite stays unmodified and
still spells the path the way it does everywhere else.

The prelude and the suite are concatenated into one temporary file, because
that mode takes exactly one script.
"""

import argparse
import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))

ASSET = "go/assets/example.a7p"


def read_file(path):
    with open(path, "rb") as f:
        return f.read()


def prelude(data):
    """The fixture, plus an open() that serves it from memory."""
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
    ap.add_argument("firmware", help="path to firmware.uf2")
    ap.add_argument("--suite", default="test_a7p_core.py")
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()

    tests = os.path.join(_REPO, "micropython", "tests")
    asset = read_file(os.path.join(_REPO, ASSET))
    suite = read_file(os.path.join(tests, args.suite))

    combined = prelude(asset) + b"\n" + suite
    fd, path = tempfile.mkstemp(prefix="a7p_rp2040_", suffix=".py")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(combined)

        print("[rp2040py] %s + %s (%d bytes of fixture) -> %s"
              % (args.suite, ASSET, len(asset), path), flush=True)
        cmd = ["rp2040py", "micropython", "--image", args.firmware, path]
        print("[rp2040py] %s" % " ".join(cmd), flush=True)

        proc = subprocess.run(cmd, capture_output=True, timeout=args.timeout)
        text = (proc.stdout + proc.stderr).decode(errors="replace")
        print(text, end="" if text.endswith("\n") else "\n", flush=True)
    finally:
        os.unlink(path)

    # The suite signals success by printing OK rather than by exit status: it
    # is written to run under a plain interpreter too, and MicroPython's raw
    # REPL swallows an uncaught SystemExit without a traceback anyway, so
    # rp2040py's own exit code cannot be relied on to carry a failure. Same
    # check ci/run_qemu.py makes, and the same reasoning behind
    # micropython-bclibc's rp2040 job grepping its output.
    if "OK" not in text or "Traceback" in text:
        print("[rp2040py] RESULT: FAILED", file=sys.stderr)
        sys.exit(1)
    print("[rp2040py] RESULT: PASSED")


if __name__ == "__main__":
    main()

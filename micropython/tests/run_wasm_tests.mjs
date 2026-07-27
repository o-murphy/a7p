// Runs tests/test_a7p.py and tests/test_validate.py against a built
// ports/webassembly micropython.mjs, via Node's ESM loader + the wasm
// build's own JS API (loadMicroPython/runPython) -- webassembly has no
// standalone interpreter binary to invoke a .py file with directly, unlike
// every other port these tests run against (unix, for both natmod and
// usermod).
//
// The test logic itself lives entirely in test_a7p.py/test_validate.py --
// this script is only a harness translating between Node's filesystem and
// the wasm build's in-memory FS (Emscripten's FS.writeFile), so there is
// exactly one copy of what "passing" means, run three different ways
// (natmod/unix, usermod/unix, usermod/webassembly).
//
// Usage (run from the repo root):
//   node micropython/tests/run_wasm_tests.mjs path/to/micropython.mjs
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const mjsPath = process.argv[2];
if (!mjsPath) {
    console.error("usage: node run_wasm_tests.mjs <path-to-micropython.mjs>");
    process.exit(2);
}

const { loadMicroPython } = await import(pathToFileURL(mjsPath).href);
const mp = await loadMicroPython();

// test_a7p.py/test_validate.py open this exact relative path (both are
// written to run from the repo root, same as every other port's test step).
// Emscripten's FS.writeFile doesn't create parent directories itself.
mp.FS.mkdirTree("go/assets");
mp.FS.writeFile("go/assets/example.a7p", readFileSync("go/assets/example.a7p"));

// test_a7p.py/test_validate.py need a7p.load/dump's md5 checksum, which
// used to mean hashlib.md5 -- unavailable on the webassembly port's stock
// config (MICROPY_PY_SSL off by default) and the reason this used to only
// run test_a7p_core.py here. a7p.load/dump now use the module's own
// vendored md5 (_a7p.md5(), src/md5.c) instead of hashlib, so all three
// run the same way as every other port.
for (const script of [
    "micropython/tests/test_a7p_core.py",
    "micropython/tests/test_a7p.py",
    "micropython/tests/test_validate.py",
]) {
    const source = readFileSync(script, "utf8");
    try {
        mp.runPython(source);
    } catch (e) {
        console.error(`FAILED: ${script}`);
        console.error(e.message ?? e);
        process.exit(1);
    }
    console.log(`OK: ${script}`);
}

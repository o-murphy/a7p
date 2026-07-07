// Regenerates src/generated/a7p_schema_validator.{js,d.ts} from
// ../schema/a7p.schema.json (the canonical copy, shared with py/dart --
// see docs/DESIGN-schema-unification.md at the a7p-cross repo root).
//
// Run after editing the schema (only works when js/ is checked out inside
// an a7p-cross tree, same constraint as build:proto):
//   node scripts/build_schema_validator.mjs
//
// There's no `ajv compile --standalone` CLI flag (ajv-cli's --spec= only
// covers draft7/draft2019-09, not the draft 2020-12 our schema uses) --
// this goes through ajv's JS API directly instead: Ajv2020 (2020-12
// support) + standaloneCode() (the actual "compile schema to a
// self-contained module, no ajv runtime dependency needed to execute it"
// feature). `strict: false` is required: our schema uses x-* vendor
// extensions (x-fraction-digits, x-unit, x-decision, ...) that ajv's
// strict mode rejects as unknown keywords.
//
// Output is CommonJS (.cjs), not ESM, even though the rest of this package
// is "type": "module" -- ajv's `code.esm: true` option still leaves a bare
// `require("ajv/dist/runtime/ucs2length")` in the emitted code for
// Unicode-aware maxLength/minLength checks, which crashes under Node's ESM
// loader ("require is not defined in ES module scope"). Node's ESM loader
// can `import` a `.cjs` file directly (it's wrapped as the default export),
// so this doesn't block validate.ts from consuming it -- verified against
// a real build (`dist_smoke_test.mjs` at the time this was written).
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import Ajv2020 from 'ajv/dist/2020.js';
import standaloneCode from 'ajv/dist/standalone/index.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.dirname(here); // js/
const schemaPath = path.join(repoRoot, '..', 'schema', 'a7p.schema.json');
const outDir = path.join(repoRoot, 'src', 'generated');

const schema = JSON.parse(readFileSync(schemaPath, 'utf8'));

const ajv = new Ajv2020({
  code: { source: true },
  allErrors: true,
  strict: false,
});
const validate = ajv.compile(schema);
const moduleCode = standaloneCode(ajv, validate);

const header =
  '// GENERATED FILE -- DO NOT EDIT BY HAND.\n' +
  '// Source:      schema/a7p.schema.json\n' +
  '// Regenerate:  node scripts/build_schema_validator.mjs (or python scripts/compile.py --ts from the repo root)\n\n';

writeFileSync(path.join(outDir, 'a7p_schema_validator.cjs'), header + moduleCode);

const dts =
  header +
  `export interface A7pSchemaError {
  instancePath: string;
  schemaPath: string;
  keyword: string;
  params: Record<string, unknown>;
  message?: string;
}

export interface A7pSchemaValidateFunction {
  (data: unknown): boolean;
  errors?: A7pSchemaError[] | null;
}

export declare const validate: A7pSchemaValidateFunction;
export default validate;
`;

writeFileSync(path.join(outDir, 'a7p_schema_validator.d.cts'), dts);

console.log(`wrote ${outDir}/a7p_schema_validator.{cjs,d.cts} (${moduleCode.length} bytes embedded)`);

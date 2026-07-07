// GENERATED FILE -- DO NOT EDIT BY HAND.
// Source:      schema/a7p.schema.json
// Regenerate:  node scripts/build_schema_validator.mjs (or python scripts/compile.py --ts from the repo root)

export interface A7pSchemaError {
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

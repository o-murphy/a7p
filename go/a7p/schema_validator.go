package a7p

import (
	"bytes"
	"fmt"
	"sync"

	generated "github.com/o-murphy/a7p/go/a7p/generated"
	profedit "github.com/o-murphy/a7p/go/a7p/profedit"
	jsonschema "github.com/santhosh-tekuri/jsonschema/v6"
	protojson "google.golang.org/protobuf/encoding/protojson"
)

const schemaResourceURL = "a7p.schema.json"

var (
	schemaOnce     sync.Once
	compiledSchema *jsonschema.Schema
	schemaLoadErr  error
)

// compiledA7pSchema lazily compiles the embedded schema/a7p.schema.json
// (see generated.A7pSchemaJSON) into a reusable *jsonschema.Schema, once per
// process -- the same lazy-singleton shape as A7pValidator._schema in
// dart/lib/src/a7p_validator.dart, since building it is comparatively
// expensive and validate() may run many times per process.
func compiledA7pSchema() (*jsonschema.Schema, error) {
	schemaOnce.Do(func() {
		doc, err := jsonschema.UnmarshalJSON(bytes.NewReader(generated.A7pSchemaJSON))
		if err != nil {
			schemaLoadErr = fmt.Errorf("parse embedded schema: %w", err)
			return
		}

		compiler := jsonschema.NewCompiler()
		if err := compiler.AddResource(schemaResourceURL, doc); err != nil {
			schemaLoadErr = fmt.Errorf("add schema resource: %w", err)
			return
		}

		compiledSchema, schemaLoadErr = compiler.Compile(schemaResourceURL)
	})
	return compiledSchema, schemaLoadErr
}

// validateSchema validates payload against the shared schema/a7p.schema.json
// -- the same source of truth py/js/dart validate against (see
// docs/DESIGN-schema-unification.md). The proto's own field/enum names are
// already snake_case and match the schema's property names exactly, so
// protojson.MarshalOptions{UseProtoNames: true} needs no further remapping
// (unlike dart's manual camelCase->snake_case _payloadToJson).
func validateSchema(payload *profedit.Payload) error {
	schema, err := compiledA7pSchema()
	if err != nil {
		return err
	}

	// EmitDefaultValues: the schema's required/property checks need
	// zero-valued scalar fields (zero_x, twist_dir's default enum, etc.)
	// present in the JSON, not omitted the way protojson does by default.
	data, err := protojson.MarshalOptions{UseProtoNames: true, EmitDefaultValues: true}.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	instance, err := jsonschema.UnmarshalJSON(bytes.NewReader(data))
	if err != nil {
		return fmt.Errorf("unmarshal payload json: %w", err)
	}

	if err := schema.Validate(instance); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	return validateUniqueMv(payload.GetProfile().GetCoefRows())
}

// validateUniqueMv enforces that coef_rows[].mv values are unique except for
// mv == 0 -- not expressible in plain JSON Schema (see
// x-unique-except-zero in schema/a7p.schema.json), checked as a small manual
// step the same way py/js/dart do.
func validateUniqueMv(rows []*profedit.CoefRow) error {
	seen := make(map[int32]bool, len(rows))
	for _, r := range rows {
		mv := r.GetMv()
		if mv == 0 {
			continue
		}
		if seen[mv] {
			return fmt.Errorf("coef_rows: 'mv' values must be unique, except for mv == 0")
		}
		seen[mv] = true
	}
	return nil
}

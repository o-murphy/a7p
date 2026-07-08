package tests

import (
	"os"
	"path/filepath"
	"testing"

	a7p "github.com/o-murphy/a7p/go/a7p"
	profedit "github.com/o-murphy/a7p/go/a7p/profedit"
	protojson "google.golang.org/protobuf/encoding/protojson"
)

const fixturesDir = "../../schema/fixtures"

func fixturePaths(t *testing.T, dir string) []string {
	t.Helper()
	entries, err := os.ReadDir(dir)
	if err != nil {
		t.Fatalf("reading %s: %v", dir, err)
	}
	var paths []string
	for _, e := range entries {
		if !e.IsDir() && filepath.Ext(e.Name()) == ".json" {
			paths = append(paths, filepath.Join(dir, e.Name()))
		}
	}
	if len(paths) == 0 {
		t.Fatalf("no fixtures found in %s", dir)
	}
	return paths
}

// TestValidFixturesPass runs every file in schema/fixtures/valid/ -- the
// fixtures shared across py/js/dart/go (see
// docs/DESIGN-schema-unification.md) -- through the real decode path
// (protojson.Unmarshal, which accepts these snake_case field names directly
// since they're the proto's own names) and a7p.ValidateProto. Mirrors
// py/tests/test_validation.py's test_valid_fixtures_pass and
// dart/test/a7p_validator_test.dart.
func TestValidFixturesPass(t *testing.T) {
	for _, path := range fixturePaths(t, filepath.Join(fixturesDir, "valid")) {
		t.Run(filepath.Base(path), func(t *testing.T) {
			data, err := os.ReadFile(path)
			if err != nil {
				t.Fatal(err)
			}
			var payload profedit.Payload
			if err := protojson.Unmarshal(data, &payload); err != nil {
				t.Fatalf("unmarshal: %v", err)
			}
			if err := a7p.ValidateProto(&payload); err != nil {
				t.Errorf("expected valid, got: %v", err)
			}
		})
	}
}

// TestInvalidFixturesFail runs schema/fixtures/invalid/ and expects each to
// be rejected -- either at protojson.Unmarshal (e.g. bad_enum.json's unknown
// "SIDEWAYS" twist_dir, which isn't a valid enum value at all) or at
// a7p.ValidateProto (the rest: out-of-range values, a too-long string, too
// few switches, duplicate non-zero mv).
func TestInvalidFixturesFail(t *testing.T) {
	for _, path := range fixturePaths(t, filepath.Join(fixturesDir, "invalid")) {
		t.Run(filepath.Base(path), func(t *testing.T) {
			data, err := os.ReadFile(path)
			if err != nil {
				t.Fatal(err)
			}
			var payload profedit.Payload
			if err := protojson.Unmarshal(data, &payload); err != nil {
				return // rejected at parse time -- still a pass
			}
			if err := a7p.ValidateProto(&payload); err == nil {
				t.Errorf("expected %s to be rejected, but it validated cleanly", filepath.Base(path))
			}
		})
	}
}

// TestUniqueMvAllowsRepeatedZero mirrors dart's "mv == 0 may repeat across
// rows" -- the one rule schema/a7p.schema.json documents as not expressible
// in plain JSON Schema (x-unique-except-zero) and checked as a manual step
// in a7p.ValidateProto instead (see validateUniqueMv in schema_validator.go).
func TestUniqueMvAllowsRepeatedZero(t *testing.T) {
	data, err := os.ReadFile(filepath.Join(fixturesDir, "valid", "custom_profile.json"))
	if err != nil {
		t.Fatal(err)
	}
	var payload profedit.Payload
	if err := protojson.Unmarshal(data, &payload); err != nil {
		t.Fatal(err)
	}

	payload.Profile.CoefRows = []*profedit.CoefRow{
		{BcCd: 1000, Mv: 0},
		{BcCd: 1100, Mv: 0},
	}
	if err := a7p.ValidateProto(&payload); err != nil {
		t.Errorf("expected repeated mv == 0 to be allowed, got: %v", err)
	}

	payload.Profile.CoefRows = []*profedit.CoefRow{
		{BcCd: 1000, Mv: 8000},
		{BcCd: 1100, Mv: 8000},
	}
	if err := a7p.ValidateProto(&payload); err == nil {
		t.Error("expected duplicate non-zero mv to be rejected")
	}
}

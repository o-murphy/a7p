package tests

import (
	"bytes"
	"fmt"
	a7p "github.com/o-murphy/a7p/go/a7p"
	"slices"
	"strings"
	"testing"
)

func TestSlice(t *testing.T) {
	s := []int32{100, 200}
	i := slices.Index(s, 0)
	fmt.Println("I", i)
}

func TestA7p(t *testing.T) {
	payload, err := a7p.Loads(TestingData, true)
	if err != nil {
		t.Errorf("Error %s", err)
	}
	fmt.Println(payload)

	dump, err := a7p.Dumps(payload, true)

	if err != nil {
		t.Errorf("Error %s", err)
	}

	// Compare if the dumped data matches the original TestingData
	if !bytes.Equal(dump, TestingData) {
		// Compare if the dumped data matches the original TestingData
		// Truncate the output to show only the first few bytes for diff
		maxDiffBytes := 50
		if len(TestingData) < maxDiffBytes {
			maxDiffBytes = len(TestingData)
		}
		t.Errorf("Data mismatch: expected first %v bytes: %v, but got: %v", maxDiffBytes, TestingData[:maxDiffBytes], dump[:maxDiffBytes])
	}
}

// TestValidator documents a pre-existing data issue in ../assets/example.a7p
// (and dump.a7p/switches.a7p, which share the same distances table): its
// distances[0] is 0. The old protovalidate-go annotation on this field only
// checked repeated.min_items/max_items (array length), never each item's
// value -- so this was never actually caught before the migration to the
// shared schema/a7p.schema.json, which does enforce distances[i] >= 100 (see
// docs/DESIGN-schema-unification.md). This asserts the specific, now-correct
// rejection rather than silently requiring a clean validate() here.
func TestValidator(t *testing.T) {
	protoPayload, _ := a7p.Load("../assets/example.a7p", false)

	err := a7p.ValidateSpec(protoPayload)
	if err == nil {
		t.Fatal("expected validation error for known-bad distances[0] == 0 in example.a7p, got nil")
	}
	if !strings.Contains(err.Error(), "distances/0") {
		t.Errorf("expected error about distances/0, got: %s", err)
	}
}

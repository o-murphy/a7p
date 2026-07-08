package tests

import (
	a7p "a7p-go/a7p"
	"bytes"
	"fmt"
	"slices"
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

func TestValidator(t *testing.T) {
	protoPayload, _ := a7p.Load("../assets/example.a7p", true)

	if err := a7p.ValidateSpec(protoPayload); err != nil {
		t.Error(err)
	}
}

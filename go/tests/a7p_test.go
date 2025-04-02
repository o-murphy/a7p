package tests

import (
	a7p "a7p-go/a7p"
	"bytes"
	"fmt"
	"testing"
)

func TestA7p(t *testing.T) {
	payload, err := a7p.Loads(TestingData, true)
	if err != nil {
		t.Errorf("Error %s", err)
	}
	fmt.Println(payload)

	// payload.Profile.BDiameter = 308
	// fmt.Println("BDiameter", payload.Profile.BDiameter)

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

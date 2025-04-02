package a7p

import (
	profedit "a7p-go/a7p/profedit"
	"fmt"

	protovalidate "github.com/bufbuild/protovalidate-go"
)

const SwitchesMaxCount = 4

// Validate checks the content using protovalidate.
func ValidateProto(payload *profedit.Payload) error {
	validator, err := protovalidate.New()
	if err != nil {
		return fmt.Errorf("failed to create validator: %w", err)
	}

	if err := validator.Validate(payload); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}
	return nil
}

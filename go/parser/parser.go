package parser

import (
	"a7p/profedit"
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"io"
	"os"

	"github.com/bufbuild/protovalidate-go"
	"google.golang.org/protobuf/proto"
)

// OpenFile reads the content of a file and returns it as a byte slice.
func OpenFile(filename string) ([]byte, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

	data, err := io.ReadAll(file)
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %w", err)
	}

	return data, nil
}

// CheckMD5Sum extracts the first 32 characters as the MD5 checksum
// and validates it against the remaining content.
func CheckMD5Sum(data []byte) ([]byte, error) {
	if len(data) < 32 {
		return nil, fmt.Errorf("invalid file format: insufficient data")
	}

	expectedMD5 := string(data[:32]) // First 32 characters contain the MD5 hash
	content := data[32:]             // Rest is the actual data

	// Compute MD5 hash of the content
	hash := md5.Sum(content)
	calculatedMD5 := hex.EncodeToString(hash[:])

	if expectedMD5 != calculatedMD5 {
		return nil, fmt.Errorf("MD5 checksum mismatch: expected %s, got %s", expectedMD5, calculatedMD5)
	}

	return content, nil
}

// Unmarshal decodes a protobuf message from content.
func Unmarshal(content []byte) (*profedit.Payload, error) {
	payload := &profedit.Payload{}
	if err := proto.Unmarshal(content, payload); err != nil {
		return nil, fmt.Errorf("failed to unmarshal protobuf: %w", err)
	}
	return payload, nil
}

// Validate checks the content using protovalidate.
func Validate(payload *profedit.Payload) error {
	validator, err := protovalidate.New()
	if err != nil {
		return fmt.Errorf("failed to create validator: %w", err)
	}

	if err := validator.Validate(payload); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}
	return nil
}

func Loads(data []byte, validate bool) (*profedit.Payload, error) {
	// Validate MD5 checksum and get content
	content, err := CheckMD5Sum(data)
	if err != nil {
		return nil, err
	}

	// Unmarshal content into protobuf struct
	payload, err := Unmarshal(content)
	if err != nil {
		return nil, err
	}

	// Validate the payload if requested
	if validate {
		if err := Validate(payload); err != nil {
			return nil, err
		}
	}

	return payload, nil
}

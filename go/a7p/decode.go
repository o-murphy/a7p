package a7p

import (
	"a7p/profedit"
	"crypto/md5"
	"encoding/hex"
	"fmt"

	"google.golang.org/protobuf/proto"
)

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

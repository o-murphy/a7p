package a7p

import (
	"a7p/profedit"
	"crypto/md5"
	"encoding/hex"
	"fmt"

	"google.golang.org/protobuf/proto"
)

// AddMD5Sum computes the MD5 checksum of the given content and
// prepends it to the content as a 32-character hex string.
func AddMD5Sum(content []byte) []byte {
	// Compute MD5 hash of the content
	hash := md5.Sum(content)
	md5Hex := hex.EncodeToString(hash[:])

	// Prepend the MD5 checksum to the content
	return append([]byte(md5Hex), content...)
}

// Marshal encodes a protobuf message into a byte slice.
func Marshal(payload *profedit.Payload) ([]byte, error) {
	data, err := proto.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal protobuf: %w", err)
	}
	return data, nil
}

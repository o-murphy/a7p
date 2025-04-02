package a7p

import (
	"a7p/profedit"
	"fmt"
	"io"
	"os"
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

func SaveFile(filename string, data []byte) error {
	// Open the file for writing, create it if it doesn't exist, and truncate it if it does
	file, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

	// Write the data to the file
	_, err = file.Write(data)
	if err != nil {
		return fmt.Errorf("failed to write to file: %w", err)
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
		return payload, err
	}

	// Validate the payload if requested
	if validate {
		err = ValidateProto(payload)
	}

	return payload, err

}

func Load(filename string, validate bool) (*profedit.Payload, error) {
	data, err := OpenFile(filename)
	if err != nil {
		fmt.Println("Error:", err)
		return nil, err
	}
	return Loads(data, validate)
}

func Dumps(payload *profedit.Payload, validate bool) ([]byte, error) {

	// Validate the payload if requested
	if validate {
		if err := ValidateProto(payload); err != nil {
			return nil, err
		}
	}

	content, err := Marshal(payload)
	if err != nil {
		return nil, err
	}

	return AddMD5Sum(content), nil
}

func Dump(filename string, payload *profedit.Payload, validate bool) error {
	data, err := Dumps(payload, validate)
	if err != nil {
		return err
	}
	if err = SaveFile(filename, data); err != nil {
		return err
	}
	return nil
}

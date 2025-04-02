PACKAGE_DIR=a7p
PROTO_DIR=profedit
PROTO_FILE=$(PACKAGE_DIR)/$(PROTO_DIR)/profedit_validate.proto

# Detect OS and set the binary name accordingly
ifeq ($(OS),Windows_NT)
    BINARY=dist/a7p.exe
else
    BINARY=dist/a7p
endif

.PHONY: all build generate install-tools clean test

all: build

# Build both protobuf files and the Go project
build: generate
	@echo "Building Go project..."
	@mkdir -p dist  # Ensure the dist directory exists
	@GOFLAGS="-mod=readonly" go build -o $(BINARY) -ldflags "-X main.Version=0.0.0" .
	@echo "Build successful. Binary placed at: $(BINARY)"

# Generate protobuf Go code
generate: install-tools
	@echo "Generating Protobuf files..."
	@protoc --go_out=. --go_opt=paths=source_relative \
	        --go-grpc_out=. --go-grpc_opt=paths=source_relative \
	        -I. -Ibuf $(PROTO_FILE)

# Install necessary protobuf tools
install-tools:
	@echo "Installing required tools..."
	@GOBIN=$$(go env GOPATH)/bin go install \
		google.golang.org/protobuf/cmd/protoc-gen-go@latest
	@GOBIN=$$(go env GOPATH)/bin go install \
		google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Test
test: install-tools generate
	@echo "Running tests..."
	go test ./tests
	@echo "Tests complete"

# Remove generated files and binaries
clean:
	@echo "Cleaning up..."
	@rm -rf $(PROTO_DIR)/*.pb.go dist/

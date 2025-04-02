# OS and Architecture lists based on the OS
ifeq ($(OS),Windows_NT)
    GOOS = windows
    GOARCH_LIST = 386 amd64 arm arm64
else ifeq ($(shell uname), Darwin)
    GOOS = darwin
    GOARCH_LIST = 386 amd64 arm arm64
else
    GOOS = linux
    GOARCH_LIST = 386 amd64 arm arm64 mips mips64 mipsle  # Add mipsle for linux
endif

# Add support for wasm/js architecture
GOOS_WASM = js
GOARCH_WASM_LIST = wasm

PACKAGE_DIR=a7p
PROTO_DIR=profedit
PROTO_FILE=$(PACKAGE_DIR)/$(PROTO_DIR)/profedit_validate.proto
DIST_DIR = dist
BINARY = a7p

.PHONY: all build generate install-tools clean test

all: build

# Build both protobuf files and the Go project
build: generate
	@mkdir -p $(DIST_DIR)  # Ensure the dist directory exists
	@echo "Building for OS: $(GOOS)"
	@for arch in $(GOARCH_LIST); do \
		GOOS=$(GOOS) GOARCH=$$arch go build -o $(DIST_DIR)/$(BINARY)-$(GOOS)-$$arch; \
		if [ "$(GOOS)" = "windows" ]; then \
			mv $(DIST_DIR)/$(BINARY)-$(GOOS)-$$arch $(DIST_DIR)/$(BINARY)-$(GOOS)-$$arch.exe; \
		fi; \
	done

	# Now build for WASM
	@echo "Building for WASM"
	@for arch in $(GOARCH_WASM_LIST); do \
		GOOS=$(GOOS_WASM) GOARCH=$$arch go build -o $(DIST_DIR)/$(BINARY)-$(GOOS_WASM)-$$arch.wasm; \
	done

	@echo "Build successful. Binaries placed at: $(DIST_DIR)"
	@ls -la $(DIST_DIR)

# Generate protobuf Go code
generate: install-tools
	@echo "Generating Protobuf files..."
	@protoc --go_out=. --go_opt=paths=source_relative \
	        --go-grpc_out=. --go-grpc_opt=paths=source_relative \
	        -I. -Ibuf $(PROTO_FILE)

# Install protoc tool depending on the OS
install-protoc:
	@echo "Installing protoc..."
ifeq ($(GOOS), windows)
	@echo "Installing protoc for Windows using Chocolatey..."
	@choco install protoc --confirm -y --accept-license # --confirm to suppress prompts, -y for automatic confirmation
else ifeq ($(GOOS), darwin)
	@echo "Installing protoc for macOS using Homebrew..."
	@brew install protobuf --quiet # --quiet to suppress prompts
else ifeq ($(GOOS), linux)
	@echo "Installing protoc for Linux using apt-get..."
	@sudo apt-get install -y protobuf-compiler # -y for automatic confirmation
endif

# Install necessary protobuf tools
install-tools: install-protoc
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

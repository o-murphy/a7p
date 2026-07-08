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

DIST_DIR = dist
BINARY = a7p

.PHONY: all build clean test

all: build

# protobuf bindings (a7p/profedit/profedit.pb.go) and the embedded JSON
# schema (a7p/generated/a7p_schema.g.json) are generated from the repo
# root's canonical proto/profedit.proto and schema/a7p.schema.json --
# `../scripts/generate_proto.sh --go` / `../scripts/compile.py --go` --
# and checked in, not regenerated as part of the build (see
# docs/DESIGN-schema-unification.md).
build:
	@mkdir -p $(DIST_DIR)  # Ensure the dist directory exists
	@echo "Building for OS: $(GOOS)"
	@for arch in $(GOARCH_LIST); do \
		GOOS=$(GOOS) GOARCH=$$arch go build -o $(DIST_DIR)/$(BINARY)-$(GOOS)-$$arch -ldflags="-s -w" .; \
		if [ "$(GOOS)" = "windows" ]; then \
			mv $(DIST_DIR)/$(BINARY)-$(GOOS)-$$arch $(DIST_DIR)/$(BINARY)-$(GOOS)-$$arch.exe; \
		fi; \
	done

	# Now build for WASM
	@echo "Building for WASM"
	@for arch in $(GOARCH_WASM_LIST); do \
		GOOS=$(GOOS_WASM) GOARCH=$$arch go build -o $(DIST_DIR)/$(BINARY)-$(GOOS_WASM)-$$arch.wasm .; \
	done

	@echo "Build successful. Binaries placed at: $(DIST_DIR)"

test:
	@echo "Running tests..."
	go test ./tests/...
	@echo "Tests complete"

# Remove binaries
clean:
	@echo "Cleaning up..."
	@rm -rf dist/

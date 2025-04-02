# gen proto

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest 
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
# buf dep update
# $env:PATH += ";" + (go env GOPATH) + "\bin"
# buf export buf.build/bufbuild/protovalidate --output=buf
# go get buf.build/gen/go/bufbuild/protovalidate/protocolbuffers/go@latest
# go get -u buf.build/gen/go/bufbuild/protovalidate/protocolbuffers/go/buf/validate
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative -I. -Ibuf .\profedit\profedit_validate.proto
go mod tidy
go get github.com/bufbuild/protovalidate-go
```
package main

import (
	a7p "a7p-go/a7p"
	profedit "a7p-go/a7p/profedit"
	log "a7p-go/log"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	arg "github.com/alexflint/go-arg"
)

const Version = "0.0.0"

var argParser *arg.Parser

// Define a struct to hold the command-line arguments
// Arguments struct with fields for path and version flag
type arguments struct {
	Path      string `arg:"positional,required" help:"Path to the directory or a .a7p file to process"`
	Version   bool   `arg:"-V, --version" help:"Display the current version of the tool"`
	Recursive bool   `arg:"-r, --recursive" help:"Recursively process files in the specified directory"`
	Force     bool   `arg:"-F, --force" help:"Force saving changes without confirmation"`
	Unsafe    bool   `arg:"--unsafe" help:"Skip data validation (use with caution)\n\nSingle-file-only:"`

	// Single file specific options
	Verbose bool `arg:"--verbose" help:"Enable verbose output for detailed logs. This option is only allowed for a single file."`
	Recover bool `arg:"--recover" help:"Attempt to recover from errors found in a file. This option is only allowed for a single file.\n\nDistances:"`

	// Distances group options
	ZeroDistance int    `arg:"--zero-distance" help:"Set the zero distance in meters."`
	DistanceType string `arg:"--distances" choices:"subsonic,low,medium,long,ultra" help:"Specify the distance range: 'subsonic', 'low', 'medium', 'long', or 'ultra'.\n\nZeroing:"`

	// Zeroing group options
	ZeroSync   string    `arg:"--zero-sync" help:"Synchronize zero using a specified configuration file."`
	ZeroOffset []float64 `arg:"--zero-offset" help:"Set the offset for zeroing in clicks (X_OFFSET and Y_OFFSET).\n\nARCHER-device-specific:"`

	// Switches group options (Archer devices specific)
	CopySwitchesFrom string `arg:"--copy-switches-from" help:"Copy switches from another a7p file."`
}

type zeros struct {
	x int32
	y int32
}

type result struct {
	Path            string
	Error           any
	ValidationError any
	Zero            zeros
	NewZero         zeros
	ZeroUpdate      bool
	Distances       string
	ZeroDistance    string
	Recover         string
	Payload         profedit.Payload
	Switches        bool
}

func (r *result) resetErrors() {
	r.Error = nil
	r.ValidationError = nil
}

func (r *result) print() {
	// ...
}

func (r *result) saveChanges() {

}

func getFilesWithExtension(dir string, ext string) []string {
	var files []string

	// Read the directory contents
	dirContents, err := os.ReadDir(dir)
	if err != nil {
		argParser.Fail(err.Error())
	}

	// Loop through the directory contents and filter files with the specified extension
	for _, entry := range dirContents {
		// Check if it's a file and has the specified extension
		if !entry.IsDir() && strings.HasSuffix(entry.Name(), ext) {
			// Get the full path to the file
			fullPath := filepath.Join(dir, entry.Name())
			files = append(files, fullPath)
		}
	}

	return files
}

func getFilesWithExtensionRecursive(dir string, ext string) []string {
	var files []string

	// Walk through the directory recursively
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		// Skip errors (like permission issues)
		if err != nil {
			return nil
		}

		// Only consider files with the specified extension
		if !info.IsDir() && strings.HasSuffix(info.Name(), ext) {
			files = append(files, path)
		}
		return nil
	})

	if err != nil {
		argParser.Fail(err.Error())
	}

	return files
}

func getZeroToSync(path string, validate bool) *zeros {
	if path == "" {
		return nil
	}
	payload, err := a7p.Load(path, validate)
	if err != nil {
		argParser.Fail(err.Error())
	}
	return &zeros{
		x: payload.Profile.ZeroX,
		y: payload.Profile.ZeroY,
	}
}

func getSwitchesToCopy(path string, validate bool) []*profedit.SwPos {
	if path == "" {
		return nil
	}
	payload, err := a7p.Load(path, validate)
	if err != nil {
		argParser.Fail(err.Error())
	}
	return payload.Profile.Switches
}

func updateDistances(payload *profedit.Payload, distances string, zero_distance int32) {
	// ...
}

func updateZeroing(payload *profedit.Payload, zeroOffset []int32, zeroSync zeros) {
	// ...
}

func updateSwitches(payload *profedit.Payload, switches []*profedit.SwPos) {
	// ...
}

func updateData(payload *profedit.Payload) {
	// ...
}

func printResultAndSave(results []result, verbose, force bool) {

}

// pathStatus returns the status of the path: directory, file, or nonexistent.
// It also handles errors gracefully and provides meaningful messages.
func pathStatus(path string) string {
	info, err := os.Stat(path)

	if err != nil {
		if os.IsNotExist(err) {
			// Path doesn't exist
			err = fmt.Errorf("the path '%s' does not exist", path)
		} else if os.IsPermission(err) {
			// Permission error
			err = fmt.Errorf("permission error when accessing '%s'", path)
		} else {
			// Other errors (such as incorrect function on Windows)
			err = fmt.Errorf("error accessing '%s': %s", path, err)
		}
		argParser.Fail(err.Error())
	}

	// Check if it's a directory
	if info.IsDir() {
		return "dir"
	}

	// Otherwise, it's a regular file
	return "file"
}

func processFile(path string, args arguments) result {
	if args.Recover {
		args.Verbose = true
		argParser.Fail("Not implemented yet [--recover]") // FIXME
	}
	return result{Path: path}
}

func processFiles(args arguments) {
	validate := !args.Unsafe

	var files []string
	var results []result

	// Check if the path is a directory
	pStatus := pathStatus(args.Path)

	zeroSync := getZeroToSync(args.ZeroSync, validate)
	// copySwitches := getSwitchesToCopy(args.CopySwitchesFrom, validate)[:SwitchesMaxCount]
	copySwitches := getSwitchesToCopy(args.CopySwitchesFrom, validate)

	switch pStatus {
	case "file":
		files = []string{args.Path}

	case "dir":
		if args.Recover {
			log.Warn("The '--recover' option is supported only when processing a single file.")
			args.Recover = false
		}
		if args.Verbose {
			log.Warn("The '--verbose' option is supported only when processing a single file.")
			args.Verbose = false
		}

		if args.Recursive {
			files = getFilesWithExtensionRecursive(args.Path, a7p.FileExtension)
		} else {
			files = getFilesWithExtension(args.Path, a7p.FileExtension)
		}

	}
	for _, file := range files {
		results = append(results, processFile(file, args))
	}

	fmt.Println(files, zeroSync, copySwitches)
	fmt.Println(results)
}

func main() {

	// Initialize the argument parser
	var args arguments

	arg.Parse(&args)

	// Check if the version flag is set
	if args.Version {
		// Print the version and exit
		fmt.Println("Current version:", Version)
		os.Exit(0)
	}

	argParser = arg.MustParse(&args)

	fmt.Println(args)
	processFiles(args)
}

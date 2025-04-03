package main

import (
	a7p "a7p-go/a7p"
	profedit "a7p-go/a7p/profedit"
	log "a7p-go/log"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"

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
	ZeroDistance int32  `arg:"--zero-distance" help:"Set the zero distance in meters."`
	Distances    string `arg:"--distances" choices:"subsonic,low,medium,long,ultra" help:"Specify the distance range: 'subsonic', 'low', 'medium', 'long', or 'ultra'.\n\nZeroing:"`

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

type resultT struct {
	Path            string
	Error           error
	ValidationError any
	Zero            zeros
	NewZero         zeros
	ZeroUpdate      bool
	Distances       string
	ZeroDistance    string
	Recover         string
	Payload         *profedit.Payload
	Switches        bool
}

func (r *resultT) resetErrors() {
	r.Error = nil
	r.ValidationError = nil
}

func (r *resultT) print() {
	fmt.Println("Path:", r.Path)
	fmt.Println("Err:", r.Error)
	fmt.Println()
}

func (r *resultT) saveChanges() {

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

func updateDistances(payload *profedit.Payload, args arguments) {
	// ...
}

func updateZeroing(payload *profedit.Payload, args arguments, validate bool) {
	// zeroSyncData := getZeroToSync(args.ZeroSync, validate)
}

func updateSwitches(payload *profedit.Payload, args arguments, validate bool) {
	// copySwitches := getSwitchesToCopy(args.CopySwitchesFrom, validate)
}

func printResultAndSave(results []resultT, verbose, force bool) {
	for _, r := range results {
		r.print()
	}
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

func processFile(path string, args arguments, validate bool) resultT {
	payload, err := a7p.Load(path, validate)
	result := resultT{
		Path:       path,
		Error:      err,
		Payload:    payload,
		Zero:       zeros{payload.Profile.ZeroX, payload.Profile.ZeroY},
		Distances:  args.Distances,
		ZeroUpdate: len(args.ZeroOffset) == 2 || args.ZeroSync != "",
		// NewZero: ,  // FIXME
		Switches: args.CopySwitchesFrom != "",
	}
	if result.Error != nil {
		return result
	}

	if result.Distances != "" {
		updateDistances(result.Payload, args)
	}
	if result.ZeroUpdate {
		updateZeroing(result.Payload, args, validate)
	}
	if result.Switches {
		updateSwitches(result.Payload, args, validate)
	}

	return result
}

func processFiles(args arguments) {
	validate := !args.Unsafe

	var files []string

	// Check if the path is a directory
	pStatus := pathStatus(args.Path)

	if args.ZeroSync != "" {
		if len(args.ZeroOffset) == 2 {
			argParser.Fail("--zero-offset and --zero-sync should be used mutually exclusive")
		}
	} else if len(args.ZeroOffset) > 0 && len(args.ZeroOffset) != 2 {
		argParser.Fail("--zero-offset require a pair of floats")
	}

	switch pStatus {
	case "file":
		if args.Recover {
			args.Verbose = true
			argParser.Fail("Not implemented yet [--recover]") // FIXME
		}
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

	var wg sync.WaitGroup
	resultsChan := make(chan resultT, len(files)) // Channel to collect results

	for _, file := range files {
		wg.Add(1)
		go func(file string) {
			defer wg.Done()
			// Process the file and send the result to the channel
			result := processFile(file, args, validate)
			resultsChan <- result
		}(file)
	}

	// Wait for all goroutines to finish
	wg.Wait()
	close(resultsChan)

	var results []resultT
	for result := range resultsChan {
		results = append(results, result)
	}

	printResultAndSave(results, args.Verbose, args.Force)
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

	processFiles(args)
}

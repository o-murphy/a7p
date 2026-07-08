package main

import (
	a7p "a7p-go/a7p"
	profedit "a7p-go/a7p/profedit"
	log "a7p-go/log"
	"fmt"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"sync"

	"github.com/akamensky/argparse"
)

const Version = "0.0.0"

var argParser = argparse.NewParser("a7p", Version)
var args arguments

type zeros struct {
	x int32
	y int32
}

func (z *zeros) String() string {
	return fmt.Sprintf("X: %.2f,\tY: %.2f", float64(-z.x)/1000, float64(z.y)/1000)
}

type resultT struct {
	path            string
	err             error
	validationError any
	zero            *zeros
	newZero         *zeros
	distances       *string
	zeroDistance    *int
	// recover         bool
	payload  *profedit.Payload
	switches []*profedit.SwPos
}

func (r *resultT) resetErrors() {
	r.err = nil
	r.validationError = nil
}

func (r *resultT) print() {

	if r.err != nil {
		msg := log.FmtRed(fmt.Sprintf("Invalid (%s):", r.err))
		fmt.Printf("%s File: %s\n", msg, r.path)
	} else {
		msg := log.FmtGreen("Valid:")
		fmt.Printf("%s File: %s\n", msg, r.path)
	}

	if r.zero != nil {
		fmt.Printf("\tZero:\t%s\n", r.zero)
	}

	var updates []string

	if r.newZero != nil {
		updates = append(updates, fmt.Sprintf("\tNew zero:\t%s", r.newZero))
	}
	if *r.distances != "" {
		updates = append(updates, fmt.Sprintf("\tNew range:\t%s", r.distances))
	}
	if *r.zeroDistance > -1 {
		updates = append(updates, fmt.Sprintf("\tNew zero distance:\t%d", *r.zeroDistance))
	}
	if r.switches != nil {
		updates = append(updates, "\tSwitches copied")
	}

	fmt.Println(log.FmtBlue(strings.Join(updates, "\n")))

	if r.validationError != nil && *args.Verbose {
		log.Err("Not implemented")
	}
}

func (r *resultT) saveChanges(validate bool) {
	hasChanges := *r.zeroDistance > 0 || *r.distances != "" || r.newZero != nil || r.switches != nil

	if hasChanges {
		if !*args.Force {
			var yesNo string
			fmt.Println(log.FmtYellow("Do you want to save changes? (Y/N): "))
			fmt.Scanln(&yesNo)
			yesNo = strings.TrimSpace(strings.ToUpper(yesNo))
			if yesNo != "Y" {
				log.Info("No changes have been saved.")
				return
			}
		}

		// if r.recover {
		// 	ext := filepath.Ext(r.path)
		// 	base := strings.TrimSuffix(r.path, ext)
		// 	r.path = base + "_recovered" + ext
		// }

		if _, err := a7p.Dumps(r.payload, validate); err != nil {
			log.Warn("The data is invalid. Changes have not been saved.")
			return
		}
		if err := a7p.Dump(r.path, r.payload, validate); err != nil {
			log.Warn(fmt.Sprintf("An error occurred while saving: %s", err.Error()))
			return
		}
		log.Info(fmt.Sprintf("Changes have been saved successfully to %s.", r.path))
		fmt.Println(r.newZero)
		fmt.Println(r.payload.Profile.ZeroX, r.payload.Profile.ZeroY)
	}
}

func getFilesWithExtension(dir string, ext string) []string {
	var files []string

	// Read the directory contents
	dirContents, err := os.ReadDir(dir)
	if err != nil {
		Fail(err.Error())
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
		Fail(err.Error())
	}

	return files
}

func getZeroToSync(path string, validate bool) *zeros {
	if path == "" {
		return nil
	}
	payload, err := a7p.Load(path, validate)
	if err != nil {
		Fail(err.Error())
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
		Fail(err.Error())
	}
	return payload.Profile.Switches
}

func updateDistances(result *resultT) {
	var curZeroDistance int32

	if *result.zeroDistance < 0 {
		curZeroDistance = result.payload.Profile.Distances[result.payload.Profile.CZeroDistanceIdx]
	} else {
		curZeroDistance = int32(*result.zeroDistance) * 100
	}

	dType := a7p.DistanceType(*result.distances)
	switch dType {
	case a7p.SubsonicRange, a7p.LowRange, a7p.MediumRange, a7p.LongRange, a7p.UltraRange:
		result.payload.Profile.Distances = a7p.Distances[dType]
	}

	if slices.Index(result.payload.Profile.Distances, curZeroDistance) < 0 {
		result.payload.Profile.Distances = append(result.payload.Profile.Distances, curZeroDistance)
	}
	slices.Sort(result.payload.Profile.Distances)
	result.payload.Profile.CZeroDistanceIdx = int32(slices.Index(result.payload.Profile.Distances, curZeroDistance))
}

func updateZeroing(result *resultT, validate bool) {

	if *args.ZeroSync != "" {
		result.newZero = getZeroToSync(*args.ZeroSync, validate)
	} else if len(*args.ZeroOffset) == 2 {
		result.newZero = &zeros{
			x: result.zero.x + int32((*args.ZeroOffset)[0]*-1000),
			y: result.zero.y + int32((*args.ZeroOffset)[1]*1000),
		}
	}

	if result.newZero != nil {
		result.payload.Profile.ZeroX = result.newZero.x
		result.payload.Profile.ZeroY = result.newZero.y
	}
}

func updateSwitches(result *resultT) {
	if result.switches != nil {
		result.payload.Profile.Switches = result.switches
	}
}

func printResultAndSave(results []*resultT, validate bool) {

	countErrors := 0

	for _, result := range results {
		if result != nil {
			result.print()
			fmt.Println()
			result.saveChanges(validate)

			if result.err != nil {
				countErrors++
			}
		}
	}

	outStrings := []string{
		fmt.Sprintf("Files checked: %d", len(results)),
		log.FmtGreen(fmt.Sprintf("Ok: %d", len(results)-countErrors)),
		log.FmtRed(fmt.Sprintf("Failed: %d", countErrors)),
	}
	fmt.Println(strings.Join(outStrings, ", "))

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
		Fail(err.Error())
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
	result := &resultT{
		path:         path,
		err:          err,
		payload:      payload,
		zero:         &zeros{payload.Profile.ZeroX, payload.Profile.ZeroY},
		distances:    args.Distances,
		zeroDistance: args.ZeroDistance,
		switches:     getSwitchesToCopy(*args.CopySwitchesFrom, validate),
	}
	if result.err != nil {
		return *result
	}

	updateDistances(result)
	updateZeroing(result, validate)
	updateSwitches(result)

	return *result
}

func processFiles() {
	validate := !*args.Unsafe

	var files []string

	// Check if the path is a directory
	pStatus := pathStatus(*args.Path)

	if *args.ZeroSync != "" {
		if len(*args.ZeroOffset) == 2 {
			Fail("--zero-offset and --zero-sync should be used mutually exclusive")
		}
	} else if len(*args.ZeroOffset) > 0 && len(*args.ZeroOffset) != 2 {
		Fail("--zero-offset require a pair of floats")
	}

	switch a7p.DistanceType(*args.Distances) {
	case a7p.SubsonicRange, a7p.LowRange, a7p.MediumRange, a7p.LongRange, a7p.UltraRange, "":

	default:
		Fail("Invalid --distances")
	}

	switch pStatus {
	case "file":
		// if *args.Recover {
		// 	*args.Verbose = true
		// 	Fail("Not implemented yet [--recover]") // FIXME
		// }
		files = []string{*args.Path}

	case "dir":
		// if *args.Recover {
		// 	log.Warn("The '--recover' option is supported only when processing a single file.")
		// 	*args.Recover = false
		// }
		if *args.Verbose {
			log.Warn("The '--verbose' option is supported only when processing a single file.")
			*args.Verbose = false
		}

		if *args.Recursive {
			files = getFilesWithExtensionRecursive(*args.Path, a7p.FileExtension)
		} else {
			files = getFilesWithExtension(*args.Path, a7p.FileExtension)
		}

	}

	// async file processing
	var wg sync.WaitGroup
	resultsChan := make(chan *resultT, len(files)) // Channel to collect results

	for _, file := range files {
		wg.Add(1)
		go func(file string) {
			defer wg.Done()
			// Process the file and send the result to the channel
			result := processFile(file, args, validate)
			resultsChan <- &result
		}(file)
	}

	// Wait for all goroutines to finish
	wg.Wait()
	close(resultsChan)

	var results []*resultT
	for result := range resultsChan {
		if result != nil {
			results = append(results, result)
		}
	}

	printResultAndSave(results, validate)
}

// Define a struct to hold the command-line arguments
// Arguments struct with fields for path and version flag
type arguments struct {
	Path      *string
	Version   *bool
	Recursive *bool
	Force     *bool
	Unsafe    *bool

	// Single file specific options
	Verbose *bool
	// Recover *bool

	// Distances group options
	ZeroDistance *int
	Distances    *string

	// Zeroing group options
	ZeroSync   *string
	ZeroOffset *[]float64

	// Switches group options (Archer devices specific)
	CopySwitchesFrom *string
}

func Fail(msg string) {
	log.Err(msg)
	os.Exit(1)
}

func main() {

	args.Path = argParser.StringPositional(&argparse.Options{Required: true, Help: "Path to the directory or a .a7p file to process"})
	args.Version = argParser.Flag("V", "version", &argparse.Options{Help: "Display the current version of the tool"})
	args.Recursive = argParser.Flag("r", "recursive", &argparse.Options{Help: "Recursively process files in the specified directory"})
	args.Force = argParser.Flag("F", "force", &argparse.Options{Help: "Force saving changes without confirmation"})
	args.Unsafe = argParser.Flag("", "unsafe", &argparse.Options{Help: "Skip data validation (use with caution)\n\nSingle-file-only:"})

	args.Verbose = argParser.Flag("", "verbose", &argparse.Options{Help: "Enable verbose output for detailed logs. This option is only allowed for a single file."})
	// args.Recover = argParser.Flag("", "recover", &argparse.Options{Help: "Attempt to recover from errors found in a file. This option is only allowed for a single file.\n\nDistances:"})

	args.ZeroDistance = argParser.Int("", "zero-distance", &argparse.Options{Help: "Set the zero distance in meters."})
	args.Distances = argParser.Selector("", "distances", []string{"subsonic", "low", "medium", "long", "ultra"}, &argparse.Options{Help: "Specify the distance range: 'subsonic', 'low', 'medium', 'long', or 'ultra'.\n\nZeroing:"})

	args.ZeroSync = argParser.String("", "zero-sync", &argparse.Options{Help: "Synchronize zero using a specified configuration file."})
	args.ZeroOffset = argParser.FloatList("", "zero-offset", &argparse.Options{Help: "Set the offset for zeroing in clicks (X_OFFSET and Y_OFFSET).\n\nARCHER-device-specific:"})

	args.CopySwitchesFrom = argParser.String("", "copy-switches-from", &argparse.Options{Help: "Copy switches from another a7p file."})

	err := argParser.Parse(os.Args)
	if err != nil {
		// In case of error print error and print usage
		// This can also be done by passing -h or --help flags
		fmt.Print(argParser.Usage(err))
		os.Exit(1)
	}

	if *args.Version {
		// Print the version and exit
		fmt.Println("Current version:", Version)
		os.Exit(0)
	}
	processFiles()
}

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

	arg "github.com/alexflint/go-arg"
)

const Version = "0.0.0"

var argParser *arg.Parser
var args arguments

var distances = make(map[distanceType][]int32)

// Initialize the map inside init()
func init() {
	distances[subsonicRange] = []int32{25, 50, 75, 100, 110, 120, 130, 140, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220,
		225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300, 305, 310, 315, 320, 325, 330,
		335, 340, 345, 350, 355, 360, 365, 370, 375, 380, 385, 390, 395, 400}
	distances[lowRange] = []int32{100, 150, 200, 225, 250, 275, 300, 320, 340, 360, 380, 400, 410, 420, 430, 440,
		450, 460, 470, 480, 490, 500, 505, 510, 515, 520, 525, 530, 535, 540, 545, 550,
		555, 560, 565, 570, 575, 580, 585, 590, 595, 600, 605, 610, 615, 620, 625, 630,
		635, 640, 645, 650, 655, 660, 665, 670, 675, 680, 685, 690, 695, 700}
	distances[mediumRange] = []int32{100, 200, 250, 300, 325, 350, 375, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600, 610, 620, 630, 640,
		650, 660, 670, 680, 690, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800, 805, 810, 815, 820, 825, 830,
		835, 840, 845, 850, 855, 860, 865, 870, 875, 880, 885, 890, 895, 900, 905, 910, 915, 920, 925, 930, 935, 940,
		945, 950, 955, 960, 965, 970, 975, 980, 985, 990, 995, 1000}
	distances[longRange] = []int32{100, 200, 250, 300, 350, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600, 610, 620, 630, 640, 650, 660,
		670, 680, 690, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800, 810, 820, 830, 840, 850, 860, 870, 880,
		890, 900, 910, 920, 930, 940, 950, 960, 970, 980, 990, 1000, 1005, 1010, 1015, 1020, 1025, 1030, 1035, 1040,
		1045, 1050, 1055, 1060, 1065, 1070, 1075, 1080, 1085, 1090, 1095, 1100, 1105, 1110, 1115, 1120, 1125, 1130,
		1135, 1140, 1145, 1150, 1155, 1160, 1165, 1170, 1175, 1180, 1185, 1190, 1195, 1200, 1205, 1210, 1215, 1220,
		1225, 1230, 1235, 1240, 1245, 1250, 1255, 1260, 1265, 1270, 1275, 1280, 1285, 1290, 1295, 1300, 1305, 1310,
		1315, 1320, 1325, 1330, 1335, 1340, 1345, 1350, 1355, 1360, 1365, 1370, 1375, 1380, 1385, 1390, 1395, 1400,
		1405, 1410, 1415, 1420, 1425, 1430, 1435, 1440, 1445, 1450, 1455, 1460, 1465, 1470, 1475, 1480, 1485, 1490,
		1495, 1500, 1505, 1510, 1515, 1520, 1525, 1530, 1535, 1540, 1545, 1550, 1555, 1560, 1565, 1570, 1575, 1580,
		1585, 1590, 1595, 1600, 1605, 1610, 1615, 1620, 1625, 1630, 1635, 1640, 1645, 1650, 1655, 1660, 1665, 1670,
		1675, 1680, 1685, 1690, 1695, 1700}
	distances[ultraRange] = []int32{100, 200, 250, 300, 350, 400, 450, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700, 720, 740, 760, 780,
		800, 820, 840, 860, 880, 900, 920, 940, 960, 980, 1000, 1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090,
		1100, 1110, 1120, 1130, 1140, 1150, 1160, 1170, 1180, 1190, 1200, 1210, 1220, 1230, 1240, 1250, 1260, 1270,
		1280, 1290, 1300, 1310, 1320, 1330, 1340, 1350, 1360, 1370, 1380, 1390, 1400, 1410, 1420, 1430, 1440, 1450,
		1460, 1470, 1480, 1490, 1500, 1505, 1510, 1515, 1520, 1525, 1530, 1535, 1540, 1545, 1550, 1555, 1560, 1565,
		1570, 1575, 1580, 1585, 1590, 1595, 1600, 1605, 1610, 1615, 1620, 1625, 1630, 1635, 1640, 1645, 1650, 1655,
		1660, 1665, 1670, 1675, 1680, 1685, 1690, 1695, 1700, 1705, 1710, 1715, 1720, 1725, 1730, 1735, 1740, 1745,
		1750, 1755, 1760, 1765, 1770, 1775, 1780, 1785, 1790, 1795, 1800, 1805, 1810, 1815, 1820, 1825, 1830, 1835,
		1840, 1845, 1850, 1855, 1860, 1865, 1870, 1875, 1880, 1885, 1890, 1895, 1900, 1905, 1910, 1915, 1920, 1925,
		1930, 1935, 1940, 1945, 1950, 1955, 1960, 1965, 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015,
		2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065}
}

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
	ZeroDistance int32        `arg:"--zero-distance" default:"-1" help:"Set the zero distance in meters."`
	Distances    distanceType `arg:"--distances" choices:"subsonic,low,medium,long,ultra" help:"Specify the distance range: 'subsonic', 'low', 'medium', 'long', or 'ultra'.\n\nZeroing:"`

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

func (z *zeros) String() string {
	return fmt.Sprintf("X: %.2f,\tY: %.2f", float64(-z.x)/1000, float64(z.y)/1000)
}

type distanceType string

const (
	subsonicRange distanceType = "subsonic"
	lowRange      distanceType = "low"
	mediumRange   distanceType = "medium"
	longRange     distanceType = "long"
	ultraRange    distanceType = "ultra"
)

type resultT struct {
	path            string
	err             error
	validationError any
	zero            *zeros
	newZero         *zeros
	distances       distanceType
	zeroDistance    int32
	recover         bool
	payload         *profedit.Payload
	switches        []*profedit.SwPos
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
	if r.distances != "" {
		updates = append(updates, fmt.Sprintf("\tNew range:\t%s", r.distances))
	}
	if r.zeroDistance > -1 {
		updates = append(updates, fmt.Sprintf("\tNew zero distance:\t%d", r.zeroDistance))
	}
	if r.switches != nil {
		updates = append(updates, "\tSwitches copied")
	}

	fmt.Println(log.FmtBlue(strings.Join(updates, "\n")))

	if r.validationError != nil && args.Verbose {
		log.Err("Not implemented")
	}
}

func (r *resultT) saveChanges(validate bool) {
	hasChanges := r.zeroDistance > 0 || r.distances != "" || r.newZero != nil || r.switches != nil

	if hasChanges {
		if !args.Force {
			var yesNo string
			fmt.Println(log.FmtYellow("Do you want to save changes? (Y/N): "))
			fmt.Scanln(&yesNo)
			yesNo = strings.TrimSpace(strings.ToUpper(yesNo))
			if yesNo != "Y" {
				log.Info("No changes have been saved.")
				return
			}
		}

		if r.recover {
			ext := filepath.Ext(r.path)
			base := strings.TrimSuffix(r.path, ext)
			r.path = base + "_recovered" + ext
		}

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

func updateDistances(result *resultT) {
	var curZeroDistance int32

	if result.zeroDistance < 0 {
		curZeroDistance = result.payload.Profile.Distances[result.payload.Profile.CZeroDistanceIdx]
	} else {
		curZeroDistance = result.zeroDistance * 100
	}

	switch result.distances {
	case subsonicRange, lowRange, mediumRange, longRange, ultraRange:
		result.payload.Profile.Distances = distances[result.distances]
	}

	if slices.Index(result.payload.Profile.Distances, curZeroDistance) < 0 {
		result.payload.Profile.Distances = append(result.payload.Profile.Distances, curZeroDistance)
	}
	slices.Sort(result.payload.Profile.Distances)
	result.payload.Profile.CZeroDistanceIdx = int32(slices.Index(result.payload.Profile.Distances, curZeroDistance))
}

func updateZeroing(result *resultT, validate bool) {

	if args.ZeroSync != "" {
		result.newZero = getZeroToSync(args.ZeroSync, validate)
	} else if len(args.ZeroOffset) == 2 {
		result.newZero = &zeros{
			x: result.zero.x + int32(args.ZeroOffset[0]*-1000),
			y: result.zero.y + int32(args.ZeroOffset[1]*1000),
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
	result := &resultT{
		path:         path,
		err:          err,
		payload:      payload,
		zero:         &zeros{payload.Profile.ZeroX, payload.Profile.ZeroY},
		distances:    args.Distances,
		zeroDistance: args.ZeroDistance,
		switches:     getSwitchesToCopy(args.CopySwitchesFrom, validate),
	}
	if result.err != nil {
		return *result
	}

	updateDistances(result)
	updateZeroing(result, validate)
	updateSwitches(result)

	return *result
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

	switch args.Distances {
	case subsonicRange, lowRange, mediumRange, longRange, ultraRange, "":

	default:
		argParser.Fail("Invalid --distances")
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

func main() {
	// Initialize the argument parser
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

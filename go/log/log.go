package log

import "fmt"

func Info(msg string) {
	fmt.Printf("\033[32mInfo: %s\033[0m\n", msg)
}

func Warn(msg string) {
	fmt.Printf("\033[1;33mWarning: %s\033[0m\n", msg)
}

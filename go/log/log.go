package log

import "fmt"

func Info(msg string) {
	fmt.Println(FmtGreen("Info: " + msg))
}

func Warn(msg string) {
	fmt.Println(FmtYellow("Warning: " + msg))
}

func Err(msg string) {
	fmt.Println(FmtRed("Error: " + msg))
}

func FmtBlue(msg string) string {
	return fmt.Sprintf("\033[94m%s\033[0m", msg)
}

func FmtGreen(msg string) string {
	return fmt.Sprintf("\033[32m%s\033[0m", msg)
}

func FmtYellow(msg string) string {
	return fmt.Sprintf("\033[1;33m%s\033[0m", msg)
}

func FmtRed(msg string) string {
	return fmt.Sprintf("\033[1;31m%s\033[0m", msg)
}

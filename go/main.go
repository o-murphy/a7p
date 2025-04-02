package main

import (
	"a7p/parser"
	"fmt"
)

func main() {
	filename := "example.a7p"
	data, err := parser.OpenFile(filename)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	payload, err := parser.Loads(data, true)
	if err != nil {
		fmt.Println("Error:", err)
	}
	fmt.Println(payload)
}

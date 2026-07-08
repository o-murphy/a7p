# a7p-go

#### Simple Go-lang wrapper for .a7p (ballistic profile) files \

## Table of Contents

- [Instalation](#instalation)
- [Usage](#usage)
- [Build](#build)
- [Dimensions](#dimensions)
- [Gallery of .a7p ballistic profiles](https://o-murphy.github.io/a7pIndex/)

## Description

Simple Go-lang wrapper for .a7p files

## Instalation

```bash
git clone https://github.com/o-murphy/a7p-go.git
cd a7p-go
go install .
```

## Usage

#### CLI-tool

```bash
a7p -h
Usage: a7p.exe [--version] [--recursive] [--force] [--unsafe] [--verbose] [--recover] [--zero-distance ZERO-DISTANCE] [--distances DISTANCES] [--zero-sync ZERO-SYNC] [--zero-offset ZERO-OFFSET] [--copy-switches-from COPY-SWITCHES-FROM] PATH

Positional arguments:
  PATH                   Path to the directory or a .a7p file to process

Options:
  --version, -V          Display the current version of the tool
  --recursive, -r        Recursively process files in the specified directory
  --force, -F            Force saving changes without confirmation
  --unsafe               Skip data validation (use with caution)

Single file only:
  --verbose              Enable verbose output for detailed logs. This option is only allowed for a single file.
  --recover              Attempt to recover from errors found in a file. This option is only allowed for a single file.

Distances:
  --zero-distance ZERO-DISTANCE
                         Set the zero distance in meters.
  --distances DISTANCES
                         Specify the distance range: 'subsonic', 'low', 'medium', 'long', or 'ultra'.

Zeroing:
  --zero-sync ZERO-SYNC
                         Synchronize zero using a specified configuration file.
  --zero-offset ZERO-OFFSET
                         Set the offset for zeroing in clicks (X_OFFSET and Y_OFFSET).

ARCHER device specific:
  --copy-switches-from COPY-SWITCHES-FROM
                         Copy switches from another a7p file.
  --help, -h             display this help and exit
```

#### Use as imported module
```go
//
```

## Build

### Prerequisites

1. **Go**  
   Download and install Go from [golang.org](https://golang.org/dl/).

2. **Git**  
   Download and install Git from [git-scm.com](https://git-scm.com/).

3. **Make**  
   - On **Linux/macOS**, `make` is typically pre-installed. If it's not, install it using a package manager:
     - **Linux**: `sudo apt-get install make`
     - **macOS**: `brew install make`
   - On **Windows**, you can install Make using [Chocolatey](https://chocolatey.org/):
     ```bash
     choco install make
     ```

4. **Protoc (Protocol Buffers Compiler)**  
   - **Linux**: Install `protoc` using `apt`:
     ```bash
     sudo apt-get install -y protobuf-compiler
     ```
   - **macOS**: Install `protoc` using Homebrew:
     ```bash
     brew install protobuf
     ```
   - **Windows**: Use [Chocolatey](https://chocolatey.org/) to install `protoc`:
     ```bash
     choco install protoc
     ```

This ensures you have all the necessary tools to build and work with Go, Git, Make, and Protocol Buffers.

<!-- * GCC compiler (only required if using cgo or specific C libraries, not needed for most Go projects) -->

#### Build Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/o-murphy/a7p-go
    cd a7p-go
    ```

2. Run the `make` command:
    ```bash
    make
    ```


## Dimensions

To obtain values from an .a7p profile in the desired units, you need to divide them by the multiplier.
For the reverse operation, you need to perform the inverse operation and convert to an integer.

| key                      | unit           | multiplier | desc                                        |
|--------------------------|----------------|------------|---------------------------------------------|
| sc_height                | mm             | 1          | sight height in mm                          |
| r_twist                  | inch           | 100        | positive twist value                        |
| c_zero_temperature       | C              | 1          | temperature at c_muzzle_velocity            |
| c_muzzle_velocity        | mps            | 10         | muzzle velocity at c_zero_temperature       |
| c_t_coeff                | %/15C          | 1000       | temperature sensitivity                     |
| c_zero_distance_idx      | <int>          | 10         | index of zero distance from distances table |
| c_zero_air_temperature   | C              | 1          | air temperature at zero                     |
| c_zero_air_pressure      | hPa            | 10         | air pressure at zero                        |
| c_zero_air_humidity      | %              | 1          | air humidity at zero                        |
| c_zero_p_temperature     | C              | 1          | powder temperature at zero                  |
| c_zero_w_pitch           | deg            | 1          | zeroing look angle                          |
| b_diameter               | inch           | 1000       | bullet diameter                             |
| b_weight                 | grain          | 10         | bullet weight                               |
| b_length                 | inch           | 1000       | bullet length                               |
| twist_dir                | RIGHT\|LEFT    |            | twist direction                             |
| bc_type                  | G1\|G7\|CUSTOM |            | g-func type                                 |
| distances                | m              | 100        | distances table in m                        |
| zero_x                   | <int>          | -1000      | zeroing h-clicks for specific device        |
| zero_y                   | <int>          | 1000       | zeroing v-clicks for specific device        |
| coef_rows.bc_cd (G1/G7)  |                | 10000      | bc coefficient for mv                       |
| coef_rows.mv    (G1/G7)  | mps            | 10         | mv for bc provided                          |
| coef_rows.bc_cd (CUSTOM) |                | 10000      | drag coefficient (Cd)                       |
| coef_rows.mv    (CUSTOM) | mach           | 10         | speed in mach                               |

# Table of Contents

- [Description](#description)
- [Instalation](#instalation)
- [Usage](#usage)
- [Dimensions](#dimensions)
- [Gallery of .a7p ballistic profiles](https://o-murphy.github.io/a7pIndex/)

## Description

Simple python3 wrapper for .a7p files \

## Instalation

#### with pypx as a CLI-tool

```bash
pipx install a7p
```

#### From PyPi:

```bash
pip install a7p
```

#### or latest from repository:

```bash
pip install https://github.com/o-murphy/a7p
```

## Usage

#### CLI-tool

```
a7p -h
usage: a7p 1.0.0b3 [-h] [-V] [-r] [-F] [--unsafe] [--verbose] [--recover] [-zd ZERO_DISTANCE] [-d {subsonic,low,medium,long,ultra}] [-zs ZERO_SYNC | -zo X_OFFSET Y_OFFSET] path

positional arguments:
  path                  Specify the path to the directory or a .a7p file to process.

options:
  -h, --help            show this help message and exit
  -V, --version         Display the current version of the tool.
  -r, --recursive       Recursively process files in the specified directory.
  -F, --force           Force saving changes without confirmation.
  --unsafe              Skip data validation (use with caution).

Single file specific options:
  --verbose             Enable verbose output for detailed logs. This option is only allowed for a single file.
  --recover             Attempt to recover from errors found in a file. This option is only allowed for a single file.

Distances:
  -zd ZERO_DISTANCE, --zero-distance ZERO_DISTANCE
                        Set the zero distance in meters.
  -d {subsonic,low,medium,long,ultra}, --distances {subsonic,low,medium,long,ultra}
                        Specify the distance range: 'subsonic', 'low', 'medium', 'long', or 'ultra'.

Zeroing:
  -zs ZERO_SYNC, --zero-sync ZERO_SYNC
                        Synchronize zero using a specified configuration file.
  -zo X_OFFSET Y_OFFSET, --zero-offset X_OFFSET Y_OFFSET
                        Set the offset for zeroing in clicks (X_OFFSET and Y_OFFSET).
```

#### Use as imported module

```python
import logging
import a7p
from a7p import exceptions, A7PFactory

# open file in binary mode
with open('data/test.a7p', 'rb') as fp:
    # read data from file
    try:
        payload = a7p.load(fp)
    except exceptions.A7PDataError as exc:  # raises if md5 crc not match
        logging.error(exc)

# accessing attributes as for default protobuf payload
profile_name = payload.profile.profile_name

# data conversion to common types
payload_json = a7p.to_json(payload)
payload_dict = a7p.to_dict(payload)
from_json = a7p.from_json(payload_json)
from_dict = a7p.from_dict(payload_dict)

# saving builded profile
with open('data/test.a7p', 'rb') as fp:
    a7p.dump(payload, fp)

# creating a new a7p Payload
payload = A7PFactory(
    meta=A7PFactory.Meta(
        name="test profile name",
    ),
    bullet=A7PFactory.Bullet(
        weight=175,
        length=0.9
    ),
    distances=A7PFactory.DistanceTable.LONG_RANGE
)
with open('data/test.a7p', 'wb') as fp:
    a7p.dump(payload, fp)
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

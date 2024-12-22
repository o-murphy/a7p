# Table of Contents

- [Description](#description)
- [Instalation](#instalation)
- [Usage](#usage)
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

usage: a7p 1.0.0b2 [-h] [-V] [-r] [--unsafe] [--verbose] [-F] [-zd ZERO_DISTANCE]
                   [-d {subsonic,low,medium,long,ultra}] [-zs ZERO_SYNC | -zo X_OFFSET Y_OFFSET]
                   path

positional arguments:
  path                  Specify the path to the directory or a .a7p file to process.

options:
  -h, --help            show this help message and exit
  -V, --version         Display the current version of the tool.
  -r, --recursive       Recursively process files in the specified directory.
  --unsafe              Skip data validation (use with caution).
  --verbose             Enable verbose output for detailed logs. This option is only allowed for a single file.
  -F, --force           Force saving changes without confirmation.

Distances:
  -zd, --zero-distance ZERO_DISTANCE
                        Set the zero distance in meters.
  -d, --distances {subsonic,low,medium,long,ultra}
                        Specify the distance range: 'subsonic', 'low', 'medium', 'long', or 'ultra'.

Zeroing:
  -zs, --zero-sync ZERO_SYNC
                        Synchronize zero using a specified configuration file.
  -zo, --zero-offset X_OFFSET Y_OFFSET
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

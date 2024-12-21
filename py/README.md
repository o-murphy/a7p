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
```bash
a7p -h
usage: a7p 0.0.10 [-h] [-V] [-r] [--unsafe] [--verbose] [-F] [-zd ZERO_DISTANCE] [-d {subsonic,low,medium,long,ultra}] [-zs ZERO_SYNC | -zo X_OFFSET Y_OFFSET] path

positional arguments:
  path                  Path to the directory or file

options:
  -h, --help            show this help message and exit
  -V, --version         show program`s version number and exit
  -r, --recursive       Recursively walk files
  --unsafe              Skip validation
  --verbose             Verbose
  -F, --force           Force changes saving

Distances:
  -zd ZERO_DISTANCE, --zero-distance ZERO_DISTANCE
                        Set zero distance in meters
  -d {subsonic,low,medium,long,ultra}, --distances {subsonic,low,medium,long,ultra}
                        Set distances range

Zeroing:
  -zs ZERO_SYNC, --zero-sync ZERO_SYNC
                        Synchronize zero
  -zo X_OFFSET Y_OFFSET, --zero-offset X_OFFSET Y_OFFSET
                        Set clicks offset

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
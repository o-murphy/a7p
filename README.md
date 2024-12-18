# Table of Contents

- [Description](#description)
- [Instalation](#instalation)
- [Usage](#usage)
- [Gallery](#gallery)

## Description

Simple python3 wrapper for .a7p files \

## Instalation

#### with pypx
```bash
pipx install a7p
```

#### As common from PyPi:
```bash
pip install a7p
```

#### or latest from repository:
```bash
git clone https://github.com/o-murphy/a7p
cd a7p_transfer_example/a7p_py
python setup.py install
```

This command builds the Docker image and tags it as `go-server`.

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

#### Direct

```python
import logging
from a7p import A7PFile, A7PDataError
from a7p.factory import A7PFactory

# open file in binary mode
with open('data/test.a7p', 'rb') as fp:

    # read data from file
    try:
        profile_opj = A7PFile.load(fp)
    except A7PDataError as exc:  # raises if md5 crc not match
        logging.error(exc)

# accessing attributes as for default protobuf payload
profile_name = profile_opj.profile.profile_name    

# data conversion to common types
as_json = A7PFile.to_json(profile_opj)
as_dict = A7PFile.to_dict(profile_opj)
from_json = A7PFile.from_json(profile_opj)
from_dict = A7PFile.from_dict(profile_opj)

# saving builded profile
with open('data/test.a7p', 'rb') as fp:
    A7PFile.dump(profile_opj, fp)

    
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
    A7PFile.dump(payload, fp)
```

## Gallery
Latest updates available at **[JsDelivr CDN](https://cdn.jsdelivr.net/gh/o-murphy/a7p/gallery/)**
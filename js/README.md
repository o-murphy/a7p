# a7p-js

[![NPM Version](https://img.shields.io/npm/v/a7p-js?logo=npm)
](https://www.npmjs.com/package/a7p-js)
[![npm downloads](https://img.shields.io/npm/dm/a7p-js.svg)](https://www.npmjs.com/package/a7p-js)
[![license](https://img.shields.io/npm/l/a7p-js.svg)](LICENSE)

Wrapper for `.a7p` files

`.a7p` is the most common ballistic profile format for the latest `Archer` thermal vision devices

## Table of Contents

- [a7p-js](#a7p-js)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [In a Node.js / TypeScript project](#in-a-nodejs--typescript-project)
    - [In a browser, via CDN](#in-a-browser-via-cdn)
  - [Dimensions](#dimensions)
    - [Build notes](#build-notes)

## Installation

```shell
yarn add a7p-js
# or
npm install a7p-js
```

## Usage

### In a Node.js / TypeScript project

```ts
import { readFile } from 'fs/promises';
import { decode, encode, ValidationError } from 'a7p-js';

const bytes = await readFile('./example.a7p');

try {
  // decode a .a7p file into a plain Payload object
  const payload = decode(bytes);
  console.log(payload.profile.profileName);
  console.log(payload.profile.switches);

  // encode a Payload back into .a7p bytes
  const buffer = encode(payload);
} catch (error) {
  if (error instanceof ValidationError) {
    error.errors.forEach((message) => console.log(message));
  } else {
    throw error;
  }
}
```

### In a browser, via CDN

`a7p-js` ships as an ES module, so it can be imported directly from a CDN such as
[esm.sh](https://esm.sh) or [jsDelivr](https://www.jsdelivr.com/) with no build step:

```html
<script type="module">
  import { decode } from "https://esm.sh/a7p-js@1.1.0";

  const input = document.querySelector('input[type="file"]');
  input.addEventListener('change', async () => {
    const file = input.files[0];
    const buffer = await file.arrayBuffer();
    const payload = decode(buffer);
    console.log(payload.profile);
  });
</script>
```

See it in action in this [live example](https://gist.github.com/o-murphy/d4e8562fe8308ab2542fb1d22fd7afd6), which combines `a7p-js` with [js-ballistics](https://github.com/o-murphy/js-ballistics) to compare trajectories from `.a7p` profiles entirely in the browser.

## Dimensions

To obtain values from an .a7p profile in the desired units, you need to divide them by the multiplier.
For the reverse operation, you need to perform the inverse operation and convert to an integer.

| key                      | unit           | multiplier | desc                                        |
|--------------------------|----------------|------------|---------------------------------------------|
| scHeight                 | mm             | 1          | sight height in mm                          |
| rTwist                   | inch           | 100        | positive twist value                        |
| cZeroTemperature         | C              | 1          | temperature at cMuzzleVelocity              |
| cMuzzleVelocity          | mps            | 10         | muzzle velocity at cZeroTemperature         |
| cTCoeff                  | %/15C          | 1000       | temperature sensitivity                     |
| cZeroDistanceIdx         | \<int\>        | 10         | index of zero distance from distances table |
| cZeroAirTemperature      | C              | 1          | air temperature at zero                     |
| cZeroAirPressure         | hPa            | 10         | air pressure at zero                        |
| cZeroAirHumidity         | %              | 1          | air humidity at zero                        |
| cZeroPTemperature        | C              | 1          | powder temperature at zero                  |
| cZeroWPitch              | deg            | 1          | zeroing look angle                          |
| bDiameter                | inch           | 1000       | bullet diameter                             |
| bWeight                  | grain          | 10         | bullet weight                               |
| bLength                  | inch           | 1000       | bullet length                               |
| twistDir                 | RIGHT\|LEFT    |            | twist direction                             |
| bcType                   | G1\|G7\|CUSTOM |            | g-func type                                 |
| distances                | m              | 100        | distances table in m                        |
| zeroX                    | \<int\>        | -1000      | zeroing h-clicks for specific device        |
| zeroY                    | \<int\>        | 1000       | zeroing v-clicks for specific device        |
| coefRows[].bcCd (G1/G7)  |                | 10000      | bc coefficient for mv                       |
| coefRows[].mv   (G1/G7)  | mps            | 10         | mv for bc provided                          |
| coefRows[].bcCd (CUSTOM) |                | 10000      | drag coefficient (Cd)                       |
| coefRows[].mv   (CUSTOM) | mach           | 10         | speed in mach                               |

### Build notes
Install & build proto
```shell
yarn install
yarn build:proto
```
<!-- 
Replace import declarations in profedit.js and profedit.d.ts
```
import * as $protobuf from "protobufjs/minimal"; -> import $protobuf from "protobufjs";
``` -->

Build
```shell
yarn build
npx cpy 'src/profedit.*' 'dist/'
```

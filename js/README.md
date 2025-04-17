# Wrapper for .a7p files


### Build notes
Install & build proto
```shell
yarn install
yarn build:proto
```

Replace import declarations in profedit.js and profedit.d.ts
```
import * as $protobuf from "protobufjs/minimal"; -> import $protobuf from "protobufjs";
```

Build
```shell
yarn build
npx cpy 'src/profedit.*' 'dist/'
```
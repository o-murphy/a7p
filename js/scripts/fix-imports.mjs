import { readFile, writeFile } from 'fs/promises';

const filesToUpdate = ['src/profedit.js', 'src/profedit.d.ts'];

async function replaceImports() {
  // The regular expression matches either "protobufjs" or "protobufjs/minimal".
  const findRegex = /import \* as \$protobuf from "protobufjs(\/minimal)?";/;
  const replace = 'import $protobuf from "protobufjs";';

  for (const file of filesToUpdate) {
    try {
      let content = await readFile(file, 'utf8');
      
      // Use the regex with .replace()
      content = content.replace(findRegex, replace);
      
      await writeFile(file, content);
      console.log(`Successfully updated: ${file}`);
    } catch (error) {
      console.error(`Error updating ${file}:`, error);
    }
  }
}

replaceImports();
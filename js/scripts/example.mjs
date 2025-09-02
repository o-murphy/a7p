import { ValidationError } from 'a7p-js';
import { decode, encode } from 'a7p-js';
import { readFile } from 'fs/promises';

async function readFileAsBytes(path) {
    try {
        const buffer = await readFile(path); // returns a Buffer
        const byteArray = new Uint8Array(buffer); // convert to Uint8Array if needed
        return byteArray;
    } catch (err) {
        console.error('Failed to read file:', err);
        return null;
    }
}

async function main() {
    const bytes = await readFileAsBytes('./scripts/example2.a7p').catch(err => console.log(err));

    if (bytes) {
        try {
            const payload = decode(bytes);
            console.log(payload.profile);
            console.log(payload.profile.switches);
    
            const buf = encode(payload);
            console.log(buf);
        } catch (error) {
            if (error instanceof ValidationError) {
                console.log(error.errors)
                error.errors.forEach(x => {
                    console.log(x)
                })
            }
        }

    }
}

main();

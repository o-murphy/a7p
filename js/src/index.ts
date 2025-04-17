import CryptoJS from 'crypto-js';
import { toByteArray, fromByteArray } from 'base64-js';
import { Payload } from './types.js';
import { validate } from './validate.js'
import { profedit } from './profedit.js';
import { A7pError, DecodeError, EncodeError, ValidationError, InvalidBcTypeError } from './errors.js';


const MD5_LENGTH = 32;



const md5 = (bytes: Uint8Array): string => {
    const wordArray = CryptoJS.lib.WordArray.create(bytes as any); // works even though TS complains
    return CryptoJS.MD5(wordArray).toString(CryptoJS.enc.Hex);
}


const encode = (payload: Payload): ArrayBuffer => {
    try {
        // Validate the payload
        validate(payload);

        // Encode the payload
        const payloadMessage = profedit.Payload.fromObject(payload);
        const encoded = profedit.Payload.encode(payloadMessage).finish(); // Uint8Array

        // Create checksum
        const checksum = md5(encoded); // SparkMD5.hash(Uint8Array) or convert manually
        const checksumBytes = new TextEncoder().encode(checksum); // 32 ASCII characters

        // Combine checksum and encoded payload
        const final = new Uint8Array(checksumBytes.length + encoded.length);
        final.set(checksumBytes, 0);
        final.set(encoded, checksumBytes.length);

        // Return the final buffer
        return final.buffer;
    } catch (error: unknown) {
        // Enhanced error handling with rethrowing
        if (error instanceof ValidationError) {
            // Handling validation errors
            console.error("Validation error occurred:", error.message);
            throw error; // Rethrow the existing ValidationError
        } else if (error instanceof EncodeError) {
            // Handling encoding errors
            console.error("Encoding error occurred:", error.message);
            throw error; // Rethrow the existing EncodeError
        } else if (error instanceof Error) {
            // Generic error handling
            console.error("Error occurred during encoding:", error.message);
            throw new EncodeError(`Error encoding payload: ${error.message}`);
        } else {
            // Handling unknown errors
            console.error("Unknown error occurred:", error);
            throw new A7pError("Unknown error occurred during encoding", "EncodeError");
        }
    }
}

const decode = (buffer: ArrayBuffer): Payload => {
    try {
        const dataBytes = new Uint8Array(buffer);
        const fullData = toByteArray(fromByteArray(dataBytes));
        const checksumBytes = fullData.subarray(0, MD5_LENGTH);
        const checksum = String.fromCharCode(...checksumBytes);
        const encoded = fullData.subarray(MD5_LENGTH);
        const calculatedChecksum = md5(encoded);

        // Check checksum validity
        if (checksum !== calculatedChecksum) {
            console.error("Invalid A7P file checksum");
            throw new DecodeError("Invalid checksum in A7P file");
        }

        // Decode payload
        const payloadMessage = profedit.Payload.decode(encoded);
        const payload = profedit.Payload.toObject(payloadMessage, {
            longs: Number,
            enums: String,
            bytes: String,
            defaults: true,
            arrays: true,
        }) as Payload;

        // Validate payload
        validate(payload);

        return payload;
    } catch (error: unknown) {
        // Enhanced error handling with specific error types
        if (error instanceof DecodeError) {
            console.error("Decode error occurred:", error.message);
            throw error; // Rethrow existing DecodeError
        } else if (error instanceof ValidationError) {
            console.error("Validation error occurred during decoding:", error.message);
            throw error; // Rethrow existing ValidationError
        } else if (error instanceof Error) {
            console.error("Error occurred during decoding:", error.message);
            throw new DecodeError(`Error decoding payload: ${error.message}`);
        } else {
            console.error("Unknown error occurred:", error);
            throw new A7pError("Unknown error occurred during decoding", "DecodeError");
        }
    }
}


export {
    decode,
    encode,
    profedit,
    validate,
    A7pError,
    EncodeError,
    DecodeError,
    ValidationError,
    InvalidBcTypeError,
}
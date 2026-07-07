import CryptoJS from 'crypto-js';
import { toByteArray, fromByteArray } from 'base64-js';
import { Payload, BcType, TwistDir } from './types.js';
import { validate } from './validate.js'
import { Payload as ProtoPayload, gTypeToJSON, twistDirToJSON, dTypeToJSON } from './profedit.js';
import { A7pError, DecodeError, EncodeError, ValidationError, InvalidBcTypeError } from './errors.js';


const MD5_LENGTH = 32;


const md5 = (bytes: Uint8Array): string => {
    const wordArray = CryptoJS.lib.WordArray.create(bytes as any);
    return CryptoJS.MD5(wordArray).toString(CryptoJS.enc.Hex);
}


const encode = (payload: Payload): ArrayBuffer => {
    try {
        validate(payload);

        const protoPayload = ProtoPayload.fromJSON(payload);
        const encoded = ProtoPayload.encode(protoPayload).finish();

        const checksum = md5(encoded);
        const checksumBytes = new TextEncoder().encode(checksum);

        const final = new Uint8Array(checksumBytes.length + encoded.length);
        final.set(checksumBytes, 0);
        final.set(encoded, checksumBytes.length);

        return final.buffer;
    } catch (error: unknown) {
        if (error instanceof ValidationError) {
            console.error("Validation error occurred:", error.message);
            throw error;
        } else if (error instanceof EncodeError) {
            console.error("Encoding error occurred:", error.message);
            throw error;
        } else if (error instanceof Error) {
            console.error("Error occurred during encoding:", error.message);
            throw new EncodeError(`Error encoding payload: ${error.message}`);
        } else {
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

        if (checksum !== calculatedChecksum) {
            console.error("Invalid A7P file checksum");
            throw new DecodeError("Invalid checksum in A7P file");
        }

        const proto = ProtoPayload.decode(encoded);
        const profile = proto.profile!;
        const payload: Payload = {
            profile: {
                ...profile,
                bcType: gTypeToJSON(profile.bcType) as BcType,
                twistDir: twistDirToJSON(profile.twistDir) as TwistDir,
                switches: profile.switches.map(sw => ({
                    ...sw,
                    distanceFrom: dTypeToJSON(sw.distanceFrom) as 'INDEX' | 'VALUE',
                })),
            }
        };

        validate(payload);
        return payload;
    } catch (error: unknown) {
        if (error instanceof DecodeError) {
            console.error("Decode error occurred:", error.message);
            throw error;
        } else if (error instanceof ValidationError) {
            console.error("Validation error occurred during decoding:", error.message);
            throw error;
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
    validate,
    A7pError,
    EncodeError,
    DecodeError,
    ValidationError,
    InvalidBcTypeError,
}

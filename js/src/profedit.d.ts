import $protobuf from "protobufjs";

import Long = require("long");
/** Namespace profedit. */
export namespace profedit {

    /** Properties of a Payload. */
    interface IPayload {

        /** Payload profile */
        profile?: (profedit.IProfile|null);
    }

    /** Represents a Payload. */
    class Payload implements IPayload {

        /**
         * Constructs a new Payload.
         * @param [properties] Properties to set
         */
        constructor(properties?: profedit.IPayload);

        /** Payload profile. */
        public profile?: (profedit.IProfile|null);

        /**
         * Creates a new Payload instance using the specified properties.
         * @param [properties] Properties to set
         * @returns Payload instance
         */
        public static create(properties?: profedit.IPayload): profedit.Payload;

        /**
         * Encodes the specified Payload message. Does not implicitly {@link profedit.Payload.verify|verify} messages.
         * @param message Payload message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        public static encode(message: profedit.IPayload, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified Payload message, length delimited. Does not implicitly {@link profedit.Payload.verify|verify} messages.
         * @param message Payload message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        public static encodeDelimited(message: profedit.IPayload, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a Payload message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns Payload
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): profedit.Payload;

        /**
         * Decodes a Payload message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns Payload
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): profedit.Payload;

        /**
         * Verifies a Payload message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        public static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a Payload message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns Payload
         */
        public static fromObject(object: { [k: string]: any }): profedit.Payload;

        /**
         * Creates a plain object from a Payload message. Also converts values to other types if specified.
         * @param message Payload
         * @param [options] Conversion options
         * @returns Plain object
         */
        public static toObject(message: profedit.Payload, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this Payload to JSON.
         * @returns JSON object
         */
        public toJSON(): { [k: string]: any };

        /**
         * Gets the default type url for Payload
         * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
         * @returns The default type url
         */
        public static getTypeUrl(typeUrlPrefix?: string): string;
    }

    /** Properties of a CoefRow. */
    interface ICoefRow {

        /** CoefRow bcCd */
        bcCd?: (number|null);

        /** CoefRow mv */
        mv?: (number|null);
    }

    /** Represents a CoefRow. */
    class CoefRow implements ICoefRow {

        /**
         * Constructs a new CoefRow.
         * @param [properties] Properties to set
         */
        constructor(properties?: profedit.ICoefRow);

        /** CoefRow bcCd. */
        public bcCd: number;

        /** CoefRow mv. */
        public mv: number;

        /**
         * Creates a new CoefRow instance using the specified properties.
         * @param [properties] Properties to set
         * @returns CoefRow instance
         */
        public static create(properties?: profedit.ICoefRow): profedit.CoefRow;

        /**
         * Encodes the specified CoefRow message. Does not implicitly {@link profedit.CoefRow.verify|verify} messages.
         * @param message CoefRow message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        public static encode(message: profedit.ICoefRow, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified CoefRow message, length delimited. Does not implicitly {@link profedit.CoefRow.verify|verify} messages.
         * @param message CoefRow message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        public static encodeDelimited(message: profedit.ICoefRow, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a CoefRow message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns CoefRow
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): profedit.CoefRow;

        /**
         * Decodes a CoefRow message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns CoefRow
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): profedit.CoefRow;

        /**
         * Verifies a CoefRow message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        public static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a CoefRow message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns CoefRow
         */
        public static fromObject(object: { [k: string]: any }): profedit.CoefRow;

        /**
         * Creates a plain object from a CoefRow message. Also converts values to other types if specified.
         * @param message CoefRow
         * @param [options] Conversion options
         * @returns Plain object
         */
        public static toObject(message: profedit.CoefRow, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this CoefRow to JSON.
         * @returns JSON object
         */
        public toJSON(): { [k: string]: any };

        /**
         * Gets the default type url for CoefRow
         * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
         * @returns The default type url
         */
        public static getTypeUrl(typeUrlPrefix?: string): string;
    }

    /** DType enum. */
    enum DType {
        VALUE = 0,
        INDEX = 1
    }

    /** Properties of a SwPos. */
    interface ISwPos {

        /** SwPos cIdx */
        cIdx?: (number|null);

        /** SwPos reticleIdx */
        reticleIdx?: (number|null);

        /** SwPos zoom */
        zoom?: (number|null);

        /** SwPos distance */
        distance?: (number|null);

        /** SwPos distanceFrom */
        distanceFrom?: (profedit.DType|null);
    }

    /** Represents a SwPos. */
    class SwPos implements ISwPos {

        /**
         * Constructs a new SwPos.
         * @param [properties] Properties to set
         */
        constructor(properties?: profedit.ISwPos);

        /** SwPos cIdx. */
        public cIdx: number;

        /** SwPos reticleIdx. */
        public reticleIdx: number;

        /** SwPos zoom. */
        public zoom: number;

        /** SwPos distance. */
        public distance: number;

        /** SwPos distanceFrom. */
        public distanceFrom: profedit.DType;

        /**
         * Creates a new SwPos instance using the specified properties.
         * @param [properties] Properties to set
         * @returns SwPos instance
         */
        public static create(properties?: profedit.ISwPos): profedit.SwPos;

        /**
         * Encodes the specified SwPos message. Does not implicitly {@link profedit.SwPos.verify|verify} messages.
         * @param message SwPos message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        public static encode(message: profedit.ISwPos, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified SwPos message, length delimited. Does not implicitly {@link profedit.SwPos.verify|verify} messages.
         * @param message SwPos message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        public static encodeDelimited(message: profedit.ISwPos, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a SwPos message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns SwPos
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): profedit.SwPos;

        /**
         * Decodes a SwPos message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns SwPos
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): profedit.SwPos;

        /**
         * Verifies a SwPos message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        public static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a SwPos message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns SwPos
         */
        public static fromObject(object: { [k: string]: any }): profedit.SwPos;

        /**
         * Creates a plain object from a SwPos message. Also converts values to other types if specified.
         * @param message SwPos
         * @param [options] Conversion options
         * @returns Plain object
         */
        public static toObject(message: profedit.SwPos, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this SwPos to JSON.
         * @returns JSON object
         */
        public toJSON(): { [k: string]: any };

        /**
         * Gets the default type url for SwPos
         * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
         * @returns The default type url
         */
        public static getTypeUrl(typeUrlPrefix?: string): string;
    }

    /** GType enum. */
    enum GType {
        G1 = 0,
        G7 = 1,
        CUSTOM = 2
    }

    /** TwistDir enum. */
    enum TwistDir {
        RIGHT = 0,
        LEFT = 1
    }

    /** Properties of a Profile. */
    interface IProfile {

        /** Profile profileName */
        profileName?: (string|null);

        /** Profile cartridgeName */
        cartridgeName?: (string|null);

        /** Profile bulletName */
        bulletName?: (string|null);

        /** Profile shortNameTop */
        shortNameTop?: (string|null);

        /** Profile shortNameBot */
        shortNameBot?: (string|null);

        /** Profile userNote */
        userNote?: (string|null);

        /** Profile zeroX */
        zeroX?: (number|null);

        /** Profile zeroY */
        zeroY?: (number|null);

        /** Profile scHeight */
        scHeight?: (number|null);

        /** Profile rTwist */
        rTwist?: (number|null);

        /** Profile cMuzzleVelocity */
        cMuzzleVelocity?: (number|null);

        /** Profile cZeroTemperature */
        cZeroTemperature?: (number|null);

        /** Profile cTCoeff */
        cTCoeff?: (number|null);

        /** Profile cZeroDistanceIdx */
        cZeroDistanceIdx?: (number|null);

        /** Profile cZeroAirTemperature */
        cZeroAirTemperature?: (number|null);

        /** Profile cZeroAirPressure */
        cZeroAirPressure?: (number|null);

        /** Profile cZeroAirHumidity */
        cZeroAirHumidity?: (number|null);

        /** Profile cZeroWPitch */
        cZeroWPitch?: (number|null);

        /** Profile cZeroPTemperature */
        cZeroPTemperature?: (number|null);

        /** Profile bDiameter */
        bDiameter?: (number|null);

        /** Profile bWeight */
        bWeight?: (number|null);

        /** Profile bLength */
        bLength?: (number|null);

        /** Profile twistDir */
        twistDir?: (profedit.TwistDir|null);

        /** Profile bcType */
        bcType?: (profedit.GType|null);

        /** Profile switches */
        switches?: (profedit.ISwPos[]|null);

        /** Profile distances */
        distances?: (number[]|null);

        /** Profile coefRows */
        coefRows?: (profedit.ICoefRow[]|null);

        /** Profile caliber */
        caliber?: (string|null);

        /** Profile deviceUuid */
        deviceUuid?: (string|null);
    }

    /** Represents a Profile. */
    class Profile implements IProfile {

        /**
         * Constructs a new Profile.
         * @param [properties] Properties to set
         */
        constructor(properties?: profedit.IProfile);

        /** Profile profileName. */
        public profileName: string;

        /** Profile cartridgeName. */
        public cartridgeName: string;

        /** Profile bulletName. */
        public bulletName: string;

        /** Profile shortNameTop. */
        public shortNameTop: string;

        /** Profile shortNameBot. */
        public shortNameBot: string;

        /** Profile userNote. */
        public userNote: string;

        /** Profile zeroX. */
        public zeroX: number;

        /** Profile zeroY. */
        public zeroY: number;

        /** Profile scHeight. */
        public scHeight: number;

        /** Profile rTwist. */
        public rTwist: number;

        /** Profile cMuzzleVelocity. */
        public cMuzzleVelocity: number;

        /** Profile cZeroTemperature. */
        public cZeroTemperature: number;

        /** Profile cTCoeff. */
        public cTCoeff: number;

        /** Profile cZeroDistanceIdx. */
        public cZeroDistanceIdx: number;

        /** Profile cZeroAirTemperature. */
        public cZeroAirTemperature: number;

        /** Profile cZeroAirPressure. */
        public cZeroAirPressure: number;

        /** Profile cZeroAirHumidity. */
        public cZeroAirHumidity: number;

        /** Profile cZeroWPitch. */
        public cZeroWPitch: number;

        /** Profile cZeroPTemperature. */
        public cZeroPTemperature: number;

        /** Profile bDiameter. */
        public bDiameter: number;

        /** Profile bWeight. */
        public bWeight: number;

        /** Profile bLength. */
        public bLength: number;

        /** Profile twistDir. */
        public twistDir: profedit.TwistDir;

        /** Profile bcType. */
        public bcType: profedit.GType;

        /** Profile switches. */
        public switches: profedit.ISwPos[];

        /** Profile distances. */
        public distances: number[];

        /** Profile coefRows. */
        public coefRows: profedit.ICoefRow[];

        /** Profile caliber. */
        public caliber: string;

        /** Profile deviceUuid. */
        public deviceUuid: string;

        /**
         * Creates a new Profile instance using the specified properties.
         * @param [properties] Properties to set
         * @returns Profile instance
         */
        public static create(properties?: profedit.IProfile): profedit.Profile;

        /**
         * Encodes the specified Profile message. Does not implicitly {@link profedit.Profile.verify|verify} messages.
         * @param message Profile message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        public static encode(message: profedit.IProfile, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified Profile message, length delimited. Does not implicitly {@link profedit.Profile.verify|verify} messages.
         * @param message Profile message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        public static encodeDelimited(message: profedit.IProfile, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a Profile message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns Profile
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): profedit.Profile;

        /**
         * Decodes a Profile message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns Profile
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): profedit.Profile;

        /**
         * Verifies a Profile message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        public static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a Profile message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns Profile
         */
        public static fromObject(object: { [k: string]: any }): profedit.Profile;

        /**
         * Creates a plain object from a Profile message. Also converts values to other types if specified.
         * @param message Profile
         * @param [options] Conversion options
         * @returns Plain object
         */
        public static toObject(message: profedit.Profile, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this Profile to JSON.
         * @returns JSON object
         */
        public toJSON(): { [k: string]: any };

        /**
         * Gets the default type url for Profile
         * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
         * @returns The default type url
         */
        public static getTypeUrl(typeUrlPrefix?: string): string;
    }
}

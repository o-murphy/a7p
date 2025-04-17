/*eslint-disable block-scoped-var, id-length, no-control-regex, no-magic-numbers, no-prototype-builtins, no-redeclare, no-shadow, no-var, sort-vars*/
import * as $protobuf from "protobufjs/minimal";

// Common aliases
const $Reader = $protobuf.Reader, $Writer = $protobuf.Writer, $util = $protobuf.util;

// Exported root namespace
const $root = $protobuf.roots["default"] || ($protobuf.roots["default"] = {});

export const profedit = $root.profedit = (() => {

    /**
     * Namespace profedit.
     * @exports profedit
     * @namespace
     */
    const profedit = {};

    profedit.Payload = (function() {

        /**
         * Properties of a Payload.
         * @memberof profedit
         * @interface IPayload
         * @property {profedit.IProfile|null} [profile] Payload profile
         */

        /**
         * Constructs a new Payload.
         * @memberof profedit
         * @classdesc Represents a Payload.
         * @implements IPayload
         * @constructor
         * @param {profedit.IPayload=} [properties] Properties to set
         */
        function Payload(properties) {
            if (properties)
                for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null)
                        this[keys[i]] = properties[keys[i]];
        }

        /**
         * Payload profile.
         * @member {profedit.IProfile|null|undefined} profile
         * @memberof profedit.Payload
         * @instance
         */
        Payload.prototype.profile = null;

        /**
         * Creates a new Payload instance using the specified properties.
         * @function create
         * @memberof profedit.Payload
         * @static
         * @param {profedit.IPayload=} [properties] Properties to set
         * @returns {profedit.Payload} Payload instance
         */
        Payload.create = function create(properties) {
            return new Payload(properties);
        };

        /**
         * Encodes the specified Payload message. Does not implicitly {@link profedit.Payload.verify|verify} messages.
         * @function encode
         * @memberof profedit.Payload
         * @static
         * @param {profedit.IPayload} message Payload message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        Payload.encode = function encode(message, writer) {
            if (!writer)
                writer = $Writer.create();
            if (message.profile != null && Object.hasOwnProperty.call(message, "profile"))
                $root.profedit.Profile.encode(message.profile, writer.uint32(/* id 1, wireType 2 =*/10).fork()).ldelim();
            return writer;
        };

        /**
         * Encodes the specified Payload message, length delimited. Does not implicitly {@link profedit.Payload.verify|verify} messages.
         * @function encodeDelimited
         * @memberof profedit.Payload
         * @static
         * @param {profedit.IPayload} message Payload message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        Payload.encodeDelimited = function encodeDelimited(message, writer) {
            return this.encode(message, writer).ldelim();
        };

        /**
         * Decodes a Payload message from the specified reader or buffer.
         * @function decode
         * @memberof profedit.Payload
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {profedit.Payload} Payload
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        Payload.decode = function decode(reader, length, error) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            let end = length === undefined ? reader.len : reader.pos + length, message = new $root.profedit.Payload();
            while (reader.pos < end) {
                let tag = reader.uint32();
                if (tag === error)
                    break;
                switch (tag >>> 3) {
                case 1: {
                        message.profile = $root.profedit.Profile.decode(reader, reader.uint32());
                        break;
                    }
                default:
                    reader.skipType(tag & 7);
                    break;
                }
            }
            return message;
        };

        /**
         * Decodes a Payload message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof profedit.Payload
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {profedit.Payload} Payload
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        Payload.decodeDelimited = function decodeDelimited(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a Payload message.
         * @function verify
         * @memberof profedit.Payload
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        Payload.verify = function verify(message) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (message.profile != null && message.hasOwnProperty("profile")) {
                let error = $root.profedit.Profile.verify(message.profile);
                if (error)
                    return "profile." + error;
            }
            return null;
        };

        /**
         * Creates a Payload message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof profedit.Payload
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {profedit.Payload} Payload
         */
        Payload.fromObject = function fromObject(object) {
            if (object instanceof $root.profedit.Payload)
                return object;
            let message = new $root.profedit.Payload();
            if (object.profile != null) {
                if (typeof object.profile !== "object")
                    throw TypeError(".profedit.Payload.profile: object expected");
                message.profile = $root.profedit.Profile.fromObject(object.profile);
            }
            return message;
        };

        /**
         * Creates a plain object from a Payload message. Also converts values to other types if specified.
         * @function toObject
         * @memberof profedit.Payload
         * @static
         * @param {profedit.Payload} message Payload
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        Payload.toObject = function toObject(message, options) {
            if (!options)
                options = {};
            let object = {};
            if (options.defaults)
                object.profile = null;
            if (message.profile != null && message.hasOwnProperty("profile"))
                object.profile = $root.profedit.Profile.toObject(message.profile, options);
            return object;
        };

        /**
         * Converts this Payload to JSON.
         * @function toJSON
         * @memberof profedit.Payload
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        Payload.prototype.toJSON = function toJSON() {
            return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the default type url for Payload
         * @function getTypeUrl
         * @memberof profedit.Payload
         * @static
         * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
         * @returns {string} The default type url
         */
        Payload.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
            if (typeUrlPrefix === undefined) {
                typeUrlPrefix = "type.googleapis.com";
            }
            return typeUrlPrefix + "/profedit.Payload";
        };

        return Payload;
    })();

    profedit.CoefRow = (function() {

        /**
         * Properties of a CoefRow.
         * @memberof profedit
         * @interface ICoefRow
         * @property {number|null} [bcCd] CoefRow bcCd
         * @property {number|null} [mv] CoefRow mv
         */

        /**
         * Constructs a new CoefRow.
         * @memberof profedit
         * @classdesc Represents a CoefRow.
         * @implements ICoefRow
         * @constructor
         * @param {profedit.ICoefRow=} [properties] Properties to set
         */
        function CoefRow(properties) {
            if (properties)
                for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null)
                        this[keys[i]] = properties[keys[i]];
        }

        /**
         * CoefRow bcCd.
         * @member {number} bcCd
         * @memberof profedit.CoefRow
         * @instance
         */
        CoefRow.prototype.bcCd = 0;

        /**
         * CoefRow mv.
         * @member {number} mv
         * @memberof profedit.CoefRow
         * @instance
         */
        CoefRow.prototype.mv = 0;

        /**
         * Creates a new CoefRow instance using the specified properties.
         * @function create
         * @memberof profedit.CoefRow
         * @static
         * @param {profedit.ICoefRow=} [properties] Properties to set
         * @returns {profedit.CoefRow} CoefRow instance
         */
        CoefRow.create = function create(properties) {
            return new CoefRow(properties);
        };

        /**
         * Encodes the specified CoefRow message. Does not implicitly {@link profedit.CoefRow.verify|verify} messages.
         * @function encode
         * @memberof profedit.CoefRow
         * @static
         * @param {profedit.ICoefRow} message CoefRow message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        CoefRow.encode = function encode(message, writer) {
            if (!writer)
                writer = $Writer.create();
            if (message.bcCd != null && Object.hasOwnProperty.call(message, "bcCd"))
                writer.uint32(/* id 1, wireType 0 =*/8).int32(message.bcCd);
            if (message.mv != null && Object.hasOwnProperty.call(message, "mv"))
                writer.uint32(/* id 2, wireType 0 =*/16).int32(message.mv);
            return writer;
        };

        /**
         * Encodes the specified CoefRow message, length delimited. Does not implicitly {@link profedit.CoefRow.verify|verify} messages.
         * @function encodeDelimited
         * @memberof profedit.CoefRow
         * @static
         * @param {profedit.ICoefRow} message CoefRow message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        CoefRow.encodeDelimited = function encodeDelimited(message, writer) {
            return this.encode(message, writer).ldelim();
        };

        /**
         * Decodes a CoefRow message from the specified reader or buffer.
         * @function decode
         * @memberof profedit.CoefRow
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {profedit.CoefRow} CoefRow
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        CoefRow.decode = function decode(reader, length, error) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            let end = length === undefined ? reader.len : reader.pos + length, message = new $root.profedit.CoefRow();
            while (reader.pos < end) {
                let tag = reader.uint32();
                if (tag === error)
                    break;
                switch (tag >>> 3) {
                case 1: {
                        message.bcCd = reader.int32();
                        break;
                    }
                case 2: {
                        message.mv = reader.int32();
                        break;
                    }
                default:
                    reader.skipType(tag & 7);
                    break;
                }
            }
            return message;
        };

        /**
         * Decodes a CoefRow message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof profedit.CoefRow
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {profedit.CoefRow} CoefRow
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        CoefRow.decodeDelimited = function decodeDelimited(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a CoefRow message.
         * @function verify
         * @memberof profedit.CoefRow
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        CoefRow.verify = function verify(message) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (message.bcCd != null && message.hasOwnProperty("bcCd"))
                if (!$util.isInteger(message.bcCd))
                    return "bcCd: integer expected";
            if (message.mv != null && message.hasOwnProperty("mv"))
                if (!$util.isInteger(message.mv))
                    return "mv: integer expected";
            return null;
        };

        /**
         * Creates a CoefRow message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof profedit.CoefRow
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {profedit.CoefRow} CoefRow
         */
        CoefRow.fromObject = function fromObject(object) {
            if (object instanceof $root.profedit.CoefRow)
                return object;
            let message = new $root.profedit.CoefRow();
            if (object.bcCd != null)
                message.bcCd = object.bcCd | 0;
            if (object.mv != null)
                message.mv = object.mv | 0;
            return message;
        };

        /**
         * Creates a plain object from a CoefRow message. Also converts values to other types if specified.
         * @function toObject
         * @memberof profedit.CoefRow
         * @static
         * @param {profedit.CoefRow} message CoefRow
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        CoefRow.toObject = function toObject(message, options) {
            if (!options)
                options = {};
            let object = {};
            if (options.defaults) {
                object.bcCd = 0;
                object.mv = 0;
            }
            if (message.bcCd != null && message.hasOwnProperty("bcCd"))
                object.bcCd = message.bcCd;
            if (message.mv != null && message.hasOwnProperty("mv"))
                object.mv = message.mv;
            return object;
        };

        /**
         * Converts this CoefRow to JSON.
         * @function toJSON
         * @memberof profedit.CoefRow
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        CoefRow.prototype.toJSON = function toJSON() {
            return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the default type url for CoefRow
         * @function getTypeUrl
         * @memberof profedit.CoefRow
         * @static
         * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
         * @returns {string} The default type url
         */
        CoefRow.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
            if (typeUrlPrefix === undefined) {
                typeUrlPrefix = "type.googleapis.com";
            }
            return typeUrlPrefix + "/profedit.CoefRow";
        };

        return CoefRow;
    })();

    /**
     * DType enum.
     * @name profedit.DType
     * @enum {number}
     * @property {number} VALUE=0 VALUE value
     * @property {number} INDEX=1 INDEX value
     */
    profedit.DType = (function() {
        const valuesById = {}, values = Object.create(valuesById);
        values[valuesById[0] = "VALUE"] = 0;
        values[valuesById[1] = "INDEX"] = 1;
        return values;
    })();

    profedit.SwPos = (function() {

        /**
         * Properties of a SwPos.
         * @memberof profedit
         * @interface ISwPos
         * @property {number|null} [cIdx] SwPos cIdx
         * @property {number|null} [reticleIdx] SwPos reticleIdx
         * @property {number|null} [zoom] SwPos zoom
         * @property {number|null} [distance] SwPos distance
         * @property {profedit.DType|null} [distanceFrom] SwPos distanceFrom
         */

        /**
         * Constructs a new SwPos.
         * @memberof profedit
         * @classdesc Represents a SwPos.
         * @implements ISwPos
         * @constructor
         * @param {profedit.ISwPos=} [properties] Properties to set
         */
        function SwPos(properties) {
            if (properties)
                for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null)
                        this[keys[i]] = properties[keys[i]];
        }

        /**
         * SwPos cIdx.
         * @member {number} cIdx
         * @memberof profedit.SwPos
         * @instance
         */
        SwPos.prototype.cIdx = 0;

        /**
         * SwPos reticleIdx.
         * @member {number} reticleIdx
         * @memberof profedit.SwPos
         * @instance
         */
        SwPos.prototype.reticleIdx = 0;

        /**
         * SwPos zoom.
         * @member {number} zoom
         * @memberof profedit.SwPos
         * @instance
         */
        SwPos.prototype.zoom = 0;

        /**
         * SwPos distance.
         * @member {number} distance
         * @memberof profedit.SwPos
         * @instance
         */
        SwPos.prototype.distance = 0;

        /**
         * SwPos distanceFrom.
         * @member {profedit.DType} distanceFrom
         * @memberof profedit.SwPos
         * @instance
         */
        SwPos.prototype.distanceFrom = 0;

        /**
         * Creates a new SwPos instance using the specified properties.
         * @function create
         * @memberof profedit.SwPos
         * @static
         * @param {profedit.ISwPos=} [properties] Properties to set
         * @returns {profedit.SwPos} SwPos instance
         */
        SwPos.create = function create(properties) {
            return new SwPos(properties);
        };

        /**
         * Encodes the specified SwPos message. Does not implicitly {@link profedit.SwPos.verify|verify} messages.
         * @function encode
         * @memberof profedit.SwPos
         * @static
         * @param {profedit.ISwPos} message SwPos message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        SwPos.encode = function encode(message, writer) {
            if (!writer)
                writer = $Writer.create();
            if (message.cIdx != null && Object.hasOwnProperty.call(message, "cIdx"))
                writer.uint32(/* id 1, wireType 0 =*/8).int32(message.cIdx);
            if (message.reticleIdx != null && Object.hasOwnProperty.call(message, "reticleIdx"))
                writer.uint32(/* id 2, wireType 0 =*/16).int32(message.reticleIdx);
            if (message.zoom != null && Object.hasOwnProperty.call(message, "zoom"))
                writer.uint32(/* id 3, wireType 0 =*/24).int32(message.zoom);
            if (message.distance != null && Object.hasOwnProperty.call(message, "distance"))
                writer.uint32(/* id 4, wireType 0 =*/32).int32(message.distance);
            if (message.distanceFrom != null && Object.hasOwnProperty.call(message, "distanceFrom"))
                writer.uint32(/* id 5, wireType 0 =*/40).int32(message.distanceFrom);
            return writer;
        };

        /**
         * Encodes the specified SwPos message, length delimited. Does not implicitly {@link profedit.SwPos.verify|verify} messages.
         * @function encodeDelimited
         * @memberof profedit.SwPos
         * @static
         * @param {profedit.ISwPos} message SwPos message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        SwPos.encodeDelimited = function encodeDelimited(message, writer) {
            return this.encode(message, writer).ldelim();
        };

        /**
         * Decodes a SwPos message from the specified reader or buffer.
         * @function decode
         * @memberof profedit.SwPos
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {profedit.SwPos} SwPos
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        SwPos.decode = function decode(reader, length, error) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            let end = length === undefined ? reader.len : reader.pos + length, message = new $root.profedit.SwPos();
            while (reader.pos < end) {
                let tag = reader.uint32();
                if (tag === error)
                    break;
                switch (tag >>> 3) {
                case 1: {
                        message.cIdx = reader.int32();
                        break;
                    }
                case 2: {
                        message.reticleIdx = reader.int32();
                        break;
                    }
                case 3: {
                        message.zoom = reader.int32();
                        break;
                    }
                case 4: {
                        message.distance = reader.int32();
                        break;
                    }
                case 5: {
                        message.distanceFrom = reader.int32();
                        break;
                    }
                default:
                    reader.skipType(tag & 7);
                    break;
                }
            }
            return message;
        };

        /**
         * Decodes a SwPos message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof profedit.SwPos
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {profedit.SwPos} SwPos
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        SwPos.decodeDelimited = function decodeDelimited(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a SwPos message.
         * @function verify
         * @memberof profedit.SwPos
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        SwPos.verify = function verify(message) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (message.cIdx != null && message.hasOwnProperty("cIdx"))
                if (!$util.isInteger(message.cIdx))
                    return "cIdx: integer expected";
            if (message.reticleIdx != null && message.hasOwnProperty("reticleIdx"))
                if (!$util.isInteger(message.reticleIdx))
                    return "reticleIdx: integer expected";
            if (message.zoom != null && message.hasOwnProperty("zoom"))
                if (!$util.isInteger(message.zoom))
                    return "zoom: integer expected";
            if (message.distance != null && message.hasOwnProperty("distance"))
                if (!$util.isInteger(message.distance))
                    return "distance: integer expected";
            if (message.distanceFrom != null && message.hasOwnProperty("distanceFrom"))
                switch (message.distanceFrom) {
                default:
                    return "distanceFrom: enum value expected";
                case 0:
                case 1:
                    break;
                }
            return null;
        };

        /**
         * Creates a SwPos message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof profedit.SwPos
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {profedit.SwPos} SwPos
         */
        SwPos.fromObject = function fromObject(object) {
            if (object instanceof $root.profedit.SwPos)
                return object;
            let message = new $root.profedit.SwPos();
            if (object.cIdx != null)
                message.cIdx = object.cIdx | 0;
            if (object.reticleIdx != null)
                message.reticleIdx = object.reticleIdx | 0;
            if (object.zoom != null)
                message.zoom = object.zoom | 0;
            if (object.distance != null)
                message.distance = object.distance | 0;
            switch (object.distanceFrom) {
            default:
                if (typeof object.distanceFrom === "number") {
                    message.distanceFrom = object.distanceFrom;
                    break;
                }
                break;
            case "VALUE":
            case 0:
                message.distanceFrom = 0;
                break;
            case "INDEX":
            case 1:
                message.distanceFrom = 1;
                break;
            }
            return message;
        };

        /**
         * Creates a plain object from a SwPos message. Also converts values to other types if specified.
         * @function toObject
         * @memberof profedit.SwPos
         * @static
         * @param {profedit.SwPos} message SwPos
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        SwPos.toObject = function toObject(message, options) {
            if (!options)
                options = {};
            let object = {};
            if (options.defaults) {
                object.cIdx = 0;
                object.reticleIdx = 0;
                object.zoom = 0;
                object.distance = 0;
                object.distanceFrom = options.enums === String ? "VALUE" : 0;
            }
            if (message.cIdx != null && message.hasOwnProperty("cIdx"))
                object.cIdx = message.cIdx;
            if (message.reticleIdx != null && message.hasOwnProperty("reticleIdx"))
                object.reticleIdx = message.reticleIdx;
            if (message.zoom != null && message.hasOwnProperty("zoom"))
                object.zoom = message.zoom;
            if (message.distance != null && message.hasOwnProperty("distance"))
                object.distance = message.distance;
            if (message.distanceFrom != null && message.hasOwnProperty("distanceFrom"))
                object.distanceFrom = options.enums === String ? $root.profedit.DType[message.distanceFrom] === undefined ? message.distanceFrom : $root.profedit.DType[message.distanceFrom] : message.distanceFrom;
            return object;
        };

        /**
         * Converts this SwPos to JSON.
         * @function toJSON
         * @memberof profedit.SwPos
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        SwPos.prototype.toJSON = function toJSON() {
            return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the default type url for SwPos
         * @function getTypeUrl
         * @memberof profedit.SwPos
         * @static
         * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
         * @returns {string} The default type url
         */
        SwPos.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
            if (typeUrlPrefix === undefined) {
                typeUrlPrefix = "type.googleapis.com";
            }
            return typeUrlPrefix + "/profedit.SwPos";
        };

        return SwPos;
    })();

    /**
     * GType enum.
     * @name profedit.GType
     * @enum {number}
     * @property {number} G1=0 G1 value
     * @property {number} G7=1 G7 value
     * @property {number} CUSTOM=2 CUSTOM value
     */
    profedit.GType = (function() {
        const valuesById = {}, values = Object.create(valuesById);
        values[valuesById[0] = "G1"] = 0;
        values[valuesById[1] = "G7"] = 1;
        values[valuesById[2] = "CUSTOM"] = 2;
        return values;
    })();

    /**
     * TwistDir enum.
     * @name profedit.TwistDir
     * @enum {number}
     * @property {number} RIGHT=0 RIGHT value
     * @property {number} LEFT=1 LEFT value
     */
    profedit.TwistDir = (function() {
        const valuesById = {}, values = Object.create(valuesById);
        values[valuesById[0] = "RIGHT"] = 0;
        values[valuesById[1] = "LEFT"] = 1;
        return values;
    })();

    profedit.Profile = (function() {

        /**
         * Properties of a Profile.
         * @memberof profedit
         * @interface IProfile
         * @property {string|null} [profileName] Profile profileName
         * @property {string|null} [cartridgeName] Profile cartridgeName
         * @property {string|null} [bulletName] Profile bulletName
         * @property {string|null} [shortNameTop] Profile shortNameTop
         * @property {string|null} [shortNameBot] Profile shortNameBot
         * @property {string|null} [userNote] Profile userNote
         * @property {number|null} [zeroX] Profile zeroX
         * @property {number|null} [zeroY] Profile zeroY
         * @property {number|null} [scHeight] Profile scHeight
         * @property {number|null} [rTwist] Profile rTwist
         * @property {number|null} [cMuzzleVelocity] Profile cMuzzleVelocity
         * @property {number|null} [cZeroTemperature] Profile cZeroTemperature
         * @property {number|null} [cTCoeff] Profile cTCoeff
         * @property {number|null} [cZeroDistanceIdx] Profile cZeroDistanceIdx
         * @property {number|null} [cZeroAirTemperature] Profile cZeroAirTemperature
         * @property {number|null} [cZeroAirPressure] Profile cZeroAirPressure
         * @property {number|null} [cZeroAirHumidity] Profile cZeroAirHumidity
         * @property {number|null} [cZeroWPitch] Profile cZeroWPitch
         * @property {number|null} [cZeroPTemperature] Profile cZeroPTemperature
         * @property {number|null} [bDiameter] Profile bDiameter
         * @property {number|null} [bWeight] Profile bWeight
         * @property {number|null} [bLength] Profile bLength
         * @property {profedit.TwistDir|null} [twistDir] Profile twistDir
         * @property {profedit.GType|null} [bcType] Profile bcType
         * @property {Array.<profedit.ISwPos>|null} [switches] Profile switches
         * @property {Array.<number>|null} [distances] Profile distances
         * @property {Array.<profedit.ICoefRow>|null} [coefRows] Profile coefRows
         * @property {string|null} [caliber] Profile caliber
         * @property {string|null} [deviceUuid] Profile deviceUuid
         */

        /**
         * Constructs a new Profile.
         * @memberof profedit
         * @classdesc Represents a Profile.
         * @implements IProfile
         * @constructor
         * @param {profedit.IProfile=} [properties] Properties to set
         */
        function Profile(properties) {
            this.switches = [];
            this.distances = [];
            this.coefRows = [];
            if (properties)
                for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null)
                        this[keys[i]] = properties[keys[i]];
        }

        /**
         * Profile profileName.
         * @member {string} profileName
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.profileName = "";

        /**
         * Profile cartridgeName.
         * @member {string} cartridgeName
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cartridgeName = "";

        /**
         * Profile bulletName.
         * @member {string} bulletName
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.bulletName = "";

        /**
         * Profile shortNameTop.
         * @member {string} shortNameTop
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.shortNameTop = "";

        /**
         * Profile shortNameBot.
         * @member {string} shortNameBot
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.shortNameBot = "";

        /**
         * Profile userNote.
         * @member {string} userNote
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.userNote = "";

        /**
         * Profile zeroX.
         * @member {number} zeroX
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.zeroX = 0;

        /**
         * Profile zeroY.
         * @member {number} zeroY
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.zeroY = 0;

        /**
         * Profile scHeight.
         * @member {number} scHeight
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.scHeight = 0;

        /**
         * Profile rTwist.
         * @member {number} rTwist
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.rTwist = 0;

        /**
         * Profile cMuzzleVelocity.
         * @member {number} cMuzzleVelocity
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cMuzzleVelocity = 0;

        /**
         * Profile cZeroTemperature.
         * @member {number} cZeroTemperature
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cZeroTemperature = 0;

        /**
         * Profile cTCoeff.
         * @member {number} cTCoeff
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cTCoeff = 0;

        /**
         * Profile cZeroDistanceIdx.
         * @member {number} cZeroDistanceIdx
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cZeroDistanceIdx = 0;

        /**
         * Profile cZeroAirTemperature.
         * @member {number} cZeroAirTemperature
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cZeroAirTemperature = 0;

        /**
         * Profile cZeroAirPressure.
         * @member {number} cZeroAirPressure
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cZeroAirPressure = 0;

        /**
         * Profile cZeroAirHumidity.
         * @member {number} cZeroAirHumidity
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cZeroAirHumidity = 0;

        /**
         * Profile cZeroWPitch.
         * @member {number} cZeroWPitch
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cZeroWPitch = 0;

        /**
         * Profile cZeroPTemperature.
         * @member {number} cZeroPTemperature
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.cZeroPTemperature = 0;

        /**
         * Profile bDiameter.
         * @member {number} bDiameter
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.bDiameter = 0;

        /**
         * Profile bWeight.
         * @member {number} bWeight
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.bWeight = 0;

        /**
         * Profile bLength.
         * @member {number} bLength
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.bLength = 0;

        /**
         * Profile twistDir.
         * @member {profedit.TwistDir} twistDir
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.twistDir = 0;

        /**
         * Profile bcType.
         * @member {profedit.GType} bcType
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.bcType = 0;

        /**
         * Profile switches.
         * @member {Array.<profedit.ISwPos>} switches
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.switches = $util.emptyArray;

        /**
         * Profile distances.
         * @member {Array.<number>} distances
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.distances = $util.emptyArray;

        /**
         * Profile coefRows.
         * @member {Array.<profedit.ICoefRow>} coefRows
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.coefRows = $util.emptyArray;

        /**
         * Profile caliber.
         * @member {string} caliber
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.caliber = "";

        /**
         * Profile deviceUuid.
         * @member {string} deviceUuid
         * @memberof profedit.Profile
         * @instance
         */
        Profile.prototype.deviceUuid = "";

        /**
         * Creates a new Profile instance using the specified properties.
         * @function create
         * @memberof profedit.Profile
         * @static
         * @param {profedit.IProfile=} [properties] Properties to set
         * @returns {profedit.Profile} Profile instance
         */
        Profile.create = function create(properties) {
            return new Profile(properties);
        };

        /**
         * Encodes the specified Profile message. Does not implicitly {@link profedit.Profile.verify|verify} messages.
         * @function encode
         * @memberof profedit.Profile
         * @static
         * @param {profedit.IProfile} message Profile message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        Profile.encode = function encode(message, writer) {
            if (!writer)
                writer = $Writer.create();
            if (message.profileName != null && Object.hasOwnProperty.call(message, "profileName"))
                writer.uint32(/* id 1, wireType 2 =*/10).string(message.profileName);
            if (message.cartridgeName != null && Object.hasOwnProperty.call(message, "cartridgeName"))
                writer.uint32(/* id 2, wireType 2 =*/18).string(message.cartridgeName);
            if (message.bulletName != null && Object.hasOwnProperty.call(message, "bulletName"))
                writer.uint32(/* id 3, wireType 2 =*/26).string(message.bulletName);
            if (message.shortNameTop != null && Object.hasOwnProperty.call(message, "shortNameTop"))
                writer.uint32(/* id 4, wireType 2 =*/34).string(message.shortNameTop);
            if (message.shortNameBot != null && Object.hasOwnProperty.call(message, "shortNameBot"))
                writer.uint32(/* id 5, wireType 2 =*/42).string(message.shortNameBot);
            if (message.userNote != null && Object.hasOwnProperty.call(message, "userNote"))
                writer.uint32(/* id 6, wireType 2 =*/50).string(message.userNote);
            if (message.zeroX != null && Object.hasOwnProperty.call(message, "zeroX"))
                writer.uint32(/* id 7, wireType 0 =*/56).int32(message.zeroX);
            if (message.zeroY != null && Object.hasOwnProperty.call(message, "zeroY"))
                writer.uint32(/* id 8, wireType 0 =*/64).int32(message.zeroY);
            if (message.scHeight != null && Object.hasOwnProperty.call(message, "scHeight"))
                writer.uint32(/* id 9, wireType 0 =*/72).int32(message.scHeight);
            if (message.rTwist != null && Object.hasOwnProperty.call(message, "rTwist"))
                writer.uint32(/* id 10, wireType 0 =*/80).int32(message.rTwist);
            if (message.cMuzzleVelocity != null && Object.hasOwnProperty.call(message, "cMuzzleVelocity"))
                writer.uint32(/* id 11, wireType 0 =*/88).int32(message.cMuzzleVelocity);
            if (message.cZeroTemperature != null && Object.hasOwnProperty.call(message, "cZeroTemperature"))
                writer.uint32(/* id 12, wireType 0 =*/96).int32(message.cZeroTemperature);
            if (message.cTCoeff != null && Object.hasOwnProperty.call(message, "cTCoeff"))
                writer.uint32(/* id 13, wireType 0 =*/104).int32(message.cTCoeff);
            if (message.cZeroDistanceIdx != null && Object.hasOwnProperty.call(message, "cZeroDistanceIdx"))
                writer.uint32(/* id 14, wireType 0 =*/112).int32(message.cZeroDistanceIdx);
            if (message.cZeroAirTemperature != null && Object.hasOwnProperty.call(message, "cZeroAirTemperature"))
                writer.uint32(/* id 15, wireType 0 =*/120).int32(message.cZeroAirTemperature);
            if (message.cZeroAirPressure != null && Object.hasOwnProperty.call(message, "cZeroAirPressure"))
                writer.uint32(/* id 16, wireType 0 =*/128).int32(message.cZeroAirPressure);
            if (message.cZeroAirHumidity != null && Object.hasOwnProperty.call(message, "cZeroAirHumidity"))
                writer.uint32(/* id 17, wireType 0 =*/136).int32(message.cZeroAirHumidity);
            if (message.cZeroWPitch != null && Object.hasOwnProperty.call(message, "cZeroWPitch"))
                writer.uint32(/* id 18, wireType 0 =*/144).int32(message.cZeroWPitch);
            if (message.cZeroPTemperature != null && Object.hasOwnProperty.call(message, "cZeroPTemperature"))
                writer.uint32(/* id 19, wireType 0 =*/152).int32(message.cZeroPTemperature);
            if (message.bDiameter != null && Object.hasOwnProperty.call(message, "bDiameter"))
                writer.uint32(/* id 20, wireType 0 =*/160).int32(message.bDiameter);
            if (message.bWeight != null && Object.hasOwnProperty.call(message, "bWeight"))
                writer.uint32(/* id 21, wireType 0 =*/168).int32(message.bWeight);
            if (message.bLength != null && Object.hasOwnProperty.call(message, "bLength"))
                writer.uint32(/* id 22, wireType 0 =*/176).int32(message.bLength);
            if (message.twistDir != null && Object.hasOwnProperty.call(message, "twistDir"))
                writer.uint32(/* id 23, wireType 0 =*/184).int32(message.twistDir);
            if (message.bcType != null && Object.hasOwnProperty.call(message, "bcType"))
                writer.uint32(/* id 24, wireType 0 =*/192).int32(message.bcType);
            if (message.switches != null && message.switches.length)
                for (let i = 0; i < message.switches.length; ++i)
                    $root.profedit.SwPos.encode(message.switches[i], writer.uint32(/* id 25, wireType 2 =*/202).fork()).ldelim();
            if (message.distances != null && message.distances.length) {
                writer.uint32(/* id 26, wireType 2 =*/210).fork();
                for (let i = 0; i < message.distances.length; ++i)
                    writer.int32(message.distances[i]);
                writer.ldelim();
            }
            if (message.coefRows != null && message.coefRows.length)
                for (let i = 0; i < message.coefRows.length; ++i)
                    $root.profedit.CoefRow.encode(message.coefRows[i], writer.uint32(/* id 27, wireType 2 =*/218).fork()).ldelim();
            if (message.caliber != null && Object.hasOwnProperty.call(message, "caliber"))
                writer.uint32(/* id 28, wireType 2 =*/226).string(message.caliber);
            if (message.deviceUuid != null && Object.hasOwnProperty.call(message, "deviceUuid"))
                writer.uint32(/* id 29, wireType 2 =*/234).string(message.deviceUuid);
            return writer;
        };

        /**
         * Encodes the specified Profile message, length delimited. Does not implicitly {@link profedit.Profile.verify|verify} messages.
         * @function encodeDelimited
         * @memberof profedit.Profile
         * @static
         * @param {profedit.IProfile} message Profile message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        Profile.encodeDelimited = function encodeDelimited(message, writer) {
            return this.encode(message, writer).ldelim();
        };

        /**
         * Decodes a Profile message from the specified reader or buffer.
         * @function decode
         * @memberof profedit.Profile
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {profedit.Profile} Profile
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        Profile.decode = function decode(reader, length, error) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            let end = length === undefined ? reader.len : reader.pos + length, message = new $root.profedit.Profile();
            while (reader.pos < end) {
                let tag = reader.uint32();
                if (tag === error)
                    break;
                switch (tag >>> 3) {
                case 1: {
                        message.profileName = reader.string();
                        break;
                    }
                case 2: {
                        message.cartridgeName = reader.string();
                        break;
                    }
                case 3: {
                        message.bulletName = reader.string();
                        break;
                    }
                case 4: {
                        message.shortNameTop = reader.string();
                        break;
                    }
                case 5: {
                        message.shortNameBot = reader.string();
                        break;
                    }
                case 6: {
                        message.userNote = reader.string();
                        break;
                    }
                case 7: {
                        message.zeroX = reader.int32();
                        break;
                    }
                case 8: {
                        message.zeroY = reader.int32();
                        break;
                    }
                case 9: {
                        message.scHeight = reader.int32();
                        break;
                    }
                case 10: {
                        message.rTwist = reader.int32();
                        break;
                    }
                case 11: {
                        message.cMuzzleVelocity = reader.int32();
                        break;
                    }
                case 12: {
                        message.cZeroTemperature = reader.int32();
                        break;
                    }
                case 13: {
                        message.cTCoeff = reader.int32();
                        break;
                    }
                case 14: {
                        message.cZeroDistanceIdx = reader.int32();
                        break;
                    }
                case 15: {
                        message.cZeroAirTemperature = reader.int32();
                        break;
                    }
                case 16: {
                        message.cZeroAirPressure = reader.int32();
                        break;
                    }
                case 17: {
                        message.cZeroAirHumidity = reader.int32();
                        break;
                    }
                case 18: {
                        message.cZeroWPitch = reader.int32();
                        break;
                    }
                case 19: {
                        message.cZeroPTemperature = reader.int32();
                        break;
                    }
                case 20: {
                        message.bDiameter = reader.int32();
                        break;
                    }
                case 21: {
                        message.bWeight = reader.int32();
                        break;
                    }
                case 22: {
                        message.bLength = reader.int32();
                        break;
                    }
                case 23: {
                        message.twistDir = reader.int32();
                        break;
                    }
                case 24: {
                        message.bcType = reader.int32();
                        break;
                    }
                case 25: {
                        if (!(message.switches && message.switches.length))
                            message.switches = [];
                        message.switches.push($root.profedit.SwPos.decode(reader, reader.uint32()));
                        break;
                    }
                case 26: {
                        if (!(message.distances && message.distances.length))
                            message.distances = [];
                        if ((tag & 7) === 2) {
                            let end2 = reader.uint32() + reader.pos;
                            while (reader.pos < end2)
                                message.distances.push(reader.int32());
                        } else
                            message.distances.push(reader.int32());
                        break;
                    }
                case 27: {
                        if (!(message.coefRows && message.coefRows.length))
                            message.coefRows = [];
                        message.coefRows.push($root.profedit.CoefRow.decode(reader, reader.uint32()));
                        break;
                    }
                case 28: {
                        message.caliber = reader.string();
                        break;
                    }
                case 29: {
                        message.deviceUuid = reader.string();
                        break;
                    }
                default:
                    reader.skipType(tag & 7);
                    break;
                }
            }
            return message;
        };

        /**
         * Decodes a Profile message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof profedit.Profile
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {profedit.Profile} Profile
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        Profile.decodeDelimited = function decodeDelimited(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a Profile message.
         * @function verify
         * @memberof profedit.Profile
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        Profile.verify = function verify(message) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (message.profileName != null && message.hasOwnProperty("profileName"))
                if (!$util.isString(message.profileName))
                    return "profileName: string expected";
            if (message.cartridgeName != null && message.hasOwnProperty("cartridgeName"))
                if (!$util.isString(message.cartridgeName))
                    return "cartridgeName: string expected";
            if (message.bulletName != null && message.hasOwnProperty("bulletName"))
                if (!$util.isString(message.bulletName))
                    return "bulletName: string expected";
            if (message.shortNameTop != null && message.hasOwnProperty("shortNameTop"))
                if (!$util.isString(message.shortNameTop))
                    return "shortNameTop: string expected";
            if (message.shortNameBot != null && message.hasOwnProperty("shortNameBot"))
                if (!$util.isString(message.shortNameBot))
                    return "shortNameBot: string expected";
            if (message.userNote != null && message.hasOwnProperty("userNote"))
                if (!$util.isString(message.userNote))
                    return "userNote: string expected";
            if (message.zeroX != null && message.hasOwnProperty("zeroX"))
                if (!$util.isInteger(message.zeroX))
                    return "zeroX: integer expected";
            if (message.zeroY != null && message.hasOwnProperty("zeroY"))
                if (!$util.isInteger(message.zeroY))
                    return "zeroY: integer expected";
            if (message.scHeight != null && message.hasOwnProperty("scHeight"))
                if (!$util.isInteger(message.scHeight))
                    return "scHeight: integer expected";
            if (message.rTwist != null && message.hasOwnProperty("rTwist"))
                if (!$util.isInteger(message.rTwist))
                    return "rTwist: integer expected";
            if (message.cMuzzleVelocity != null && message.hasOwnProperty("cMuzzleVelocity"))
                if (!$util.isInteger(message.cMuzzleVelocity))
                    return "cMuzzleVelocity: integer expected";
            if (message.cZeroTemperature != null && message.hasOwnProperty("cZeroTemperature"))
                if (!$util.isInteger(message.cZeroTemperature))
                    return "cZeroTemperature: integer expected";
            if (message.cTCoeff != null && message.hasOwnProperty("cTCoeff"))
                if (!$util.isInteger(message.cTCoeff))
                    return "cTCoeff: integer expected";
            if (message.cZeroDistanceIdx != null && message.hasOwnProperty("cZeroDistanceIdx"))
                if (!$util.isInteger(message.cZeroDistanceIdx))
                    return "cZeroDistanceIdx: integer expected";
            if (message.cZeroAirTemperature != null && message.hasOwnProperty("cZeroAirTemperature"))
                if (!$util.isInteger(message.cZeroAirTemperature))
                    return "cZeroAirTemperature: integer expected";
            if (message.cZeroAirPressure != null && message.hasOwnProperty("cZeroAirPressure"))
                if (!$util.isInteger(message.cZeroAirPressure))
                    return "cZeroAirPressure: integer expected";
            if (message.cZeroAirHumidity != null && message.hasOwnProperty("cZeroAirHumidity"))
                if (!$util.isInteger(message.cZeroAirHumidity))
                    return "cZeroAirHumidity: integer expected";
            if (message.cZeroWPitch != null && message.hasOwnProperty("cZeroWPitch"))
                if (!$util.isInteger(message.cZeroWPitch))
                    return "cZeroWPitch: integer expected";
            if (message.cZeroPTemperature != null && message.hasOwnProperty("cZeroPTemperature"))
                if (!$util.isInteger(message.cZeroPTemperature))
                    return "cZeroPTemperature: integer expected";
            if (message.bDiameter != null && message.hasOwnProperty("bDiameter"))
                if (!$util.isInteger(message.bDiameter))
                    return "bDiameter: integer expected";
            if (message.bWeight != null && message.hasOwnProperty("bWeight"))
                if (!$util.isInteger(message.bWeight))
                    return "bWeight: integer expected";
            if (message.bLength != null && message.hasOwnProperty("bLength"))
                if (!$util.isInteger(message.bLength))
                    return "bLength: integer expected";
            if (message.twistDir != null && message.hasOwnProperty("twistDir"))
                switch (message.twistDir) {
                default:
                    return "twistDir: enum value expected";
                case 0:
                case 1:
                    break;
                }
            if (message.bcType != null && message.hasOwnProperty("bcType"))
                switch (message.bcType) {
                default:
                    return "bcType: enum value expected";
                case 0:
                case 1:
                case 2:
                    break;
                }
            if (message.switches != null && message.hasOwnProperty("switches")) {
                if (!Array.isArray(message.switches))
                    return "switches: array expected";
                for (let i = 0; i < message.switches.length; ++i) {
                    let error = $root.profedit.SwPos.verify(message.switches[i]);
                    if (error)
                        return "switches." + error;
                }
            }
            if (message.distances != null && message.hasOwnProperty("distances")) {
                if (!Array.isArray(message.distances))
                    return "distances: array expected";
                for (let i = 0; i < message.distances.length; ++i)
                    if (!$util.isInteger(message.distances[i]))
                        return "distances: integer[] expected";
            }
            if (message.coefRows != null && message.hasOwnProperty("coefRows")) {
                if (!Array.isArray(message.coefRows))
                    return "coefRows: array expected";
                for (let i = 0; i < message.coefRows.length; ++i) {
                    let error = $root.profedit.CoefRow.verify(message.coefRows[i]);
                    if (error)
                        return "coefRows." + error;
                }
            }
            if (message.caliber != null && message.hasOwnProperty("caliber"))
                if (!$util.isString(message.caliber))
                    return "caliber: string expected";
            if (message.deviceUuid != null && message.hasOwnProperty("deviceUuid"))
                if (!$util.isString(message.deviceUuid))
                    return "deviceUuid: string expected";
            return null;
        };

        /**
         * Creates a Profile message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof profedit.Profile
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {profedit.Profile} Profile
         */
        Profile.fromObject = function fromObject(object) {
            if (object instanceof $root.profedit.Profile)
                return object;
            let message = new $root.profedit.Profile();
            if (object.profileName != null)
                message.profileName = String(object.profileName);
            if (object.cartridgeName != null)
                message.cartridgeName = String(object.cartridgeName);
            if (object.bulletName != null)
                message.bulletName = String(object.bulletName);
            if (object.shortNameTop != null)
                message.shortNameTop = String(object.shortNameTop);
            if (object.shortNameBot != null)
                message.shortNameBot = String(object.shortNameBot);
            if (object.userNote != null)
                message.userNote = String(object.userNote);
            if (object.zeroX != null)
                message.zeroX = object.zeroX | 0;
            if (object.zeroY != null)
                message.zeroY = object.zeroY | 0;
            if (object.scHeight != null)
                message.scHeight = object.scHeight | 0;
            if (object.rTwist != null)
                message.rTwist = object.rTwist | 0;
            if (object.cMuzzleVelocity != null)
                message.cMuzzleVelocity = object.cMuzzleVelocity | 0;
            if (object.cZeroTemperature != null)
                message.cZeroTemperature = object.cZeroTemperature | 0;
            if (object.cTCoeff != null)
                message.cTCoeff = object.cTCoeff | 0;
            if (object.cZeroDistanceIdx != null)
                message.cZeroDistanceIdx = object.cZeroDistanceIdx | 0;
            if (object.cZeroAirTemperature != null)
                message.cZeroAirTemperature = object.cZeroAirTemperature | 0;
            if (object.cZeroAirPressure != null)
                message.cZeroAirPressure = object.cZeroAirPressure | 0;
            if (object.cZeroAirHumidity != null)
                message.cZeroAirHumidity = object.cZeroAirHumidity | 0;
            if (object.cZeroWPitch != null)
                message.cZeroWPitch = object.cZeroWPitch | 0;
            if (object.cZeroPTemperature != null)
                message.cZeroPTemperature = object.cZeroPTemperature | 0;
            if (object.bDiameter != null)
                message.bDiameter = object.bDiameter | 0;
            if (object.bWeight != null)
                message.bWeight = object.bWeight | 0;
            if (object.bLength != null)
                message.bLength = object.bLength | 0;
            switch (object.twistDir) {
            default:
                if (typeof object.twistDir === "number") {
                    message.twistDir = object.twistDir;
                    break;
                }
                break;
            case "RIGHT":
            case 0:
                message.twistDir = 0;
                break;
            case "LEFT":
            case 1:
                message.twistDir = 1;
                break;
            }
            switch (object.bcType) {
            default:
                if (typeof object.bcType === "number") {
                    message.bcType = object.bcType;
                    break;
                }
                break;
            case "G1":
            case 0:
                message.bcType = 0;
                break;
            case "G7":
            case 1:
                message.bcType = 1;
                break;
            case "CUSTOM":
            case 2:
                message.bcType = 2;
                break;
            }
            if (object.switches) {
                if (!Array.isArray(object.switches))
                    throw TypeError(".profedit.Profile.switches: array expected");
                message.switches = [];
                for (let i = 0; i < object.switches.length; ++i) {
                    if (typeof object.switches[i] !== "object")
                        throw TypeError(".profedit.Profile.switches: object expected");
                    message.switches[i] = $root.profedit.SwPos.fromObject(object.switches[i]);
                }
            }
            if (object.distances) {
                if (!Array.isArray(object.distances))
                    throw TypeError(".profedit.Profile.distances: array expected");
                message.distances = [];
                for (let i = 0; i < object.distances.length; ++i)
                    message.distances[i] = object.distances[i] | 0;
            }
            if (object.coefRows) {
                if (!Array.isArray(object.coefRows))
                    throw TypeError(".profedit.Profile.coefRows: array expected");
                message.coefRows = [];
                for (let i = 0; i < object.coefRows.length; ++i) {
                    if (typeof object.coefRows[i] !== "object")
                        throw TypeError(".profedit.Profile.coefRows: object expected");
                    message.coefRows[i] = $root.profedit.CoefRow.fromObject(object.coefRows[i]);
                }
            }
            if (object.caliber != null)
                message.caliber = String(object.caliber);
            if (object.deviceUuid != null)
                message.deviceUuid = String(object.deviceUuid);
            return message;
        };

        /**
         * Creates a plain object from a Profile message. Also converts values to other types if specified.
         * @function toObject
         * @memberof profedit.Profile
         * @static
         * @param {profedit.Profile} message Profile
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        Profile.toObject = function toObject(message, options) {
            if (!options)
                options = {};
            let object = {};
            if (options.arrays || options.defaults) {
                object.switches = [];
                object.distances = [];
                object.coefRows = [];
            }
            if (options.defaults) {
                object.profileName = "";
                object.cartridgeName = "";
                object.bulletName = "";
                object.shortNameTop = "";
                object.shortNameBot = "";
                object.userNote = "";
                object.zeroX = 0;
                object.zeroY = 0;
                object.scHeight = 0;
                object.rTwist = 0;
                object.cMuzzleVelocity = 0;
                object.cZeroTemperature = 0;
                object.cTCoeff = 0;
                object.cZeroDistanceIdx = 0;
                object.cZeroAirTemperature = 0;
                object.cZeroAirPressure = 0;
                object.cZeroAirHumidity = 0;
                object.cZeroWPitch = 0;
                object.cZeroPTemperature = 0;
                object.bDiameter = 0;
                object.bWeight = 0;
                object.bLength = 0;
                object.twistDir = options.enums === String ? "RIGHT" : 0;
                object.bcType = options.enums === String ? "G1" : 0;
                object.caliber = "";
                object.deviceUuid = "";
            }
            if (message.profileName != null && message.hasOwnProperty("profileName"))
                object.profileName = message.profileName;
            if (message.cartridgeName != null && message.hasOwnProperty("cartridgeName"))
                object.cartridgeName = message.cartridgeName;
            if (message.bulletName != null && message.hasOwnProperty("bulletName"))
                object.bulletName = message.bulletName;
            if (message.shortNameTop != null && message.hasOwnProperty("shortNameTop"))
                object.shortNameTop = message.shortNameTop;
            if (message.shortNameBot != null && message.hasOwnProperty("shortNameBot"))
                object.shortNameBot = message.shortNameBot;
            if (message.userNote != null && message.hasOwnProperty("userNote"))
                object.userNote = message.userNote;
            if (message.zeroX != null && message.hasOwnProperty("zeroX"))
                object.zeroX = message.zeroX;
            if (message.zeroY != null && message.hasOwnProperty("zeroY"))
                object.zeroY = message.zeroY;
            if (message.scHeight != null && message.hasOwnProperty("scHeight"))
                object.scHeight = message.scHeight;
            if (message.rTwist != null && message.hasOwnProperty("rTwist"))
                object.rTwist = message.rTwist;
            if (message.cMuzzleVelocity != null && message.hasOwnProperty("cMuzzleVelocity"))
                object.cMuzzleVelocity = message.cMuzzleVelocity;
            if (message.cZeroTemperature != null && message.hasOwnProperty("cZeroTemperature"))
                object.cZeroTemperature = message.cZeroTemperature;
            if (message.cTCoeff != null && message.hasOwnProperty("cTCoeff"))
                object.cTCoeff = message.cTCoeff;
            if (message.cZeroDistanceIdx != null && message.hasOwnProperty("cZeroDistanceIdx"))
                object.cZeroDistanceIdx = message.cZeroDistanceIdx;
            if (message.cZeroAirTemperature != null && message.hasOwnProperty("cZeroAirTemperature"))
                object.cZeroAirTemperature = message.cZeroAirTemperature;
            if (message.cZeroAirPressure != null && message.hasOwnProperty("cZeroAirPressure"))
                object.cZeroAirPressure = message.cZeroAirPressure;
            if (message.cZeroAirHumidity != null && message.hasOwnProperty("cZeroAirHumidity"))
                object.cZeroAirHumidity = message.cZeroAirHumidity;
            if (message.cZeroWPitch != null && message.hasOwnProperty("cZeroWPitch"))
                object.cZeroWPitch = message.cZeroWPitch;
            if (message.cZeroPTemperature != null && message.hasOwnProperty("cZeroPTemperature"))
                object.cZeroPTemperature = message.cZeroPTemperature;
            if (message.bDiameter != null && message.hasOwnProperty("bDiameter"))
                object.bDiameter = message.bDiameter;
            if (message.bWeight != null && message.hasOwnProperty("bWeight"))
                object.bWeight = message.bWeight;
            if (message.bLength != null && message.hasOwnProperty("bLength"))
                object.bLength = message.bLength;
            if (message.twistDir != null && message.hasOwnProperty("twistDir"))
                object.twistDir = options.enums === String ? $root.profedit.TwistDir[message.twistDir] === undefined ? message.twistDir : $root.profedit.TwistDir[message.twistDir] : message.twistDir;
            if (message.bcType != null && message.hasOwnProperty("bcType"))
                object.bcType = options.enums === String ? $root.profedit.GType[message.bcType] === undefined ? message.bcType : $root.profedit.GType[message.bcType] : message.bcType;
            if (message.switches && message.switches.length) {
                object.switches = [];
                for (let j = 0; j < message.switches.length; ++j)
                    object.switches[j] = $root.profedit.SwPos.toObject(message.switches[j], options);
            }
            if (message.distances && message.distances.length) {
                object.distances = [];
                for (let j = 0; j < message.distances.length; ++j)
                    object.distances[j] = message.distances[j];
            }
            if (message.coefRows && message.coefRows.length) {
                object.coefRows = [];
                for (let j = 0; j < message.coefRows.length; ++j)
                    object.coefRows[j] = $root.profedit.CoefRow.toObject(message.coefRows[j], options);
            }
            if (message.caliber != null && message.hasOwnProperty("caliber"))
                object.caliber = message.caliber;
            if (message.deviceUuid != null && message.hasOwnProperty("deviceUuid"))
                object.deviceUuid = message.deviceUuid;
            return object;
        };

        /**
         * Converts this Profile to JSON.
         * @function toJSON
         * @memberof profedit.Profile
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        Profile.prototype.toJSON = function toJSON() {
            return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the default type url for Profile
         * @function getTypeUrl
         * @memberof profedit.Profile
         * @static
         * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
         * @returns {string} The default type url
         */
        Profile.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
            if (typeUrlPrefix === undefined) {
                typeUrlPrefix = "type.googleapis.com";
            }
            return typeUrlPrefix + "/profedit.Profile";
        };

        return Profile;
    })();

    return profedit;
})();

export { $root as default };

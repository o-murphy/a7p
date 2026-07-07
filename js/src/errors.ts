export class A7pError extends Error {
    public readonly type: string;
    public readonly statusCode?: number;

    constructor(message: string, type: string, statusCode?: number) {
        super(message);
        this.type = type;
        this.statusCode = statusCode;
        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export class ValidationError extends A7pError {
    public readonly errors: string[];

    constructor(errors: string[], statusCode: number = 400) {
        super("Validation failed", "ValidationError", statusCode);
        this.errors = errors;
        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export class InvalidBcTypeError extends ValidationError {
    public readonly bcType: any;

    constructor(bcType: any, errors: string[] = [], statusCode: number = 400) {
        super(errors, statusCode); // Passing the errors to ValidationError
        this.bcType = bcType;
        this.message = `Invalid bcType: ${bcType}`;
        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export class EncodeError extends A7pError {
    public readonly details: string;

    constructor(details: string) {
        super(`Encoding failed: ${details}`, "EncodeError");
        this.details = details;
        this.message = `Encoding failed: ${details}`; // Ensure message is set
        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export class DecodeError extends A7pError {
    public readonly details: string;

    constructor(details: string, statusCode: number = 400) {
        super(`Decoding failed: ${details}`, "DecodeError", statusCode); // Set type and message
        this.details = details;
        this.message = `Decoding failed: ${details}`; // Ensure message is set
        Object.setPrototypeOf(this, new.target.prototype);
    }
}

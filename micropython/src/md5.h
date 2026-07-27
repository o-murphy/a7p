/*
 * Vendored verbatim from
 * https://openwall.info/wiki/people/solar/software/public-domain-source-code/md5
 * (fetched 2026-07-27) -- public domain, no external dependencies beyond
 * <string.h>. Used so a7p.py's load()/dump() md5 checksum works regardless
 * of whether the target firmware's own MICROPY_PY_SSL/MICROPY_PY_HASHLIB_MD5
 * are enabled (see README.md's "Firmware dependency: hashlib.md5" section
 * for the problem this replaces). Exposed to Python as _a7p._md5() in
 * a7p_mp.c/a7p_mod.c, not as a hashlib-compatible object -- a7p.py only
 * ever needs a single one-shot digest of an in-memory buffer.
 */

/*
 * This is an OpenSSL-compatible implementation of the RSA Data Security, Inc.
 * MD5 Message-Digest Algorithm (RFC 1321).
 *
 * Homepage:
 * http://openwall.info/wiki/people/solar/software/public-domain-source-code/md5
 *
 * Author:
 * Alexander Peslyak, better known as Solar Designer <solar at openwall.com>
 *
 * This software was written by Alexander Peslyak in 2001.  No copyright is
 * claimed, and the software is hereby placed in the public domain.
 * In case this attempt to disclaim copyright and place the software in the
 * public domain is deemed null and void, then the software is
 * Copyright (c) 2001 Alexander Peslyak and it is hereby released to the
 * general public under the following terms:
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 *
 * There's ABSOLUTELY NO WARRANTY, express or implied.
 *
 * See md5.c for more information.
 */

#ifdef HAVE_OPENSSL
#include <openssl/md5.h>
#elif !defined(_MD5_H)
#define _MD5_H

/* Any 32-bit or wider unsigned integer data type will do */
typedef unsigned int MD5_u32plus;

typedef struct {
	MD5_u32plus lo, hi;
	MD5_u32plus a, b, c, d;
	unsigned char buffer[64];
	MD5_u32plus block[16];
} MD5_CTX;

extern void MD5_Init(MD5_CTX *ctx);
extern void MD5_Update(MD5_CTX *ctx, const void *data, unsigned long size);
extern void MD5_Final(unsigned char *result, MD5_CTX *ctx);

#endif

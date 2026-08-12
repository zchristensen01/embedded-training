# mem_primitives — variants

v1  strlen, strcpy, strcmp. Byte at a time. Get the return values right.
v2  memset, memcpy. Byte at a time.
v3  memmove. Both overlap directions.
v4  strncpy and strncat, with the terminator gotchas.
v5  atoi with sign and saturating overflow, then itoa with no sprintf.
v6  Word-at-a-time memcpy: copy the unaligned head byte-wise, the body word-wise, the tail
    byte-wise. Must stay correct on an alignment-strict target.
v7  Safe variants: memcpy_s-style with a destination size parameter. Discuss in NOTES why the
    standard ones are the way they are.

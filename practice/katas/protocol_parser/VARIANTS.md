# protocol_parser — variants

v1  Byte at a time through `P_SYNC → P_LEN → P_PAYLOAD → P_CRC`, with `frames_ok`,
    `frames_bad` and `bytes_dropped` counters. Never blocks, never allocates.
v2  Table-driven CRC-8 (a 256-entry `static const` table) plus byte stuffing, so the sync byte
    can appear in a payload. Define what happens when the escape byte itself appears in data —
    that's where a hand-rolled scheme usually breaks.
v3  Timeout: abandon a partial frame when the remaining bytes never arrive. Needs a tick or
    timestamp input, which changes the API — add it without making the common path costlier.
v4  Resynchronisation: after a truncated or corrupt frame, the very next valid frame must still
    be accepted. Test the case where a sync byte lands inside a discarded payload.
v5  Zero-copy: parse in place out of a ring buffer and hand the caller a pointer plus a length
    instead of a copy. State exactly how long that pointer stays valid.
v6  CRC-16-CCITT instead of CRC-8, with the seed and the bit order stated in the header. Verify
    against a known-good vector rather than against your own implementation.
v7  Two-byte big-endian length field with a maximum-length rejection, so a corrupt length can't
    make the parser wait for 65535 bytes.

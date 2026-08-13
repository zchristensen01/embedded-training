# binary_frame_py — variants

v1  Fixed-layout frame: sync byte, `uint16` length, `uint16` id, `int16` value, `uint8` CRC.
    Little-endian, explicit prefix. `decode()` only — one frame in, dict out, `FrameError`
    on a short buffer or a bad CRC.
v2  Signed and unsigned side by side: an `int16` acceleration and a `uint16` temperature in
    the same frame. Write the test that fails if you swap `h` and `H` — 0xFFF6 as 65526
    looks like a plausible reading, so the test has to assert the value, not just the type.
v3  Big-endian, and `!` network order for one field. Prove with a test that a native-order
    decode of the same bytes returns different numbers rather than raising.
v4  Stream reassembly: `frames()` over arbitrary chunks. Feed it a frame split at every
    possible offset, and two frames arriving in one chunk. A read is not a message.
v5  Type-length-value: variable-length records, type then length then exactly that many
    bytes. Validate the declared length against the remaining buffer before slicing.
    A sync byte inside a payload must not end a frame.
v6  Zero-copy: same decoder using `memoryview` and `struct.unpack_from` at an offset, with
    no slicing in the hot loop, plus a precompiled `struct.Struct`. State what you measured.
v7  Fault injection is the deliverable: `decode()` unchanged, but write the test suite that
    proves recovery from a truncated frame, a bad CRC, an impossible length, and a stream
    that resynchronises after garbage. This is the variant that maps onto T18.

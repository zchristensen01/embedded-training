# bitops — variants

v1  Plain functions over `uint32_t`. Set, clear, toggle, test, `field_get`, `field_set`,
    `popcount`, `count_leading_zeros`, `reverse_bits`, `is_power_of_two`.
v2  Fake peripheral: a struct of `volatile uint32_t` registers, with the same operations
    written as a driver against it rather than as free functions on plain integers. Point it
    at a normal variable in the test and inspect what the driver actually wrote.
v3  Branchless and loopless `popcount` and `reverse_bits` — parallel bit counting and
    shift-and-mask. Then compare against `__builtin_popcount` in Compiler Explorer.
v4  Endianness: `bswap16`/`bswap32`, plus read and write a big-endian 32-bit value out of a
    `uint8_t` buffer without ever casting the buffer to a wider type.
v5  Width-agnostic: make `field_get`/`field_set` work on 8-, 16- and 32-bit words through
    `_Generic` or macros, without duplicating the logic three times.
v6  Total functions: every operation must be defined for every input, including `n >= 32`,
    `width == 0`, and `lsb + width > 32`. No undefined shifts anywhere — the sanitizers will
    tell you whether you succeeded.
v7  Bit array: set, clear and test bit `n` of an arbitrary-length `uint8_t` array, with the
    index arithmetic done in terms of `CHAR_BIT` rather than a hard-coded 8.

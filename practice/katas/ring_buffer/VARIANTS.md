# ring_buffer — variants

v1  Count-based. A `count` field disambiguates full from empty, so all capacity slots are
    usable. Push and pop both read-modify-write it.
v2  Lock-free single-producer / single-consumer. Delete `count`, sacrifice one slot, and
    arrange that only the producer writes `head` and only the consumer writes `tail`. Both
    `volatile`. One writer per variable is the whole trick.
v3  Power-of-two capacity. Reject a non-power-of-two in `rb_init`, then replace `% capacity`
    with `& (capacity - 1)`. Read the ARM assembly for both and see what the divide cost.
v4  Overwrite-oldest. A push into a full buffer drops the oldest byte instead of failing.
    Decide what `rb_count` means during an overwrite and write that in the header.
v5  Generic element size. Elements are `void *` of a fixed size given at init; push and pop
    `memcpy` in and out. Alignment is now your problem — say how you handled it.
v6  Bulk transfer. `rb_write(rb, const uint8_t *, n)` and `rb_read(rb, uint8_t *, n)`, each
    returning how many it moved, and each doing at most two `memcpy` calls across the wrap.
v7  Peek without pop, plus `rb_discard(n)`. Add both without breaking the frozen tests for
    the variant you started from.
v8  Interrupt-driven UART, both directions. Two buffers behind an ISR: RX pushes a byte and
    returns, TX pops one. The trap is the TX-empty interrupt — enable it when you queue data,
    and **disable it the moment the buffer drains**, or the ISR re-fires forever on an empty
    buffer and the device livelocks. Do no parsing in the ISR. State which side owns head and
    which owns tail, and why that is what makes it safe without a lock.

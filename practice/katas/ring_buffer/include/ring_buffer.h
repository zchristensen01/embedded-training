#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* rb must be non-NULL and initialised; violating that is undefined behaviour,
 * not a checked error. v1 is single-threaded only — see VARIANTS.md v2. */

typedef struct {
    uint8_t *buffer; // points at the storage for the buffer that the caller owns
    size_t capacity; // how many bytes that storage holds
    size_t count; // how many bytes are currently in it
    size_t head; // write index
    size_t tail; // read index
} ring_buffer;

/**
 * @brief   initialize an empty ring buffer from a caller supplied storage
 * @param[out] rb   empty on return
 * @param[in] buffer  at least @p capacity bytes (not copied or freed so must outlive @p rb) - contents untouched
 * @param[in] capacity    bytes of @p buffer
 * @note    capacity can not be 0
 */
void rb_init(ring_buffer *rb, uint8_t *buffer, size_t capacity);

/**
 * @brief   append one byte to the head of ring buffer
 * @param[in, out] rb   returned with appended value
 * @param[in] byte  value written to head in @p rb   
 * @return  true if successful, false if full
 * @note    on false, nothing changed
 */
bool rb_push(ring_buffer *rb, uint8_t byte);

/**
 * @brief   read one byte from the tail of ring buffer
 * @param[in, out] rb returned with tail incremented by 1
 * @param[out] out  location passed in by caller, read value written to it and returned
 * @return  true if successful, false if empty
 * @note    out is unmodified on failure
 */
bool rb_pop(ring_buffer *rb, uint8_t *out);

/**
 * @brief   returns count to see if @p rb->buffer is empty
 * @param[in] rb   returned untouched
 * @return  true if empty, false if non-empty
 */
bool rb_is_empty(const ring_buffer *rb);

/**
 * @brief   returns count to see if @p rb->buffer is full
 * @param[in] rb   returned untouched
 * @return  true if full, false if non-full
 */
bool rb_is_full(const ring_buffer *rb);

/**
 * @brief   returns count of bytes in @p rb->buffer
 * @param[in] rb   returned untouched
 * @return  current count of bytes in @p rb
 */
size_t rb_count(const ring_buffer *rb);


#endif /* RING_BUFFER_H */

/* tests/test_ring_buffer.c — FROZEN. You do not edit this during a drill.
 *
 * Write these cases yourself. Every one. AI may write the runner below this line
 * and the assert macros; it may not write a case. "How would you test this" is a
 * top-three interview question in both tracks, and this file is your answer.
 */
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "ring_buffer.h"

static int failures = 0;

#define CHECK(cond)                                                            \
    do {                                                                       \
        if (!(cond)) {                                                         \
            printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond);             \
            failures++;                                                        \
        }                                                                       \
    } while (0)

static void test_pop_on_empty_fails_and_preserves_out(void) {
    uint8_t storage[8];
    ring_buffer rb;
    uint8_t out = 0xAA;
    rb_init(&rb, storage, sizeof storage);

    CHECK(!rb_pop(&rb, &out));
    CHECK(out == 0xAA);
}

static void test_push_three_pop_three_FIFO(void) {
    uint8_t storage[8];
    ring_buffer rb;
    rb_init(&rb, storage, sizeof storage);

    uint8_t out = 0;

    uint8_t pushOne = 0xAA;
    uint8_t pushTwo = 0xAB;
    uint8_t pushThree = 0xAC;
    rb_push(&rb, pushOne);
    rb_push(&rb, pushTwo);
    rb_push(&rb, pushThree);

    CHECK(rb_pop(&rb, &out));
    CHECK(out == 0xAA);

    CHECK(rb_pop(&rb, &out));
    CHECK(out == 0xAB);

    CHECK(rb_pop(&rb, &out));
    CHECK(out == 0xAC);
}

static void test_full_buffer_returns_false_and_no_corruption(void) {
    uint8_t storage[8];
    ring_buffer rb;
    rb_init(&rb, storage, sizeof storage);

    for (size_t i = 0; i < sizeof storage; i++) {
        rb_push(&rb, 0xAA);
    }

    CHECK(!rb_push(&rb, 0xAB));
    CHECK(rb_is_full(&rb));
    CHECK(!rb_is_empty(&rb));

    for (size_t j = 0; j < sizeof storage; j++) {
        CHECK(storage[j] == 0xAA);
    }
}

static void test_drained_rb_storage_pop_fails_and_out_unchanged(void) {
    uint8_t storage[8];
    ring_buffer rb;
    rb_init(&rb, storage, sizeof storage);

    uint8_t out = 0xAA;

    for (size_t i = 0; i < sizeof storage; i++) {
        rb_push(&rb, 0xAB);
    }

    CHECK(rb_count(&rb) == 8);

    out = 0xAC;

    for (size_t i = 0; i < sizeof storage; i++) {
        rb_pop(&rb, &out);
    }

    CHECK(out == 0xAB);

    out = 0xAD;

    CHECK(!rb_pop(&rb, &out));
    CHECK(out == 0xAD);
}

static void test_wraparound_correctness(void) {
    uint8_t storage[8];
    ring_buffer rb;
    rb_init(&rb, storage, sizeof storage);

    uint8_t out = 0xAA;

    // round 1
    for (size_t i = 0; i < sizeof storage; i++) {
        rb_push(&rb, (0xA0 + i));
    }

    CHECK(rb_count(&rb) == 8);

    rb_pop(&rb, &out);
    CHECK(out == (0xA0));
    CHECK(rb_push(&rb, 0xA0 + (sizeof storage)));
    CHECK(!rb_push(&rb, 0xAC));
    
    out = 0xCC;

    for (size_t i = 0; i < sizeof storage; i++) {
        rb_pop(&rb, &out);
        CHECK(out == (0xA1 + i));
    }

    CHECK(rb_count(&rb) == 0);
    CHECK(!rb_pop(&rb, &out));

    // round 2
    for (size_t i = 0; i < sizeof storage; i++) {
        rb_push(&rb, (0xA0 + i));
    }

    CHECK(rb_count(&rb) == 8);

    rb_pop(&rb, &out);
    CHECK(out == (0xA0));
    CHECK(rb_push(&rb, 0xA0 + (sizeof storage)));
    CHECK(!rb_push(&rb, 0xAC));
    
    out = 0xCC;

    for (size_t i = 0; i < sizeof storage; i++) {
        rb_pop(&rb, &out);
        CHECK(out == (0xA1 + i));
    }

    CHECK(rb_count(&rb) == 0);
    CHECK(!rb_pop(&rb, &out));
    CHECK(rb_push(&rb, 0xAA));
    CHECK(rb_count(&rb) == 1);

}

static void test_interleaved_partial_fills_count_accuracy(void) {
    uint8_t storage[8];
    ring_buffer rb;
    rb_init(&rb, storage, sizeof storage);

    uint8_t out = 0xAA;

    // push 4
    CHECK(rb_push(&rb, 0xAA));
    CHECK(rb_push(&rb, 0xAB));
    CHECK(rb_push(&rb, 0xAC));
    CHECK(rb_push(&rb, 0xAD));
    CHECK(rb_count(&rb) == 4);


    // pop 4
    CHECK(rb_pop(&rb, &out));
    CHECK(out == (0xAA));
    CHECK(rb_pop(&rb, &out));
    CHECK(out == (0xAB));
    CHECK(rb_pop(&rb, &out));
    CHECK(out == (0xAC));
    CHECK(rb_pop(&rb, &out));
    CHECK(out == (0xAD));
    CHECK(rb_count(&rb) == 0);


    // push 2
    CHECK(rb_push(&rb, 0xDD));
    CHECK(rb_push(&rb, 0xDA));
    CHECK(rb_count(&rb) == 2);


    // pop 1
    CHECK(rb_pop(&rb, &out));
    CHECK(out == (0xDD));
    CHECK(rb_count(&rb) == 1);

    // push 1
    CHECK(rb_push(&rb, 0xDF));
    CHECK(rb_count(&rb) == 2);


    // pop 2
    CHECK(rb_pop(&rb, &out));
    CHECK(out == (0xDA));
    CHECK(rb_pop(&rb, &out));
    CHECK(out == (0xDF));
    CHECK(rb_count(&rb) == 0);

}

int main(void)
{
    test_pop_on_empty_fails_and_preserves_out();
    test_push_three_pop_three_FIFO();
    test_full_buffer_returns_false_and_no_corruption();
    test_drained_rb_storage_pop_fails_and_out_unchanged();
    test_wraparound_correctness();
    test_interleaved_partial_fills_count_accuracy();

    if (failures == 0) {
        printf("ok: all cases passed\n");
        return 0;
    }
    printf("%d failure(s)\n", failures);
    return 1;
}

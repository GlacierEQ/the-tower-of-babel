/**
 * C — Advanced Example: Lock-Free SPSC Ring Buffer for Real-Time Telemetry
 * What: Single-Producer Single-Consumer lock-free ring buffer using memory barriers.
 * Where: Real-time telemetry pipelines, audio processing, embedded flight controllers.
 * When: Sub-microsecond latency with zero system calls and zero locks.
 * Why: C gives direct access to cache-line alignment and memory ordering primitics.
 * How: Atomic load/store with acquire/release semantics on aligned cache lines.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <string.h>

#define RING_CAPACITY 65536       /* Must be power of 2 */
#define CACHE_LINE_SIZE 64

typedef struct __attribute__((aligned(CACHE_LINE_SIZE))) {
    uint64_t timestamp_ns;
    float    accel_x, accel_y, accel_z;     /* m/s^2 */
    float    gyro_x, gyro_y, gyro_z;        /* rad/s */
    float    pressure_pa;
    float    temperature_c;
    uint32_t sensor_id;
    uint32_t sequence;
} TelemetryFrame;

typedef struct {
    TelemetryFrame buffer[RING_CAPACITY];

    /* Producer-owned: aligned to separate cache line */
    _Alignas(CACHE_LINE_SIZE) _Atomic(uint64_t) write_idx;

    /* Consumer-owned: aligned to separate cache line */
    _Alignas(CACHE_LINE_SIZE) _Atomic(uint64_t) read_idx;

    /* Statistics */
    _Alignas(CACHE_LINE_SIZE) _Atomic(uint64_t) total_produced;
    _Atomic(uint64_t) total_consumed;
    _Atomic(uint64_t) total_dropped;
} SPSCRingBuffer;

SPSCRingBuffer* ring_create(void) {
    SPSCRingBuffer* ring = (SPSCRingBuffer*)aligned_alloc(
        CACHE_LINE_SIZE, sizeof(SPSCRingBuffer));
    if (!ring) return NULL;
    memset(ring, 0, sizeof(SPSCRingBuffer));
    atomic_store_explicit(&ring->write_idx, 0, memory_order_relaxed);
    atomic_store_explicit(&ring->read_idx, 0, memory_order_relaxed);
    atomic_store_explicit(&ring->total_produced, 0, memory_order_relaxed);
    atomic_store_explicit(&ring->total_consumed, 0, memory_order_relaxed);
    atomic_store_explicit(&ring->total_dropped, 0, memory_order_relaxed);
    return ring;
}

/**
 * Producer: try to enqueue a frame (non-blocking).
 * Returns true on success, false if ring is full (frame dropped).
 */
bool ring_try_push(SPSCRingBuffer* ring, const TelemetryFrame* frame) {
    uint64_t wr = atomic_load_explicit(&ring->write_idx, memory_order_relaxed);
    uint64_t rd = atomic_load_explicit(&ring->read_idx, memory_order_acquire);

    if (wr - rd >= RING_CAPACITY) {
        atomic_fetch_add_explicit(&ring->total_dropped, 1, memory_order_relaxed);
        return false;  /* Full — drop frame */
    }

    ring->buffer[wr & (RING_CAPACITY - 1)] = *frame;

    /* Release barrier: ensure frame is visible before advancing write_idx */
    atomic_store_explicit(&ring->write_idx, wr + 1, memory_order_release);
    atomic_fetch_add_explicit(&ring->total_produced, 1, memory_order_relaxed);
    return true;
}

/**
 * Consumer: try to dequeue a frame (non-blocking).
 * Returns true on success, false if ring is empty.
 */
bool ring_try_pop(SPSCRingBuffer* ring, TelemetryFrame* out) {
    uint64_t rd = atomic_load_explicit(&ring->read_idx, memory_order_relaxed);
    uint64_t wr = atomic_load_explicit(&ring->write_idx, memory_order_acquire);

    if (rd >= wr) {
        return false;  /* Empty */
    }

    *out = ring->buffer[rd & (RING_CAPACITY - 1)];

    /* Release barrier: ensure read completes before advancing read_idx */
    atomic_store_explicit(&ring->read_idx, rd + 1, memory_order_release);
    atomic_fetch_add_explicit(&ring->total_consumed, 1, memory_order_relaxed);
    return true;
}

uint64_t ring_size(const SPSCRingBuffer* ring) {
    uint64_t wr = atomic_load_explicit(&ring->write_idx, memory_order_acquire);
    uint64_t rd = atomic_load_explicit(&ring->read_idx, memory_order_acquire);
    return wr - rd;
}

void ring_stats(const SPSCRingBuffer* ring) {
    printf("[SPSC Ring] produced=%llu consumed=%llu dropped=%llu queued=%llu\n",
           (unsigned long long)atomic_load(&ring->total_produced),
           (unsigned long long)atomic_load(&ring->total_consumed),
           (unsigned long long)atomic_load(&ring->total_dropped),
           (unsigned long long)ring_size(ring));
}

void ring_destroy(SPSCRingBuffer* ring) {
    free(ring);
}

/* Standalone test */
int main(void) {
    SPSCRingBuffer* ring = ring_create();
    if (!ring) { fprintf(stderr, "Failed to allocate ring\n"); return 1; }

    /* Produce 1000 frames */
    for (uint32_t i = 0; i < 1000; i++) {
        TelemetryFrame frame = {
            .timestamp_ns = i * 1000000ULL,
            .accel_x = 0.0f, .accel_y = 0.0f, .accel_z = -9.81f,
            .gyro_x = 0.0f, .gyro_y = 0.0f, .gyro_z = 0.0f,
            .pressure_pa = 101325.0f,
            .temperature_c = 22.5f,
            .sensor_id = 1,
            .sequence = i,
        };
        ring_try_push(ring, &frame);
    }

    /* Consume all */
    TelemetryFrame out;
    int consumed = 0;
    while (ring_try_pop(ring, &out)) consumed++;

    printf("Consumed %d frames\n", consumed);
    ring_stats(ring);
    ring_destroy(ring);
    return 0;
}

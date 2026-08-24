// ============================================================================
// WHAT: In-kernel eBPF security sentinel with kprobe syscall interception
// WHERE: Linux kernel LSM and kprobe trace layer for container process isolation
// WHEN: Zero-overhead real-time telemetry is required without user-space switches
// WHY: In-kernel verification guarantees safe execution without kernel crashes
// HOW: kprobe hook on sys_execve with RingBuffer zero-copy event streaming
// ============================================================================

typedef unsigned char __u8;
typedef unsigned short __u16;
typedef unsigned int __u32;
typedef unsigned long long __u64;

#define SEC(NAME) __attribute__((section(NAME), used))
#define BPF_ANY 0
#define BPF_MAP_TYPE_HASH 1
#define BPF_MAP_TYPE_RINGBUF 27

#define MAX_FILENAME_LEN 256
#define MAX_ENTRIES 10240

struct bpf_map_def {
    __u32 type;
    __u32 key_size;
    __u32 value_size;
    __u32 max_entries;
    __u32 map_flags;
};

struct process_event_t {
    __u32 pid;
    __u32 tgid;
    __u32 uid;
    __u64 timestamp_ns;
    char comm[16];
    char filename[MAX_FILENAME_LEN];
    __u32 event_type;
};

struct bpf_map_def SEC("maps") events = {
    .type = BPF_MAP_TYPE_RINGBUF,
    .max_entries = 256 * 1024,
};

struct bpf_map_def SEC("maps") rate_limit_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(__u32),
    .value_size = sizeof(__u64),
    .max_entries = MAX_ENTRIES,
};

// BPF Helper Function Pointers
static __u64 (*bpf_ktime_get_ns)(void) = (void *) 5;
static __u64 (*bpf_get_current_pid_tgid)(void) = (void *) 14;
static __u64 (*bpf_get_current_uid_gid)(void) = (void *) 15;
static long (*bpf_get_current_comm)(void *buf, __u32 size_of_buf) = (void *) 16;
static void *(*bpf_map_lookup_elem)(void *map, const void *key) = (void *) 1;
static long (*bpf_map_update_elem)(void *map, const void *key, const void *value, __u64 flags) = (void *) 2;
static void *(*bpf_ringbuf_reserve)(void *ringbuf, __u64 size, __u64 flags) = (void *) 131;
static void (*bpf_ringbuf_submit)(void *data, __u64 flags) = (void *) 132;

SEC("kprobe/__x64_sys_execve")
int kprobe_execve(void *ctx) {
    (void)ctx;
    __u64 pid_tgid = bpf_get_current_pid_tgid();
    __u32 pid = (__u32)pid_tgid;
    __u32 tgid = (__u32)(pid_tgid >> 32);
    __u64 now = bpf_ktime_get_ns();

    // Check rate limit map
    __u64 *last_seen = bpf_map_lookup_elem(&rate_limit_map, &pid);
    if (last_seen && (now - *last_seen < 10000000ULL)) {
        return 0;
    }
    bpf_map_update_elem(&rate_limit_map, &pid, &now, BPF_ANY);

    // Reserve space in Ring Buffer
    struct process_event_t *event = bpf_ringbuf_reserve(&events, sizeof(struct process_event_t), 0);
    if (!event) {
        return 0;
    }

    event->pid = pid;
    event->tgid = tgid;
    event->uid = (__u32)bpf_get_current_uid_gid();
    event->timestamp_ns = now;
    event->event_type = 1;

    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    bpf_ringbuf_submit(event, 0);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";

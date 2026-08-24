// ============================================================================
// WHAT: In-kernel eBPF security sentinel with kprobe syscall interception
// WHERE: Linux kernel LSM and kprobe trace layer for container process isolation
// WHEN: Zero-overhead real-time telemetry is required without user-space switches
// WHY: In-kernel verification guarantees safe execution without kernel crashes
// HOW: kprobe hook on sys_execve with RingBuffer zero-copy event streaming
// ============================================================================

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define MAX_FILENAME_LEN 256
#define MAX_ENTRIES 10240

struct process_event_t {
    __u32 pid;
    __u32 tgid;
    __u32 uid;
    __u64 timestamp_ns;
    char comm[16];
    char filename[MAX_FILENAME_LEN];
    __u32 event_type;
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, __u32);
    __type(value, __u64);
} rate_limit_map SEC(".maps");

SEC("kprobe/__x64_sys_execve")
int BPF_KPROBE(kprobe_execve, const char *filename, const char *const *argv, const char *const *envp) {
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
    bpf_probe_read_user_str(&event->filename, sizeof(event->filename), filename);

    bpf_ringbuf_submit(event, 0);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";

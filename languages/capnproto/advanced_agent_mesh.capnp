# =============================================================================
# WHAT: Cap'n Proto zero-copy RPC and distributed memory mesh schema
# WHERE: Inter-agent high-throughput communication & IPC memory bus
# WHEN: Sub-microsecond serialization and capability passing is required
# WHY: Eliminates encoding/decoding CPU overhead via structured pointer alignment
# HOW: Interfaces, streaming pipes, union variants, and capability passing
# =============================================================================

@0xa1b2c3d4e5f60718;

enum TaskPriority {
    low @0;
    standard @1;
    urgent @2;
    emergencyCeiling @3;
}

enum NodeStatus {
    offline @0;
    idle @1;
    busy @2;
    degraded @3;
    activeMastermind @4;
}

struct Vector3D {
    x @0 :Float64;
    y @1 :Float64;
    z @2 :Float64;
}

struct AgentCapability {
    capabilityId @0 :Text;
    allowedDomains @1 :List(Text);
    tokenCeiling @2 :UInt32;
    expirationTimestamp @3 :UInt64;
}

struct TaskPayload {
    taskId @0 :Text;
    priority @1 :TaskPriority;
    createdAt @2 :UInt64;
    targetDomain @3 :Text;
    
    union {
        codeRefactor :group {
            targetFile @4 :Text;
            startLine @5 :UInt32;
            endLine @6 :UInt32;
            replacementCode @7 :Data;
        }
        semanticQuery :group {
            vectorEmbedding @8 :List(Float32);
            similarityThreshold @9 :Float32;
        }
        rawBinaryExecution :group {
            executableBytes @10 :Data;
            arguments @11 :List(Text);
        }
    }
}

struct TaskReceipt {
    taskId @0 :Text;
    nodeId @1 :Text;
    success @2 :Bool;
    executionTimeMicroseconds @3 :UInt64;
    cryptographicHash @4 :Data;
    errorDetail @5 :Text;
}

interface AgentNode {
    ping @0 () -> (status :NodeStatus, loadFactor :Float32);
    submitTask @1 (task :TaskPayload) -> (receipt :TaskReceipt);
    exchangeCapabilities @2 (capabilities :List(AgentCapability)) -> (accepted :Bool);
}

interface MeshOrchestrator {
    registerNode @0 (nodeId :Text, node :AgentNode, capabilities :List(AgentCapability)) -> (meshSessionId :Text);
    dispatchGlobalTask @1 (task :TaskPayload) -> (receipt :TaskReceipt);
}

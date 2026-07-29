"""
Python — Advanced Example: Async Multi-Agent Orchestrator with Priority Scheduling
What: Production-grade async agent coordinator with backpressure, circuit breakers, and structured concurrency.
Where: AI agent systems, distributed inference pipelines, MCP server orchestration.
When: Coordinating multiple LLM inference workers with heterogeneous hardware.
Why: Python's asyncio + dataclasses provide elegant actor-model concurrency.
How: asyncio event loop with semaphore-based backpressure and exponential backoff.
"""

import asyncio
import dataclasses
import hashlib
import time
from collections import defaultdict
from enum import Enum, auto
from typing import Any, Callable, Optional


class AgentState(Enum):
    IDLE = auto()
    RUNNING = auto()
    CIRCUIT_OPEN = auto()
    DRAINING = auto()


class Priority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclasses.dataclass
class AgentTask:
    task_id: str
    priority: Priority
    payload: dict[str, Any]
    created_at: float = dataclasses.field(default_factory=time.monotonic)
    retries: int = 0
    max_retries: int = 3

    def __lt__(self, other: "AgentTask") -> bool:
        return self.priority.value < other.priority.value


@dataclasses.dataclass
class AgentMetrics:
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_latency_ms: float = 0.0
    circuit_trips: int = 0

    @property
    def avg_latency_ms(self) -> float:
        if self.tasks_completed == 0:
            return 0.0
        return self.total_latency_ms / self.tasks_completed

    @property
    def success_rate(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 1.0
        return self.tasks_completed / total


class CircuitBreaker:
    """Trips after consecutive failures, auto-resets after cooldown."""

    def __init__(self, failure_threshold: int = 5, cooldown_s: float = 30.0):
        self.failure_threshold = failure_threshold
        self.cooldown_s = cooldown_s
        self.consecutive_failures = 0
        self.last_failure_time = 0.0
        self.is_open = False

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.is_open = False

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        self.last_failure_time = time.monotonic()
        if self.consecutive_failures >= self.failure_threshold:
            self.is_open = True

    def can_proceed(self) -> bool:
        if not self.is_open:
            return True
        elapsed = time.monotonic() - self.last_failure_time
        if elapsed >= self.cooldown_s:
            self.is_open = False  # Half-open: allow one attempt
            return True
        return False


class Agent:
    """Single agent worker with circuit breaker and backpressure."""

    def __init__(
        self,
        agent_id: str,
        handler: Callable[[dict[str, Any]], Any],
        concurrency: int = 4,
    ):
        self.agent_id = agent_id
        self.handler = handler
        self.state = AgentState.IDLE
        self.metrics = AgentMetrics()
        self.circuit = CircuitBreaker()
        self._semaphore = asyncio.Semaphore(concurrency)
        self._queue: asyncio.PriorityQueue[AgentTask] = asyncio.PriorityQueue()

    async def submit(self, task: AgentTask) -> None:
        await self._queue.put(task)

    async def _execute_task(self, task: AgentTask) -> Any:
        async with self._semaphore:
            if not self.circuit.can_proceed():
                self.metrics.tasks_failed += 1
                raise RuntimeError(f"Circuit open for agent {self.agent_id}")

            start = time.monotonic()
            try:
                if asyncio.iscoroutinefunction(self.handler):
                    result = await self.handler(task.payload)
                else:
                    result = self.handler(task.payload)
                elapsed_ms = (time.monotonic() - start) * 1000
                self.metrics.tasks_completed += 1
                self.metrics.total_latency_ms += elapsed_ms
                self.circuit.record_success()
                return result
            except Exception as exc:
                self.circuit.record_failure()
                self.metrics.tasks_failed += 1
                if task.retries < task.max_retries:
                    task.retries += 1
                    backoff = min(2 ** task.retries * 0.1, 5.0)
                    await asyncio.sleep(backoff)
                    await self._queue.put(task)
                raise

    async def run(self) -> None:
        self.state = AgentState.RUNNING
        while self.state == AgentState.RUNNING:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                asyncio.create_task(self._execute_task(task))
            except asyncio.TimeoutError:
                continue


class MultiAgentOrchestrator:
    """Coordinates multiple agents with priority-based task distribution."""

    def __init__(self) -> None:
        self.agents: dict[str, Agent] = {}
        self._routing_table: dict[str, list[str]] = defaultdict(list)
        self._running = False

    def register_agent(
        self,
        agent_id: str,
        handler: Callable,
        capabilities: list[str],
        concurrency: int = 4,
    ) -> None:
        agent = Agent(agent_id, handler, concurrency)
        self.agents[agent_id] = agent
        for cap in capabilities:
            self._routing_table[cap].append(agent_id)

    def _select_agent(self, capability: str) -> Optional[str]:
        candidates = self._routing_table.get(capability, [])
        if not candidates:
            return None
        # Select agent with lowest latency and open circuit
        best_id = None
        best_score = float("inf")
        for aid in candidates:
            agent = self.agents[aid]
            if agent.circuit.is_open:
                continue
            score = agent.metrics.avg_latency_ms + agent._queue.qsize() * 10
            if score < best_score:
                best_score = score
                best_id = aid
        return best_id

    async def dispatch(
        self, capability: str, payload: dict[str, Any], priority: Priority = Priority.NORMAL
    ) -> bool:
        agent_id = self._select_agent(capability)
        if agent_id is None:
            return False
        task_id = hashlib.sha256(f"{time.monotonic()}{capability}".encode()).hexdigest()[:12]
        task = AgentTask(task_id=task_id, priority=priority, payload=payload)
        await self.agents[agent_id].submit(task)
        return True

    async def start(self) -> None:
        self._running = True
        tasks = [asyncio.create_task(agent.run()) for agent in self.agents.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

    def report(self) -> dict[str, Any]:
        return {
            aid: {
                "completed": a.metrics.tasks_completed,
                "failed": a.metrics.tasks_failed,
                "avg_latency_ms": round(a.metrics.avg_latency_ms, 2),
                "success_rate": round(a.metrics.success_rate, 4),
                "circuit_open": a.circuit.is_open,
            }
            for aid, a in self.agents.items()
        }


if __name__ == "__main__":

    async def mock_inference(payload: dict) -> dict:
        await asyncio.sleep(0.01)
        return {"result": f"processed-{payload.get('id', 'unknown')}"}

    async def main() -> None:
        orch = MultiAgentOrchestrator()
        orch.register_agent("worker-0", mock_inference, ["inference", "reasoning"], concurrency=8)
        orch.register_agent("worker-1", mock_inference, ["inference", "vision"], concurrency=4)

        for i in range(20):
            await orch.dispatch("inference", {"id": i}, Priority.NORMAL)

        # Run for a short burst
        try:
            await asyncio.wait_for(orch.start(), timeout=2.0)
        except asyncio.TimeoutError:
            pass

        print(orch.report())

    asyncio.run(main())

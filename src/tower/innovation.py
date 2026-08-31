"""Babel Innovation Engine: semantic boundary → language specialization → Spiral.

The Tower of Babel is not a contest for one repository-wide language.
It evaluates the work being performed at each architectural boundary and places
languages where their native strengths create the most capability and stability.

Examples:
- memory/data-layout boundary → Odin/Rust/Zig/C-family evaluated for explicit
  allocation, layout, determinism, safety, migration and interface costs.
- logic/policy boundary → Rust and other correctness-oriented runtimes evaluated
  for invariants, types, concurrency and evidence.
- action/interface boundary → TypeScript/Go/Python/etc. evaluated for async I/O,
  connectors, RPC/web surfaces and operational reach.

The Spiral repeatedly re-evaluates the real repository after each intervention.
Local gain is rejected when it creates a larger near- or far-term loss.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .registry import TowerRegistry

SCHEMA = "glaciereq.babel-innovation.v2"
DEFAULT_TARGET = 9.0
MAX_TEXT_BYTES = 750_000

IGNORED_DIRS = frozenset({
    ".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv", "node_modules",
    "dist", "build", "target", "vendor", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".next", "coverage",
})

LANGUAGE_EXTENSIONS: Mapping[str, tuple[str, ...]] = {
    "python": (".py",), "rust": (".rs",), "go": (".go",),
    "typescript": (".ts", ".tsx"), "javascript": (".js", ".jsx", ".mjs", ".cjs"),
    "c": (".c", ".h"), "cpp": (".cc", ".cpp", ".cxx", ".hpp", ".hh"),
    "odin": (".odin",), "zig": (".zig",), "java": (".java",),
    "kotlin": (".kt", ".kts"), "swift": (".swift",), "scala": (".scala", ".sbt"),
    "elixir": (".ex", ".exs"), "haskell": (".hs",), "julia": (".jl",),
    "r": (".r", ".R"), "lua": (".lua",), "sql": (".sql",),
    "protobuf": (".proto",), "webassembly": (".wat", ".wasm"),
    "lean": (".lean",), "coq": (".v",), "agda": (".agda",),
    "terraform": (".tf",),
}

SEMANTIC_ROLES = (
    "memory", "logic", "action", "interface", "persistence",
    "orchestration", "telemetry", "security", "proof",
)

ROLE_HINTS: Mapping[str, tuple[str, ...]] = {
    "memory": ("memory", "arena", "allocator", "buffer", "cache", "store", "state", "pool",
               "heap", "stack", "layout", "slab", "ring", "queue", "vector", "matrix"),
    "logic": ("logic", "rule", "policy", "decision", "evaluate", "resolver", "planner",
              "algorithm", "constraint", "validate", "invariant", "engine", "kernel"),
    "action": ("action", "execute", "command", "worker", "job", "task", "handler",
               "dispatch", "effect", "mutation", "write", "apply", "operation", "tool"),
    "interface": ("api", "rpc", "mcp", "schema", "proto", "interface", "contract",
                  "gateway", "http", "web", "endpoint", "request", "response", "json"),
    "persistence": ("database", "db", "sql", "repository", "ledger", "journal",
                    "snapshot", "checkpoint", "migration", "transaction", "persist"),
    "orchestration": ("orchestrat", "workflow", "pipeline", "agent", "router",
                      "coordinator", "supervisor", "scheduler", "session", "control-plane"),
    "telemetry": ("telemetry", "metric", "trace", "log", "event", "observability",
                  "monitor", "diagnostic", "receipt", "audit"),
    "security": ("security", "auth", "permission", "secret", "crypto", "hash",
                 "signature", "sandbox", "isolation", "evidence", "forensic", "threat"),
    "proof": ("proof", "theorem", "formal", "verify", "model-check", "invariant",
              "lean", "coq", "agda"),
}

# Priors only. Registry language descriptions and repo evidence can move the score.
LANGUAGE_ROLE_PRIORS: Mapping[str, Mapping[str, float]] = {
    "odin": {"memory": 1.00, "logic": .72, "action": .48, "interface": .32,
             "persistence": .42, "orchestration": .30, "telemetry": .42,
             "security": .60, "proof": .20},
    "rust": {"memory": .95, "logic": 1.00, "action": .76, "interface": .72,
             "persistence": .72, "orchestration": .68, "telemetry": .72,
             "security": 1.00, "proof": .66},
    "typescript": {"memory": .34, "logic": .76, "action": 1.00, "interface": 1.00,
                   "persistence": .58, "orchestration": .95, "telemetry": .76,
                   "security": .64, "proof": .32},
    "python": {"memory": .42, "logic": .78, "action": .90, "interface": .76,
               "persistence": .64, "orchestration": 1.00, "telemetry": .76,
               "security": .62, "proof": .42},
    "go": {"memory": .62, "logic": .76, "action": .92, "interface": .88,
           "persistence": .68, "orchestration": .86, "telemetry": 1.00,
           "security": .72, "proof": .28},
    "c": {"memory": .96, "logic": .72, "action": .60, "interface": .58,
          "persistence": .40, "orchestration": .28, "telemetry": .42,
          "security": .35, "proof": .22},
    "cpp": {"memory": .94, "logic": .84, "action": .68, "interface": .62,
            "persistence": .54, "orchestration": .48, "telemetry": .52,
            "security": .52, "proof": .28},
    "zig": {"memory": .98, "logic": .76, "action": .58, "interface": .50,
            "persistence": .44, "orchestration": .34, "telemetry": .46,
            "security": .58, "proof": .24},
    "sql": {"memory": .38, "logic": .62, "action": .32, "interface": .42,
            "persistence": 1.00, "orchestration": .30, "telemetry": .48,
            "security": .60, "proof": .30},
    "protobuf": {"memory": .30, "logic": .28, "action": .30, "interface": 1.00,
                 "persistence": .44, "orchestration": .48, "telemetry": .58,
                 "security": .44, "proof": .42},
    "webassembly": {"memory": .74, "logic": .70, "action": .60, "interface": .72,
                    "persistence": .32, "orchestration": .42, "telemetry": .40,
                    "security": .92, "proof": .50},
    "lean": {"memory": .18, "logic": .80, "action": .10, "interface": .24,
             "persistence": .16, "orchestration": .14, "telemetry": .16,
             "security": .58, "proof": 1.00},
    "coq": {"memory": .18, "logic": .80, "action": .10, "interface": .24,
            "persistence": .16, "orchestration": .14, "telemetry": .16,
            "security": .58, "proof": 1.00},
}

QUALITY_WEIGHTS: Mapping[str, float] = {
    "purpose_focus": .14, "correctness": .14, "testing": .12, "security": .11,
    "semantic_placement": .13, "interfaces": .09, "maintainability": .08,
    "observability": .06, "operability": .06, "evidence": .07,
}
CRITICAL_QUALITY = ("purpose_focus", "correctness", "testing", "security", "semantic_placement")


@dataclass(frozen=True)
class FileRole:
    path: str
    language: str | None
    kind: str
    evidence_weight: float
    roles: tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class LanguageFit:
    language: str
    role: str
    score: float
    registry_evidence: str | None
    current_presence: bool
    execution_ready: bool
    reason: str


@dataclass(frozen=True)
class RoleResolution:
    role: str
    demand: float
    current_languages: tuple[str, ...]
    selected: LanguageFit
    alternatives: tuple[LanguageFit, ...]
    recommendation: str
    interface_cost: float
    migration_cost: float


@dataclass(frozen=True)
class QualityAxis:
    name: str
    score: float
    weight: float
    evidence: tuple[str, ...]
    gaps: tuple[str, ...]


@dataclass(frozen=True)
class Impact:
    near_term: float
    far_term: float
    capability_gain: float
    stability_gain: float
    reversibility: float
    risk: float
    effort: float
    complexity_delta: float

    @property
    def net(self) -> float:
        benefit = (
            .20 * self.near_term + .28 * self.far_term
            + .24 * self.capability_gain + .28 * self.stability_gain
            + .08 * self.reversibility
        )
        cost = .26 * self.risk + .18 * self.effort + .22 * max(0.0, self.complexity_delta)
        return round(benefit - cost, 6)


@dataclass(frozen=True)
class Intervention:
    intervention_id: str
    title: str
    role: str | None
    language: str | None
    reason: str
    impact: Impact
    priority: float
    completion_signal: str


@dataclass(frozen=True)
class RepoEvaluation:
    schema: str
    repository: str
    files: tuple[FileRole, ...]
    roles: tuple[RoleResolution, ...]
    quality: tuple[QualityAxis, ...]
    overall_score: float
    critical_floor: float
    target: float
    complete: bool
    fingerprint: str


@dataclass(frozen=True)
class Revolution:
    number: int
    before: float
    after: float
    intervention: Intervention | None
    status: str


Executor = Callable[[Intervention, Path], bool]


def _safe_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        try:
            if path.stat().st_size > MAX_TEXT_BYTES:
                continue
        except OSError:
            continue
        result.append(path)
    return sorted(result)


def _language(path: Path) -> str | None:
    suffix = path.suffix
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if suffix in extensions or suffix.lower() in {item.lower() for item in extensions}:
            return language
    return None


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _file_kind(path: Path, language: str | None) -> tuple[str, float]:
    """Classify evidence strength so prose cannot overpower executable reality."""
    lower_parts = {part.casefold() for part in path.parts}
    name = path.name.casefold()
    suffix = path.suffix.casefold()
    if "tests" in lower_parts or "test" in lower_parts or "spec" in lower_parts or name.startswith(("test_", "spec_")):
        return "test", .78
    if suffix in {".proto", ".sql", ".lean", ".v", ".agda"}:
        return "contract", .95
    if language is not None:
        return "implementation", 1.0
    if suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return "configuration", .62
    if suffix in {".md", ".rst", ".txt", ".adoc"}:
        return "documentation", .25
    return "support", .18


def _role_scores(path: Path, text: str) -> dict[str, float]:
    haystack = (path.as_posix() + "\n" + text[:80_000]).casefold()
    raw: dict[str, float] = {}
    for role, hints in ROLE_HINTS.items():
        hits = sum(haystack.count(hint.casefold()) for hint in hints)
        raw[role] = min(1.0, hits / 8.0)
    if path.suffix == ".proto":
        raw["interface"] = 1.0
    if path.suffix.lower() == ".sql":
        raw["persistence"] = 1.0
    if path.suffix.lower() in {".lean", ".v", ".agda"}:
        raw["proof"] = 1.0
    return raw


def classify_files(root: Path | str) -> tuple[FileRole, ...]:
    repo = Path(root).resolve()
    rows: list[FileRole] = []
    for path in _safe_files(repo):
        text = _read(path)
        relative = path.relative_to(repo)
        language = _language(path)
        kind, evidence_weight = _file_kind(relative, language)
        scores = _role_scores(relative, text)
        ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        selected = tuple(role for role, score in ordered if score >= .25)[:3]
        confidence = ordered[0][1] if ordered else 0.0
        rows.append(FileRole(
            path=relative.as_posix(),
            language=language,
            kind=kind,
            evidence_weight=evidence_weight,
            roles=selected,
            confidence=round(confidence, 3),
        ))
    return tuple(rows)


def _registry_text(row: Mapping[str, Any]) -> str:
    return " ".join(
        str(row.get(key, "")) for key in ("what", "where", "when", "why", "how")
    ).casefold()


def _registry_role_bonus(row: Mapping[str, Any] | None, role: str) -> float:
    if not row:
        return 0.0
    text = _registry_text(row)
    hits = sum(text.count(hint.casefold()) for hint in ROLE_HINTS[role])
    return min(.20, hits * .025)


def _evidence_bonus(row: Mapping[str, Any] | None) -> float:
    if not row:
        return 0.0
    state = str(row.get("evidence_state", "")).casefold()
    return {
        "production_reference": .10, "integrated": .09, "benchmark": .08,
        "tested": .07, "formally_verified": .09, "compiles": .04,
        "toolchain_gated": -.06, "service_gated": -.06, "hardware_gated": -.06,
        "illustrative": -.04,
    }.get(state, 0.0)


def _execution_ready(row: Mapping[str, Any] | None) -> bool:
    if not row:
        return False
    return str(row.get("evidence_state", "")).casefold() not in {
        "toolchain_gated", "service_gated", "hardware_gated", "illustrative",
    }


def _candidate_languages(registry: TowerRegistry, files: Sequence[FileRole]) -> tuple[str, ...]:
    present = {row.language for row in files if row.language}
    governed = {
        str(row.get("id", "")).casefold()
        for row in registry.technologies
        if isinstance(row, dict) and row.get("id")
    }
    candidates = present | governed | set(LANGUAGE_ROLE_PRIORS)
    return tuple(sorted(language for language in candidates if language in LANGUAGE_ROLE_PRIORS))


def _role_demand(files: Sequence[FileRole], role: str) -> float:
    supporting = [row for row in files if role in row.roles]
    if not supporting:
        return 0.0
    total_weight = sum(row.evidence_weight for row in files) or 1.0
    support_weight = sum(row.evidence_weight for row in supporting)
    density = support_weight / total_weight
    strength = (
        sum(row.confidence * row.evidence_weight for row in supporting)
        / max(.001, support_weight)
    )
    # Density shows how much of the actual repo performs this role; strength
    # prevents a small but unmistakable critical boundary from disappearing.
    return round(min(1.0, .65 * min(1.0, density * 3.0) + .35 * strength), 3)


def _current_languages(files: Sequence[FileRole], role: str) -> tuple[str, ...]:
    counts: dict[str, float] = {}
    for row in files:
        if role in row.roles and row.language:
            counts[row.language] = counts.get(row.language, 0.0) + row.evidence_weight * max(.25, row.confidence)
    return tuple(language for language, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _fit(
    registry: TowerRegistry,
    language: str,
    role: str,
    *,
    current: bool,
    interface_cost: float,
    migration_cost: float,
) -> LanguageFit:
    row = registry.by_id(language)
    prior = LANGUAGE_ROLE_PRIORS.get(language, {}).get(role, .0)
    ready = _execution_ready(row)
    score = prior + _registry_role_bonus(row, role) + _evidence_bonus(row)
    if current:
        score += .05  # existing proven integration has value
    elif not ready:
        score -= .10  # do not recommend a new gated dependency as if it were deployable
    score -= .12 * interface_cost + .10 * migration_cost
    score = round(max(0.0, min(1.0, score)), 6)
    reason = (
        f"role affinity={prior:.2f}; registry evidence="
        f"{row.get('evidence_state') if row else 'none'}; "
        f"interface_cost={interface_cost:.2f}; migration_cost={migration_cost:.2f}"
    )
    return LanguageFit(
        language=language,
        role=role,
        score=score,
        registry_evidence=str(row.get("evidence_state")) if row and row.get("evidence_state") else None,
        current_presence=current,
        execution_ready=ready,
        reason=reason,
    )


def resolve_roles(
    registry: TowerRegistry,
    files: Sequence[FileRole],
) -> tuple[RoleResolution, ...]:
    candidates = _candidate_languages(registry, files)
    present_all = {row.language for row in files if row.language}
    material_roles = [role for role in SEMANTIC_ROLES if _role_demand(files, role) >= .08]
    resolutions: list[RoleResolution] = []

    for role in material_roles:
        current = _current_languages(files, role)
        ranked: list[LanguageFit] = []
        for language in candidates:
            is_current = language in present_all
            interface_cost = 0.04 if is_current else min(.85, .15 + .08 * len(present_all))
            migration_cost = 0.03 if language in current else (.18 if is_current else .42)
            ranked.append(_fit(
                registry, language, role, current=is_current,
                interface_cost=interface_cost, migration_cost=migration_cost,
            ))
        ranked.sort(key=lambda item: (-item.score, item.language))
        selected = ranked[0]
        current_best = next((row for row in ranked if row.language in current), None)
        if current_best is None:
            if selected.execution_ready:
                recommendation = f"INTRODUCE {selected.language} for {role} only behind an explicit interface and measured experiment"
            else:
                recommendation = f"PROVE {selected.language} toolchain/runtime availability, then EXPERIMENT on the {role} boundary"
        elif selected.language == current_best.language:
            recommendation = f"FOCUS {selected.language} ownership of the {role} boundary"
        elif selected.score - current_best.score >= .12:
            recommendation = (
                f"EXPERIMENT {selected.language} for {role}; current {current_best.language} remains until "
                "capability/stability gain exceeds migration and interface cost"
            )
        else:
            selected = current_best
            recommendation = f"PRESERVE {current_best.language} for {role}; alternative advantage is not large enough"
        resolutions.append(RoleResolution(
            role=role,
            demand=_role_demand(files, role),
            current_languages=current,
            selected=selected,
            alternatives=tuple(ranked[:5]),
            recommendation=recommendation,
            interface_cost=round(.04 if selected.current_presence else min(.85, .15 + .08 * len(present_all)), 3),
            migration_cost=round(.03 if selected.language in current else (.18 if selected.current_presence else .42), 3),
        ))
    return tuple(sorted(resolutions, key=lambda row: (-row.demand, row.role)))


def _quality(root: Path, files: Sequence[FileRole], roles: Sequence[RoleResolution]) -> tuple[QualityAxis, ...]:
    paths = {row.path.casefold() for row in files}
    names = {Path(row.path).name.casefold() for row in files}
    tests = [row for row in files if "test" in Path(row.path).name.casefold() or "/tests/" in f"/{row.path.casefold()}/"]
    source = [row for row in files if row.language]
    has_ci = any(path.startswith(".github/workflows/") for path in paths)
    has_readme = "readme.md" in names
    has_security = "security.md" in names
    has_lock = any(name in names for name in {
        "cargo.lock", "go.sum", "package-lock.json", "pnpm-lock.yaml", "uv.lock",
        "poetry.lock", "requirements.lock",
    })
    has_arch = any("architecture" in name for name in names)
    has_observability = any(
        token in row.path.casefold()
        for row in files
        for token in ("telemetry", "metrics", "observability", "receipt", "audit")
    )
    role_count = len(roles)
    resolved_strength = (
        sum(row.selected.score for row in roles) / role_count if role_count else 0.0
    )
    overloaded = sum(
        1 for language in {row.language for row in files if row.language}
        if sum(1 for role in roles if language in role.current_languages) >= 6
    )
    interface_penalty = sum(row.interface_cost for row in roles) / role_count if role_count else 0.0

    def axis(name: str, score: float, evidence: Iterable[str], gaps: Iterable[str]) -> QualityAxis:
        return QualityAxis(
            name=name, score=round(max(0.0, min(10.0, score)), 3),
            weight=QUALITY_WEIGHTS[name], evidence=tuple(evidence), gaps=tuple(gaps),
        )

    test_ratio = len(tests) / max(1, len(source))
    return (
        axis("purpose_focus", 6.4 + (1.0 if has_arch else 0) + min(1.8, role_count * .22) - overloaded * .35,
             [f"{role_count} semantic boundaries resolved", f"{overloaded} overloaded language lanes"],
             [] if has_arch else ["document semantic boundary ownership"]),
        axis("correctness", 5.6 + min(2.2, test_ratio * 25) + (1.0 if has_ci else 0) + .7 * resolved_strength,
             [f"test/source ratio={test_ratio:.3f}", f"role-fit mean={resolved_strength:.3f}"],
             ([] if tests else ["add behavioral tests"]) + ([] if has_ci else ["execute tests in CI"])),
        axis("testing", 4.2 + min(3.6, test_ratio * 35) + (1.4 if has_ci else 0),
             [f"{len(tests)} test files", "CI present" if has_ci else "CI absent"],
             ([] if tests else ["add executable tests"]) + ([] if has_ci else ["add CI verification"])),
        axis("security", 5.0 + (1.3 if has_security else 0) + (1.1 if has_lock else 0) + (1.0 if has_ci else 0),
             ["SECURITY.md present" if has_security else "SECURITY.md absent", "dependency lock present" if has_lock else "lock absent"],
             ([] if has_security else ["document security boundary"]) + ([] if has_lock else ["lock dependencies"])),
        axis("semantic_placement", 4.8 + 4.3 * resolved_strength - 1.6 * interface_penalty - overloaded * .4,
             [f"mean role fit={resolved_strength:.3f}", f"mean interface cost={interface_penalty:.3f}"],
             ["reduce language overload and place each boundary with measured fit"] if resolved_strength < .86 else []),
        axis("interfaces", 5.2 + (1.2 if any(row.language == "protobuf" for row in files) else 0)
             + min(1.8, role_count * .18) - 1.4 * interface_penalty,
             [f"mean interface cost={interface_penalty:.3f}"],
             ["make cross-language contracts explicit"] if len({row.language for row in files if row.language}) > 1 else []),
        axis("maintainability", 5.6 + (1.0 if has_arch else 0) + (1.0 if has_readme else 0) + .8 * resolved_strength - overloaded * .35,
             ["README present" if has_readme else "README absent", "architecture present" if has_arch else "architecture absent"],
             [] if has_arch else ["document why each language owns its boundary"]),
        axis("observability", 4.8 + (2.5 if has_observability else 0) + (.9 if has_ci else 0),
             ["observability evidence present" if has_observability else "observability surface absent"],
             [] if has_observability else ["add structured metrics/receipts/diagnostics"]),
        axis("operability", 5.2 + (1.7 if has_ci else 0) + (1.0 if has_readme else 0) + .6 * resolved_strength,
             ["CI present" if has_ci else "CI absent"], [] if has_ci else ["make verification reproducible"]),
        axis("evidence", 4.8 + (1.7 if tests else 0) + (1.4 if has_ci else 0)
             + (1.0 if any(".integrity/" in f"/{row.path}" for row in files) else 0),
             ["tests present" if tests else "tests absent", "CI present" if has_ci else "CI absent"],
             [] if tests and has_ci else ["strengthen executable proof"]),
    )


def _fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in _safe_files(root):
        rel = path.relative_to(root)
        try:
            stat = path.stat()
        except OSError:
            continue
        digest.update(rel.as_posix().encode())
        digest.update(str(stat.st_size).encode())
        digest.update(str(stat.st_mtime_ns).encode())
    return digest.hexdigest()


def evaluate_repository(
    root: Path | str,
    registry: TowerRegistry,
    *,
    target: float = DEFAULT_TARGET,
) -> RepoEvaluation:
    repo = Path(root).resolve()
    if not repo.is_dir():
        raise ValueError(f"repository not found: {repo}")
    files = classify_files(repo)
    roles = resolve_roles(registry, files)
    quality = _quality(repo, files, roles)
    total_weight = sum(axis.weight for axis in quality)
    overall = round(sum(axis.score * axis.weight for axis in quality) / total_weight, 3)
    critical_floor = round(min(
        axis.score for axis in quality if axis.name in CRITICAL_QUALITY
    ), 3)
    complete = overall >= target and critical_floor >= 8.5
    return RepoEvaluation(
        schema=SCHEMA,
        repository=repo.name,
        files=files,
        roles=roles,
        quality=quality,
        overall_score=overall,
        critical_floor=critical_floor,
        target=target,
        complete=complete,
        fingerprint=_fingerprint(repo),
    )


def _impact_for(role: RoleResolution, current_score: float) -> Impact:
    selected = role.selected
    current_fit = max(
        (row.score for row in role.alternatives if row.language in role.current_languages),
        default=0.0,
    )
    fit_gain = max(0.0, selected.score - current_fit)
    introduce = selected.language not in role.current_languages
    return Impact(
        near_term=round(.48 + .30 * fit_gain, 3),
        far_term=round(.58 + .38 * fit_gain, 3),
        capability_gain=round(.45 + .50 * selected.score, 3),
        stability_gain=round(.42 + .50 * selected.score, 3),
        reversibility=.88 if "EXPERIMENT" in role.recommendation else .76,
        risk=.24 + (.20 if introduce else .05),
        effort=.28 + (.28 if introduce else .08),
        complexity_delta=.12 + (.28 if introduce else 0.0) + role.interface_cost * .25,
    )


def plan_interventions(evaluation: RepoEvaluation, *, limit: int = 10) -> tuple[Intervention, ...]:
    rows: list[Intervention] = []
    quality_map = {axis.name: axis for axis in evaluation.quality}

    for role in evaluation.roles:
        impact = _impact_for(role, evaluation.overall_score)
        current_best = max(
            (row.score for row in role.alternatives if row.language in role.current_languages),
            default=0.0,
        )
        gain = max(0.0, role.selected.score - current_best)
        if "PRESERVE" in role.recommendation and gain < .05:
            continue
        priority = (
            1.4 * role.demand + 1.2 * gain + impact.net
            + max(0.0, 9.0 - quality_map["semantic_placement"].score) * .08
        )
        rows.append(Intervention(
            intervention_id=f"role:{role.role}:{role.selected.language}",
            title=role.recommendation,
            role=role.role,
            language=role.selected.language,
            reason=(
                f"{role.role} demand={role.demand:.2f}; selected fit={role.selected.score:.2f}; "
                f"current-best={current_best:.2f}; evaluate capability + stability together"
            ),
            impact=impact,
            priority=round(priority, 6),
            completion_signal=(
                "role-fit and total quality rise after re-evaluation; no critical quality axis "
                "drops by more than 0.5 and interface cost remains below realized gain"
            ),
        ))

    for axis in evaluation.quality:
        if axis.score >= 9.0 or not axis.gaps:
            continue
        impact = Impact(
            near_term=.62, far_term=.72,
            capability_gain=.55 if axis.name not in {"testing", "evidence"} else .48,
            stability_gain=.78 if axis.name in {"correctness", "testing", "security", "interfaces"} else .58,
            reversibility=.92, risk=.16, effort=.30, complexity_delta=.08,
        )
        rows.append(Intervention(
            intervention_id=f"quality:{axis.name}",
            title=axis.gaps[0],
            role=None,
            language=None,
            reason=f"{axis.name}={axis.score:.2f}; quality debt blocks balanced 9+ completion",
            impact=impact,
            priority=round((10.0-axis.score)*axis.weight + impact.net, 6),
            completion_signal=f"{axis.name} increases with no critical-axis regression",
        ))

    return tuple(sorted(rows, key=lambda row: (-row.priority, row.intervention_id))[:limit])


class BabelSpiralEngine:
    """Repeatedly evaluate → choose → execute → re-evaluate the actual repository."""

    def __init__(
        self,
        registry: TowerRegistry,
        *,
        target: float = DEFAULT_TARGET,
        max_revolutions: int = 12,
        stagnation_limit: int = 2,
    ) -> None:
        if not 0 < target <= 10:
            raise ValueError("target must be within (0, 10]")
        if max_revolutions < 1:
            raise ValueError("max_revolutions must be positive")
        self.registry = registry
        self.target = target
        self.max_revolutions = max_revolutions
        self.stagnation_limit = max(1, stagnation_limit)

    def run(self, root: Path | str, executor: Executor | None = None) -> dict[str, Any]:
        repo = Path(root).resolve()
        current = evaluate_repository(repo, self.registry, target=self.target)
        history: list[Revolution] = []
        stagnant = 0

        for number in range(1, self.max_revolutions + 1):
            if current.complete:
                history.append(Revolution(number, current.overall_score, current.overall_score, None, "COMPLETE"))
                break
            plan = plan_interventions(current)
            if not plan:
                history.append(Revolution(number, current.overall_score, current.overall_score, None, "CONSTRAINED"))
                break
            selected = plan[0]
            if executor is None:
                history.append(Revolution(number, current.overall_score, current.overall_score, selected, "ACTION_REQUIRED"))
                break

            before = current
            if not executor(selected, repo):
                history.append(Revolution(number, before.overall_score, before.overall_score, selected, "EXECUTOR_DECLINED"))
                break
            after = evaluate_repository(repo, self.registry, target=self.target)

            before_axes = {axis.name: axis.score for axis in before.quality}
            after_axes = {axis.name: axis.score for axis in after.quality}
            regressions = [
                name for name in CRITICAL_QUALITY
                if after_axes.get(name, 0.0) < before_axes.get(name, 0.0) - .5
            ]
            if after.fingerprint == before.fingerprint or after.overall_score <= before.overall_score:
                stagnant += 1
            else:
                stagnant = 0

            if regressions:
                status = "REGRESSION_DETECTED"
            elif after.overall_score > before.overall_score:
                status = "IMPROVED"
            else:
                status = "REVISE"
            history.append(Revolution(number, before.overall_score, after.overall_score, selected, status))
            current = after

            if regressions or stagnant >= self.stagnation_limit:
                break

        return {
            "schema": SCHEMA,
            "repository": current.repository,
            "target": self.target,
            "complete": current.complete,
            "final_score": current.overall_score,
            "critical_floor": current.critical_floor,
            "evaluation": asdict(current),
            "next_interventions": [asdict(row) for row in plan_interventions(current)],
            "revolutions": [asdict(row) for row in history],
        }


def write_report(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")

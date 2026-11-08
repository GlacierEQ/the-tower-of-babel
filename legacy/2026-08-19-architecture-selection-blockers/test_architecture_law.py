from tower.architecture import (
    BoundaryObjective,
    LanguageLane,
    TechnologyCandidate,
    architecture_is_valid,
    optimize_architecture,
    select_best_technology,
    validate_lane_against_candidates,
    validate_lanes,
)


def lane(lane_id: str, concern: str, language: str) -> LanguageLane:
    return LanguageLane(
        lane_id=lane_id,
        concern=concern,
        language=language,
        rationale=f"{language} is selected because it has measurable fitness for {concern}",
        interface="versioned schema/ABI",
        proof="native test + runtime receipt",
    )


def tech(language: str, boundary: str, **fitness: float) -> TechnologyCandidate:
    return TechnologyCandidate(
        language=language,
        boundary=boundary,
        evidence=f"benchmark receipt for {language} on {boundary}",
        fitness=fitness,
        evidence_confidence=0.95,
        interoperability_cost=0.2,
        migration_cost=0.3,
    )


def test_six_language_repository_is_valid_when_lanes_are_explicit():
    lanes = [
        lane("kernel", "kernel_runtime", "Rust"),
        lane("memory", "durable_memory", "SQL"),
        lane("gpu", "accelerator_kernel", "Triton"),
        lane("control", "control_plane", "TypeScript"),
        lane("analysis", "numerical_science", "Julia"),
        lane("formal", "formal_verification", "Lean"),
    ]
    assert architecture_is_valid(lanes)


def test_duplicate_concern_owner_is_invalid():
    lanes = [
        lane("memory-a", "durable_memory", "SQL"),
        lane("memory-b", "durable_memory", "Python"),
    ]
    assert any("duplicate concern owner" in item for item in validate_lanes(lanes))


def test_empty_architecture_is_not_valid():
    assert architecture_is_valid([]) is False


def test_boundary_optimizer_selects_highest_fitness_not_default_language():
    candidates = [
        tech(
            "Python",
            "kernel_runtime",
            performance=0.35,
            memory_safety=0.55,
            determinism=0.5,
            concurrency=0.4,
            memory_density=0.4,
            portability=0.8,
            ecosystem=0.95,
            operability=0.9,
        ),
        tech(
            "Rust",
            "kernel_runtime",
            performance=0.95,
            memory_safety=0.95,
            determinism=0.9,
            concurrency=0.9,
            memory_density=0.9,
            portability=0.85,
            ecosystem=0.8,
            formal_verifiability=0.75,
            operability=0.8,
        ),
    ]
    selection = select_best_technology(candidates)
    assert selection.selected is not None
    assert selection.selected.candidate.language == "Rust"


def test_lane_validation_rejects_materially_inferior_language():
    declared = lane("kernel", "kernel_runtime", "Python")
    candidates = [
        tech(
            "Python",
            "kernel_runtime",
            performance=0.3,
            memory_safety=0.5,
            ecosystem=0.95,
        ),
        tech(
            "Rust",
            "kernel_runtime",
            performance=0.95,
            memory_safety=0.98,
            determinism=0.9,
            concurrency=0.9,
            memory_density=0.9,
            portability=0.85,
            formal_verifiability=0.8,
            ecosystem=0.8,
            operability=0.8,
        ),
    ]
    errors = validate_lane_against_candidates(declared, candidates)
    assert any("inferior language placement" in error for error in errors)


def test_architecture_optimizer_diversifies_when_different_languages_win():
    selections = optimize_architecture(
        {
            "control_plane": [
                tech(
                    "TypeScript",
                    "control_plane",
                    performance=0.75,
                    memory_safety=0.8,
                    determinism=0.9,
                    concurrency=0.95,
                    memory_density=0.7,
                    portability=1.0,
                    ecosystem=1.0,
                    operability=1.0,
                ),
                tech(
                    "Rust",
                    "control_plane",
                    performance=0.85,
                    memory_safety=0.95,
                    determinism=0.8,
                    concurrency=0.8,
                    memory_density=0.8,
                    portability=0.65,
                    formal_verifiability=0.45,
                    ecosystem=0.55,
                    operability=0.45,
                ),
            ],
            "accelerator_kernel": [
                tech(
                    "Triton",
                    "accelerator_kernel",
                    performance=0.95,
                    accelerator_access=1.0,
                    ecosystem=0.8,
                    operability=0.75,
                ),
                tech(
                    "TypeScript",
                    "accelerator_kernel",
                    performance=0.15,
                    accelerator_access=0.05,
                    ecosystem=0.95,
                    operability=0.9,
                ),
            ],
        }
    )
    assert selections["control_plane"].selected.candidate.language == "TypeScript"
    assert selections["accelerator_kernel"].selected.candidate.language == "Triton"


def test_policy_rejects_interface_cost_as_dominant_objective():
    try:
        BoundaryObjective(
            interoperability_penalty=0.3, migration_penalty=0.25
        ).validate()
    except ValueError as exc:
        assert "must not dominate" in str(exc)
    else:
        raise AssertionError("cost-dominant boundary policy must be rejected")

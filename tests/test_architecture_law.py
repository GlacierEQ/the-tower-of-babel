from tower.architecture import LanguageLane, architecture_is_valid, validate_lanes


def lane(lane_id: str, concern: str, language: str) -> LanguageLane:
    return LanguageLane(
        lane_id=lane_id,
        concern=concern,
        language=language,
        rationale=f"{language} is selected because it has measurable fitness for {concern}",
        interface="versioned schema/ABI",
        proof="native test + runtime receipt",
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

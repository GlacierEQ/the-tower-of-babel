from tower.capability_resolution import (
    BoundaryObjective,
    LanguageLane,
    TechnologyCandidate,
    rank_technology,
    resolve_architecture,
    resolve_lane_against_candidates,
    resolve_technology,
)


def lane(lane_id: str, concern: str, language: str) -> LanguageLane:
    return LanguageLane(
        lane_id=lane_id,
        concern=concern,
        language=language,
        rationale=f"{language} is active for the {concern} boundary with visible comparison evidence",
        interface="versioned schema/ABI",
        proof="native test plus runtime receipt",
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


def test_low_evidence_candidate_remains_ranked_with_resolution_work():
    candidate = TechnologyCandidate(
        language="Python",
        boundary="kernel_runtime",
        evidence="early benchmark",
        fitness={"performance": 0.7},
        evidence_confidence=0.2,
    )

    ranked = rank_technology(candidate)

    assert ranked.continuation == "enabled"
    assert "expand_evidence_confidence" in ranked.resolution_work


def test_experimental_candidate_continues_with_reversibility_work():
    candidate = TechnologyCandidate(
        language="Triton",
        boundary="accelerator_kernel",
        evidence="prototype receipt",
        fitness={"performance": 0.95, "accelerator_access": 1.0},
        experimental=True,
        reversible=False,
    )

    ranked = rank_technology(candidate)

    assert ranked.continuation == "enabled"
    assert "design_reversible_experiment_path" in ranked.resolution_work


def test_resolver_selects_strongest_available_and_preserves_all_candidates():
    resolution = resolve_technology(
        [
            tech("Python", "kernel_runtime", performance=0.3, ecosystem=0.95),
            tech("Rust", "kernel_runtime", performance=0.95, memory_safety=0.95),
        ]
    )

    assert resolution.continuation == "enabled"
    assert resolution.decision == "selected_strongest_available_capability"
    assert resolution.selected is not None
    assert resolution.selected.candidate.language == "Rust"
    assert [item.candidate.language for item in resolution.ranked] == ["Rust", "Python"]


def test_lane_difference_becomes_review_work_without_rejecting_lane():
    declared = lane("kernel", "kernel_runtime", "Python")
    candidates = [
        tech("Python", "kernel_runtime", performance=0.3, ecosystem=0.95),
        tech("Rust", "kernel_runtime", performance=0.95, memory_safety=0.98),
    ]

    resolution = resolve_lane_against_candidates(declared, candidates)

    assert resolution.continuation == "enabled"
    assert any(item.startswith("review_stronger_alternative:Rust") for item in resolution.resolution_work)


def test_empty_boundary_remains_visible_resolution_work():
    resolutions = resolve_architecture({"future_boundary": []}, {"future_boundary": BoundaryObjective()})

    assert resolutions["future_boundary"].continuation == "enabled"
    assert resolutions["future_boundary"].selected is None
    assert "supply_capability_candidates" in resolutions["future_boundary"].resolution_work

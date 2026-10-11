"""Megamind compatibility adapter for the canonical Tower selector.

Technology selection belongs to the Tower core. Megamind is a consumer of that
authority, not the owner of it. Existing imports remain supported here so external
callers do not break while the canonical implementation lives in ``tower.selector``.
"""
from tower.selector import TechnologyRequest, select_technologies

__all__ = ["TechnologyRequest", "select_technologies"]

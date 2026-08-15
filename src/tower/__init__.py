"""The Tower of Babel governance, activation, and execution package."""

from .activation import ActivationDecision, ActivationMode, activation_surface, resolve_activation

__version__ = "1.2.0"

__all__ = [
    "ActivationDecision",
    "ActivationMode",
    "activation_surface",
    "resolve_activation",
]

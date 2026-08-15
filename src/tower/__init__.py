"""The Tower of Babel governance, activation, and execution package."""

from .activation import (
    ActivationDecision,
    ActivationMode,
    activate_execution,
    activation_surface,
    resolve_activation,
)

__version__ = "1.2.1"

__all__ = [
    "ActivationDecision",
    "ActivationMode",
    "activate_execution",
    "activation_surface",
    "resolve_activation",
]

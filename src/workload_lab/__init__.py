"""Experimental framework-neutral workload analysis library."""

from .analysis import analyze
from .graph import compile_workload
from .ingest import ingest
from .ir import SCHEMA_VERSION, ValidationError


def __getattr__(name):
    # Preserve the V2 API without loading a simulator for V3 inspection/validation.
    if name in ("Arrival", "PoolSpec", "Scenario", "Task", "simulate"):
        from . import simulation

        return getattr(simulation, name)
    raise AttributeError(name)


__all__ = [
    "SCHEMA_VERSION",
    "ValidationError",
    "analyze",
    "compile_workload",
    "ingest",
    "Arrival",
    "PoolSpec",
    "Scenario",
    "Task",
    "simulate",
]

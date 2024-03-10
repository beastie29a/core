"""Models based off https://apiclient.home-connect.com/hcsdk.yaml."""
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Constraints:  # noqa: D101
    min: Optional[int] = None
    max: Optional[int] = None
    stepsize: Optional[int] = None
    allowedvalues: list[str] = field(default_factory=list)
    displayvalues: Optional[list[str]] = None
    default: Optional[dict[str, Any]] = None


@dataclass
class StatusConstraints(Constraints):
    """Constraints of the status, e.g. step size, enumeration values, etc."""

    access: Optional[str] = None


@dataclass
class Option:  # noqa: D101
    key: str
    value: dict[str, Any]
    constraints: StatusConstraints = field(default_factory=StatusConstraints)
    name: Optional[str] = None
    displayvalue: Optional[str] = None
    unit: Optional[str] = None

    def __post_init__(self):
        """Reassign constraints from dict to StatusConstraints."""
        if isinstance(self.constraints, dict):
            self.constraints = StatusConstraints(**self.constraints)


@dataclass
class StatusData(Option):  # noqa: D101
    type: Optional[str] = None


@dataclass
class Status:  # noqa: D101
    data: StatusData

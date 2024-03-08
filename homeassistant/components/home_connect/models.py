"""Models based off https://apiclient.home-connect.com/hcsdk.yaml."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Constraints:  # noqa: D101
    min: int | None = None
    max: int | None = None
    stepsize: int | None = None
    allowedvalues: list[str] = field(default_factory=list)
    displayvalues: list[str] | None = None
    default: dict[str, Any] | None = None


@dataclass
class StatusConstraints(Constraints):
    """Constraints of the status, e.g. step size, enumeration values, etc."""

    access: str | None = None

    def get(self, key: str) -> Any:
        """Create dict attribute to resolve type issue."""
        return getattr(self, key)


@dataclass
class Option:  # noqa: D101
    key: str
    value: dict[str, Any]
    constraints: StatusConstraints = field(default_factory=StatusConstraints)
    name: str | None = None
    displayvalue: str | None = None
    unit: str | None = None


@dataclass
class StatusData(Option):  # noqa: D101
    type: str | None = None
    # constraints: Optional[StatusConstraints] = None


@dataclass
class Status:  # noqa: D101
    data: StatusData

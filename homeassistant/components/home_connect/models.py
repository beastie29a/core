"""Models based off https://apiclient.home-connect.com/hcsdk.yaml."""

from collections.abc import Mapping
from dataclasses import InitVar, dataclass, field
from typing import Any


@dataclass
class StatusConstraints:
    """Constraints of the status, e.g. step size, enumeration values, etc."""

    access: str | None = None
    min: int | None = None
    max: int | None = None
    stepsize: int | None = None
    allowedvalues: list[str] = field(default_factory=list)
    displayvalues: list[str] | None = None
    default: dict[str, Any] | None = None

    # Aliases from Home Assistant variables
    step: InitVar[int] = None
    options: InitVar[list[str]] = None

    # Other HA attributes not used
    mode: str | None = None
    supported_color_modes: Any | None = None

    def __post_init__(self, step: int | None, options: list[str] | None) -> None:
        """Alias for stepsize class attribute."""
        if step is not None:
            self.stepsize = step
        if options is not None:
            self.allowedvalues = options


@dataclass
class StatusData:  # noqa: D101
    key: str
    value: str | int | float | bool
    type: str | None = None
    constraints: StatusConstraints | Mapping[str, Any] | None = field(
        default_factory=StatusConstraints
    )
    name: str | None = None
    displayvalue: str | None = None
    unit: str | None = None

    def __post_init__(self):
        """Reassign constraints from dict to StatusConstraints."""
        if isinstance(self.constraints, dict):
            self.constraints = StatusConstraints(**self.constraints)

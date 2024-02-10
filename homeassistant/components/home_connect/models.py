"""Models based off https://apiclient.home-connect.com/hcsdk.yaml."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Constraints:  # noqa: D101
    min: Optional[int] = None
    max: Optional[int] = None
    stepsize: Optional[int] = None
    allowedvalues: Optional[list[str]] = None
    displayvalues: Optional[list[str]] = None
    default: Optional[dict[str, Any]] = None


@dataclass
class Option:  # noqa: D101
    key: str
    value: dict[str, Any]
    name: Optional[str] = None
    displayvalue: Optional[str] = None
    unit: Optional[str] = None


@dataclass
class SettingConstraints(Constraints):
    """Constraints of the setting, e.g. step size, enumeration values, etc."""

    access: Optional[str] = None


@dataclass
class SettingData(Option):  # noqa: D101
    type: Optional[str] = None
    constraints: Optional[SettingConstraints] = None


@dataclass
class GetSetting:
    """Specific setting of the home appliance."""

    data: SettingData


@dataclass
class ProgramDefinitionDataOptionConstraints(Constraints):  # noqa: D101
    liveupdate: Optional[bool] = None


@dataclass
class ProgramDefinitionDataOption:  # noqa: D101
    key: str
    type: str
    name: Optional[str] = None
    unit: Optional[str] = None
    constraints: Optional[ProgramDefinitionDataOptionConstraints] = None


@dataclass
class ProgramDefinitionData:  # noqa: D101
    key: str
    name: Optional[str] = None
    options: Optional[list[ProgramDefinitionDataOption]] = None


@dataclass
class ProgramDefinition:  # noqa: D101
    """Specific definition of the appliance available program."""

    data: ProgramDefinitionData


@dataclass
class ArrayOfSettingData:  # noqa: D101
    settings: list[Option]


@dataclass
class ArrayOfSettings:
    """List of settings of the home appliance."""

    data: ArrayOfSettingData


@dataclass
class StatusConstraints(Constraints):
    """Constraints of the status, e.g. step size, enumeration values, etc."""

    access: Optional[str] = None


@dataclass
class StatusData(Option):  # noqa: D101
    type: Optional[str] = None
    constraints: Optional[StatusConstraints] = None


@dataclass
class Status:  # noqa: D101
    data: StatusData


@dataclass
class StatusItem(Option):  # noqa: D101
    pass


@dataclass
class ArrayOfStatusData:  # noqa: D101
    status: list[StatusItem]


@dataclass
class ArrayOfStatus:
    """List of status of the home appliance."""

    data: ArrayOfStatusData


@dataclass
class Program:  # noqa: D101
    key: str
    name: Optional[str] = None
    constraints: Optional[Constraints] = None


@dataclass
class ArrayOfAvailableProgramsData:  # noqa: D101
    programs: list[Program]


@dataclass
class ArrayOfAvailablePrograms:
    """List of available programs of the home appliance."""

    data: ArrayOfAvailableProgramsData

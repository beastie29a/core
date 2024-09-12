"""Provides a setting selector for Home Connect."""

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeconnect.api import HomeConnectAppliance, HomeConnectError

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ConfigEntryAuth, HomeConnectDevice
from .const import (
    DOMAIN,
    REFRIGERATION_ECO_MODE,
    REFRIGERATION_FRESH_MODE,
    REFRIGERATION_SABBATH_MODE,
    REFRIGERATION_VACATION_MODE,
)
from .entity import HomeConnectEntity

_LOGGER = logging.getLogger(__name__)

REFRIGERATION_MODES = {
    REFRIGERATION_ECO_MODE,
    REFRIGERATION_FRESH_MODE,
    REFRIGERATION_SABBATH_MODE,
    REFRIGERATION_VACATION_MODE,
}


@dataclass(frozen=True)
class HomeConnectSelectEntityDescription(SelectEntityDescription):
    """Home Connect Select Entity Description."""

    option_prefix: str | None = "Refrigeration.Common.Setting"
    value_fn: Callable[[dict], str | None] = lambda status: next(
        (
            mode.rsplit(".", maxsplit=1)[-1]
            for mode in REFRIGERATION_MODES
            if status.get(mode, {}).get("value")
        ),
        None,
    )
    exists_fn: Callable[[HomeConnectAppliance], bool] = (
        lambda appliance: appliance.type in ("FridgeFreezer", "Refrigerator", "Freezer")
    )


SELECTS: tuple[HomeConnectSelectEntityDescription, ...] = (
    HomeConnectSelectEntityDescription(
        key="Refrigeration Modes",
        options=[mode.rsplit(".", maxsplit=1)[-1] for mode in REFRIGERATION_MODES],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Home Connect switch."""

    def get_entities():
        """Get a list of entities."""
        entities = []
        hc_api: ConfigEntryAuth = hass.data[DOMAIN][config_entry.entry_id]
        entities += [
            HomeConnectSelect(
                device=device_dict[CONF_DEVICE], entity_description=description
            )
            for device_dict in hc_api.devices
            for description in SELECTS
            if description.exists_fn(device_dict[CONF_DEVICE].appliance)
        ]
        return entities

    async_add_entities(await hass.async_add_executor_job(get_entities), True)


class HomeConnectSelect(HomeConnectEntity, SelectEntity):
    """Generic select class for Home Connect Settings."""

    def __init__(
        self,
        device: HomeConnectDevice,
        entity_description: HomeConnectSelectEntityDescription,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: HomeConnectSelectEntityDescription = entity_description
        super().__init__(device, self.entity_description.key)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug("Switching mode on: %s, to %s", self.name, option)
        try:
            await self.hass.async_add_executor_job(
                self.device.appliance.set_setting,
                f"{self.entity_description.option_prefix}.{option}",
                True,
            )
        except HomeConnectError as err:
            _LOGGER.error("Error while trying to set mode: %s", err)
            return

    async def async_update(self) -> None:
        """Update the select status."""
        self.current_option = self.entity_description.value_fn(
            self.device.appliance.status
        )
        _LOGGER.debug(
            "Updated: %s, new state: %s",
            self._attr_unique_id,
            self.current_option,
        )

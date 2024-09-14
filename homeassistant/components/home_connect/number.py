"""Provides a number setting for Home Connect."""

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeconnect.api import HomeConnectError

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ConfigEntryAuth, HomeConnectDevice
from .const import (
    ATTR_VALUE,
    BSH_TEMPERATURE_UNIT_CELSIUS,
    BSH_TEMPERATURE_UNIT_FAHRENHEIT,
    DOMAIN,
    REFRIGERATION_BOTTLECOOLER_SETPOINTTEMPERATURE,
    REFRIGERATION_CHILLERCOMMON_SETPOINTTEMPERATURE,
    REFRIGERATION_CHILLERLEFT_SETPOINTTEMPERATURE,
    REFRIGERATION_CHILLERRIGHT_SETPOINTTEMPERATURE,
    REFRIGERATION_SETPOINTTEMPERATUREFREEZER,
    REFRIGERATION_SETPOINTTEMPERATUREREFRIGERATOR,
    REFRIGERATION_WINECOMPARTMENT_SETPOINTTEMPERATURE,
)
from .coordinator import HomeConnectDataUpdateCoordinator
from .entity import HomeConnectEntity

_LOGGER = logging.getLogger(__name__)

TEMPERATURE_UNIT_MAP = {
    BSH_TEMPERATURE_UNIT_CELSIUS: UnitOfTemperature.CELSIUS,
    BSH_TEMPERATURE_UNIT_FAHRENHEIT: UnitOfTemperature.FAHRENHEIT,
}


@dataclass(frozen=True, kw_only=True)
class HomeConnectNumberEntityDescription(NumberEntityDescription):
    """Home Connect Number Entity Description."""

    setting_key: str
    device_class: NumberDeviceClass = NumberDeviceClass.TEMPERATURE
    native_min_value: float = -24
    native_max_value: float = -16
    exists_fn: Callable[[str, dict], bool] = (
        lambda setting_key, status: setting_key in status
    )

    value_fn: Callable[[str, dict], float | None] = (
        lambda setting_key, status: status.get(setting_key, {}).get(ATTR_VALUE)
    )
    cache_props: bool = True


NUMBERS: tuple[HomeConnectNumberEntityDescription, ...] = (
    HomeConnectNumberEntityDescription(
        key="Chiller Left Temperature",
        setting_key=REFRIGERATION_CHILLERLEFT_SETPOINTTEMPERATURE,
    ),
    HomeConnectNumberEntityDescription(
        key="Chiller Common Temperature",
        setting_key=REFRIGERATION_CHILLERCOMMON_SETPOINTTEMPERATURE,
    ),
    HomeConnectNumberEntityDescription(
        key="Chiller Right Temperature",
        setting_key=REFRIGERATION_CHILLERRIGHT_SETPOINTTEMPERATURE,
    ),
    HomeConnectNumberEntityDescription(
        key="Refrigerator Temperature",
        setting_key=REFRIGERATION_SETPOINTTEMPERATUREREFRIGERATOR,
    ),
    HomeConnectNumberEntityDescription(
        key="Freezer Temperature",
        setting_key=REFRIGERATION_SETPOINTTEMPERATUREFREEZER,
    ),
    HomeConnectNumberEntityDescription(
        key="Bottle Cooler Temperature",
        setting_key=REFRIGERATION_BOTTLECOOLER_SETPOINTTEMPERATURE,
    ),
    HomeConnectNumberEntityDescription(
        key="Wine Compartment Temperature",
        setting_key=REFRIGERATION_WINECOMPARTMENT_SETPOINTTEMPERATURE,
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
        coordinator: HomeConnectDataUpdateCoordinator = config_entry.runtime_data
        entities.extend(
            HomeConnectNumber(
                device=device_dict[CONF_DEVICE],
                coordinator=coordinator.init_entity(
                    device=device_dict[CONF_DEVICE],
                    entity_unique_id=f"{device_dict[CONF_DEVICE].appliance.haId}-{description.key}",
                    endpoint=f"/settings/{description.setting_key}",
                ),
                entity_description=description,
            )
            for device_dict in hc_api.devices
            for description in NUMBERS
            if description.exists_fn(
                description.setting_key, device_dict[CONF_DEVICE].appliance.status
            )
        )
        return entities

    async_add_entities(await hass.async_add_executor_job(get_entities), True)


class HomeConnectNumber(HomeConnectEntity, NumberEntity):
    """Generic number class for Home Connect Settings."""

    entity_description: HomeConnectNumberEntityDescription

    def __init__(
        self,
        device: HomeConnectDevice,
        entity_description: HomeConnectNumberEntityDescription,
        coordinator: HomeConnectDataUpdateCoordinator,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: HomeConnectNumberEntityDescription = entity_description
        super().__init__(
            device=device, desc=self.entity_description.key, coordinator=coordinator
        )
        self._attr_min_value = coordinator.data[self.device.device_id][
            self.unique_id
        ].constraints.min
        self._attr_max_value = coordinator.data[self.device.device_id][
            self.unique_id
        ].constraints.max
        self._attr_step = coordinator.data[self.device.device_id][
            self.unique_id
        ].constraints.stepsize
        self.native_unit_of_measurement = coordinator.data[self.device.device_id][
            self.unique_id
        ].unit

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        _LOGGER.debug("Setting %s to %s", self.entity_description.setting_key, value)
        try:
            await self.hass.async_add_executor_job(
                self.device.appliance.set_setting,
                self.entity_description.setting_key,
                value,
            )
        except HomeConnectError as err:
            _LOGGER.error("Error while trying to change setting: %s", err)
            self._attr_available = False
            return
        else:
            self._attr_available = True
            self.async_entity_update()

    async def async_update(self) -> None:
        """Update the setting's status."""

        self.native_value = self.entity_description.value_fn(
            self.entity_description.setting_key, self.device.appliance.status
        )
        self._attr_available = True
        _LOGGER.debug(
            "Updated %s, new setting: %s",
            self.device.appliance.set_setting,
            self.native_value,
        )

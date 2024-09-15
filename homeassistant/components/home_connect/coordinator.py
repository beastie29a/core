"""Home Connect DataCoordinator implementation."""

import asyncio
import logging
from typing import Self

from requests import HTTPError

from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ConfigEntryAuth, HomeConnectDevice
from .const import DOMAIN
from .exceptions import HomeConnectAPIException, HomeConnectAuthException
from .models import StatusData

_LOGGER = logging.getLogger(__name__)


class HomeConnectDataUpdateCoordinator(DataUpdateCoordinator):
    """Home Connect coordinator."""

    def __init__(self, hass: HomeAssistant, hc_api: ConfigEntryAuth) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Home Connect",
            always_update=False,
        )
        self.hc_api = hc_api
        self.entity_cache: dict[str, dict] = {}

    async def _async_setup(self) -> None:
        """Fetch necessary parameters for platforms from the Home Connect API."""

        try:
            device_registry: dr.DeviceRegistry = dr.async_get(self.hass)
            await self.hass.async_add_executor_job(self.hc_api.get_devices)
            for device_dict in self.hc_api.devices:
                device: HomeConnectDevice = device_dict[CONF_DEVICE]

                device_entry: dr.DeviceEntry = device_registry.async_get_or_create(
                    config_entry_id=self.hc_api.config_entry.entry_id,
                    identifiers={(DOMAIN, device.appliance.haId)},
                    name=device.appliance.name,
                    manufacturer=device.appliance.brand,
                    model=device.appliance.vib,
                )

                device.device_id = device_entry.id

        except HTTPError as err:
            _LOGGER.warning("Cannot update devices: %s", err.response.status_code)

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""

        entity_cache = {}
        try:
            async with asyncio.timeout(600):
                for device_dict in self.hc_api.devices:
                    device: HomeConnectDevice = device_dict[CONF_DEVICE]
                    await self.hass.async_add_executor_job(device.initialize)
                    entity_registry = er.async_get(self.hass)
                    entities: list[er.RegistryEntry] = er.async_entries_for_device(
                        registry=entity_registry,
                        device_id=device.device_id,
                    )
                    # Store cached entity_regitry data to lessen the amount of API calls.
                    entity_cache[device.device_id] = {
                        entity.unique_id: StatusData(
                            key="",
                            value="",
                            unit=entity.unit_of_measurement,
                            constraints=entity.capabilities,
                        )
                        for entity in entities
                    }
                    print(entity_cache)
        except HomeConnectAuthException as err:
            raise ConfigEntryAuthFailed from err
        except HomeConnectAPIException as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        else:
            return entity_cache

    def init_entity(
        self, device: HomeConnectDevice, entity_unique_id: str, endpoint: str
    ) -> Self:
        """Initialize the entity when it is first created."""
        entity_entry = self.data.get(device.device_id, {}).get(entity_unique_id)
        if entity_entry is not None:
            print(entity_entry)
            _LOGGER.debug(
                "Entity cache entry found, will not make API call to: %s", endpoint
            )
            return self
        try:
            print(endpoint)
            self.data[device.device_id][entity_unique_id] = StatusData(
                **device.appliance.get(endpoint)
            )
            _LOGGER.debug(
                "Initialized cached entry: %s with data: %s",
                entity_unique_id,
                self.data[device.device_id][entity_unique_id],
            )
        except HomeConnectAPIException as err:
            _LOGGER.error(
                "Error fetching StatusData for: %s, %s", entity_unique_id, err
            )

        return self

"""API for Home Connect bound to HASS OAuth."""

from asyncio import run_coroutine_threadsafe
import logging
from typing import Any

import homeconnect
from homeconnect.api import HomeConnectAppliance, HomeConnectError

from homeassistant import config_entries, core
from homeassistant.const import CONF_DEVICE, CONF_ENTITIES
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.dispatcher import dispatcher_send

from .const import (
    API_ENDPOINT,
    ATTR_AMBIENT,
    ATTR_DESC,
    ATTR_DEVICE,
    ATTR_KEY,
    ATTR_VALUE,
    BSH_ACTIVE_PROGRAM,
    BSH_POWER_OFF,
    BSH_POWER_STANDBY,
    SIGNAL_UPDATE_ENTITIES,
)

_LOGGER = logging.getLogger(__name__)


class ConfigEntryAuth(homeconnect.HomeConnectAPI):
    """Provide Home Connect authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        hass: core.HomeAssistant,
        config_entry: config_entries.ConfigEntry,
        implementation: config_entry_oauth2_flow.AbstractOAuth2Implementation,
    ) -> None:
        """Initialize Home Connect Auth."""
        self.hass = hass
        self.config_entry = config_entry
        self.session = config_entry_oauth2_flow.OAuth2Session(
            hass, config_entry, implementation
        )
        super().__init__(self.session.token, api_url=API_ENDPOINT)
        self.devices: list[dict[str, Any]] = []

    def refresh_tokens(self) -> dict:
        """Refresh and return new Home Connect tokens using Home Assistant OAuth2 session."""
        run_coroutine_threadsafe(
            self.session.async_ensure_token_valid(), self.hass.loop
        ).result()

        return self.session.token

    def get_devices(self):
        """Get a dictionary of devices."""
        appl = self.get_appliances()
        devices = []
        for app in appl:
            if app.type == "Dryer":
                device = Dryer(self.hass, app)
            elif app.type == "Washer":
                device = Washer(self.hass, app)
            elif app.type == "WasherDryer":
                device = WasherDryer(self.hass, app)
            elif app.type == "Dishwasher":
                device = Dishwasher(self.hass, app)
            elif app.type == "FridgeFreezer":
                device = FridgeFreezer(self.hass, app)
            elif app.type == "Refrigerator":
                device = Refrigerator(self.hass, app)
            elif app.type == "Freezer":
                device = Freezer(self.hass, app)
            elif app.type == "Oven":
                device = Oven(self.hass, app)
            elif app.type == "CoffeeMaker":
                device = CoffeeMaker(self.hass, app)
            elif app.type == "Hood":
                device = Hood(self.hass, app)
            elif app.type == "Hob":
                device = Hob(self.hass, app)
            elif app.type == "CookProcessor":
                device = CookProcessor(self.hass, app)
            else:
                _LOGGER.warning("Appliance type %s not implemented", app.type)
                continue
            devices.append(
                {CONF_DEVICE: device, CONF_ENTITIES: device.get_entity_info()}
            )
        self.devices = devices
        return devices


class HomeConnectDevice:
    """Generic Home Connect device."""

    # for some devices, this is instead BSH_POWER_STANDBY
    # see https://developer.home-connect.com/docs/settings/power_state
    power_off_state = BSH_POWER_OFF

    def __init__(self, hass: core.HomeAssistant, appliance) -> None:
        """Initialize the device class."""
        self.hass = hass
        self.appliance: HomeConnectAppliance = appliance
        self.programs = None

    def initialize(self):
        """Fetch the info needed to initialize the device."""
        try:
            self.appliance.get_status()
        except (HomeConnectError, ValueError):
            _LOGGER.debug("Unable to fetch appliance status. Probably offline")
        try:
            self.appliance.get_settings()
        except (HomeConnectError, ValueError):
            _LOGGER.debug("Unable to fetch settings. Probably offline")
        try:
            program_active = self.appliance.get_programs_active()
        except (HomeConnectError, ValueError):
            _LOGGER.debug("Unable to fetch active programs. Probably offline")
            program_active = None
        if program_active and ATTR_KEY in program_active:
            self.appliance.status[BSH_ACTIVE_PROGRAM] = {
                ATTR_VALUE: program_active[ATTR_KEY]
            }
        _LOGGER.debug(
            "Finished initializing: %s, Status: %s",
            self.appliance.haId,
            self.appliance.status,
        )
        self.appliance.listen_events(callback=self.event_callback)

    def event_callback(self, appliance):
        """Handle event."""
        _LOGGER.debug("Update triggered on %s", appliance.name)
        _LOGGER.debug(self.appliance.status)
        dispatcher_send(self.hass, SIGNAL_UPDATE_ENTITIES, appliance.haId)


class DeviceWithPrograms(HomeConnectDevice):
    """Device with programs."""

    def get_programs_available(self):
        """Get the available programs."""
        try:
            programs_available = self.appliance.get_programs_available()
            _LOGGER.debug("Programs Available: %s", programs_available)
        except (HomeConnectError, ValueError):
            _LOGGER.debug("Unable to fetch available programs. Probably offline")
            programs_available = []
        self.programs = programs_available
        return programs_available

    def get_program_switches(self):
        """Get a dictionary with info about program switches.

        There will be one switch for each program.
        """
        programs = self.get_programs_available()
        return [{ATTR_DEVICE: self, "program_name": p} for p in programs]


class DeviceWithOpState(HomeConnectDevice):
    """Device that has an operation state sensor."""


class DeviceWithDoor(HomeConnectDevice):
    """Device that has a door sensor."""


class DeviceWithLight(HomeConnectDevice):
    """Device that has lighting."""

    def get_light_entity(self):
        """Get a dictionary with info about the lighting."""
        return {ATTR_DEVICE: self, ATTR_DESC: "Light", ATTR_AMBIENT: None}


class DeviceWithAmbientLight(HomeConnectDevice):
    """Device that has ambient lighting."""

    def get_ambientlight_entity(self):
        """Get a dictionary with info about the ambient lighting."""
        return {ATTR_DEVICE: self, ATTR_DESC: "AmbientLight", ATTR_AMBIENT: True}


class DeviceWithRemoteControl(HomeConnectDevice):
    """Device that has Remote Control binary sensor."""


class DeviceWithRemoteStart(HomeConnectDevice):
    """Device that has a Remote Start binary sensor."""


class Dryer(
    DeviceWithDoor,
    DeviceWithOpState,
    DeviceWithPrograms,
    DeviceWithRemoteControl,
    DeviceWithRemoteStart,
):
    """Dryer class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        program_switches = self.get_program_switches()
        return {
            "switch": program_switches,
        }


class Dishwasher(
    DeviceWithDoor,
    DeviceWithAmbientLight,
    DeviceWithOpState,
    DeviceWithPrograms,
    DeviceWithRemoteControl,
    DeviceWithRemoteStart,
):
    """Dishwasher class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        program_switches = self.get_program_switches()
        return {
            "switch": program_switches,
        }


class Oven(
    DeviceWithDoor,
    DeviceWithOpState,
    DeviceWithPrograms,
    DeviceWithRemoteControl,
    DeviceWithRemoteStart,
):
    """Oven class."""

    power_off_state = BSH_POWER_STANDBY

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        program_switches = self.get_program_switches()
        return {
            "switch": program_switches,
        }


class Washer(
    DeviceWithDoor,
    DeviceWithOpState,
    DeviceWithPrograms,
    DeviceWithRemoteControl,
    DeviceWithRemoteStart,
):
    """Washer class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        program_switches = self.get_program_switches()
        return {
            "switch": program_switches,
        }


class WasherDryer(
    DeviceWithDoor,
    DeviceWithOpState,
    DeviceWithPrograms,
    DeviceWithRemoteControl,
    DeviceWithRemoteStart,
):
    """WasherDryer class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        program_switches = self.get_program_switches()
        return {
            "switch": program_switches,
        }


class CoffeeMaker(DeviceWithOpState, DeviceWithPrograms, DeviceWithRemoteStart):
    """Coffee maker class."""

    power_off_state = BSH_POWER_STANDBY

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        program_switches = self.get_program_switches()
        return {
            "switch": program_switches,
        }


class Hood(
    DeviceWithLight,
    DeviceWithAmbientLight,
    DeviceWithOpState,
    DeviceWithPrograms,
    DeviceWithRemoteControl,
    DeviceWithRemoteStart,
):
    """Hood class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        light_entity = self.get_light_entity()
        ambientlight_entity = self.get_ambientlight_entity()
        program_switches = self.get_program_switches()
        return {
            "switch": program_switches,
            "light": [light_entity, ambientlight_entity],
        }


class FridgeFreezer(
    DeviceWithDoor,
):
    """Fridge/Freezer class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        return {}


class Refrigerator(
    DeviceWithDoor,
):
    """Refrigerator class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        return {}


class Freezer(
    DeviceWithDoor,
):
    """Freezer class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        return {}


class Hob(DeviceWithOpState, DeviceWithPrograms, DeviceWithRemoteControl):
    """Hob class."""

    def get_entity_info(self):
        """Get a dictionary with infos about the associated entities."""
        program_switches = self.get_program_switches()
        return {
            "switch": program_switches,
        }


class CookProcessor(DeviceWithOpState):
    """CookProcessor class."""

    power_off_state = BSH_POWER_STANDBY

    def get_entity_info(self) -> dict:
        """Return nothing, used as a stub."""
        return {}

"""Setup light entities."""
from dataclasses import dataclass

from homeassistant.components.light import LightEntity, LightEntityDescription

from .api import HomeConnectDevice


@dataclass(frozen=True)
class HomeConnectLightEntityDescription(LightEntityDescription):
    """Light entity description."""


LIGHTS: dict[str, HomeConnectLightEntityDescription] = {
    "refrigeration_light": HomeConnectLightEntityDescription(key="refrigeration_light"),
    "common_ambient_light": HomeConnectLightEntityDescription(
        key="common_ambient_light"
    ),
    "common_light": HomeConnectLightEntityDescription(key="common_light"),
    "cooking_light": HomeConnectLightEntityDescription(key="cooking_light"),
}


class HomeConnectLight(LightEntity):
    """HomeConnect Light Entity."""

    def __init__(
        self,
        device: HomeConnectDevice,
        entity_description: HomeConnectLightEntityDescription,
    ) -> None:
        """Set up Light entity."""
        self._device = device
        self.entity_description = entity_description

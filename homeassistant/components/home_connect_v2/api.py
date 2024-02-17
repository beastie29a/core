"""API for Home Connect v2 bound to Home Assistant OAuth."""
from asyncio import run_coroutine_threadsafe

import homeconnect

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow


class ConfigEntryAuth(homeconnect.HomeConnectAPI):
    """Provide Home Connect v2 authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        hass: HomeAssistant,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize Home Connect v2 Auth."""
        self.hass = hass
        self.session = oauth_session
        super().__init__(self.session.token)

    def refresh_tokens(self) -> str:
        """Refresh and return new Home Connect v2 tokens using Home Assistant OAuth2 session."""
        run_coroutine_threadsafe(
            self.session.async_ensure_token_valid(), self.hass.loop
        ).result()

        return self.session.token["access_token"]


class HomeConnectDevice:
    """Home Connect Device."""

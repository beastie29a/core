"""Exceptions for Home Connect API calls."""

from homeconnect.api import HomeConnectError

from homeassistant.exceptions import HomeAssistantError


class HomeConnectAuthException(HomeAssistantError):
    """Authentication related error talking to the Home Connect API."""


class HomeConnectAPIException(HomeConnectError):
    """Errors related to the Home Connect API."""

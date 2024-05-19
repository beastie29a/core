"""Test Onkyo config flow."""

import logging
from typing import Any
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import eiscp
import pytest

from homeassistant import config_entries
from homeassistant.components.onkyo.const import (
    CONF_LEGACY_MAXIMUM_VOLUME,
    CONF_LEGACY_RECEIVER_MAXIMUM_VOLUME,
    CONF_SOURCES,
    DOMAIN,
    EISCP_IDENTIFIER,
    EISCP_MODEL_NAME,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import (
    CONF_DEVICE,
    CONF_HOST,
    CONF_MAC,
    CONF_MODEL,
    CONF_NAME,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry
from tests.components.onkyo import setup_integration

MOCK_ONKYO_CONFIG = {
    CONF_HOST: "127.0.0.1",
    CONF_NAME: "Receiver test name",
    CONF_LEGACY_MAXIMUM_VOLUME: 42,
    CONF_LEGACY_RECEIVER_MAXIMUM_VOLUME: 69,
    CONF_SOURCES: {
        "Key_one": "Value-A",
        "Key_two": "Value-B",
    },
}

_LOGGER = logging.getLogger(__name__)


async def test_no_manual_entry_and_no_devices_discovered(hass: HomeAssistant) -> None:
    """Test the full user configuration flow."""

    # eISCP discovery shows no devices discovered
    with patch.object(eiscp.eISCP, "discover", return_value=[]):
        init_result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
        )

        # Empty form triggers manual discovery
        configure_result = await hass.config_entries.flow.async_configure(
            init_result["flow_id"],
            user_input={},
        )

        assert configure_result["type"] is FlowResultType.ABORT
        assert configure_result["reason"] == "no_devices_found"


async def test_manual_entry_invalid_ip(hass: HomeAssistant) -> None:
    """Test the full user configuration flow."""

    init_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    configure_result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input={CONF_HOST: "xxx"},
    )

    assert configure_result["type"] is FlowResultType.FORM
    assert configure_result["step_id"] == "user"
    assert configure_result["errors"]["base"] == "no_ip"


@mock.patch("eiscp.eISCP", autospec=eiscp.eISCP)
async def test_manual_entry_valid_ip_fails_connection(
    mock_receiver: MagicMock, hass: HomeAssistant
) -> None:
    """Test the full user configuration flow."""

    client = mock_receiver.return_value
    client.host = "fake_host"
    client.port = 1337
    client.info = None

    init_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    configure_result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input={CONF_HOST: "127.0.0.1"},
    )

    client.disconnect.assert_called()
    assert configure_result["type"] is FlowResultType.FORM
    assert configure_result["step_id"] == "user"
    assert configure_result["errors"]["base"] == "cannot_connect"


@mock.patch("eiscp.eISCP", autospec=eiscp.eISCP)
async def test_manual_entry_valid_ip(
    mock_receiver: MagicMock, hass: HomeAssistant
) -> None:
    """Test the full user configuration flow."""

    client = mock_receiver.return_value
    client.host = "fake_host"
    client.port = 1337
    client.info = {EISCP_IDENTIFIER: "001122334455", EISCP_MODEL_NAME: "fake_model"}

    init_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    configure_result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input={CONF_HOST: "127.0.0.1"},
    )

    client.disconnect.assert_called()
    assert configure_result["type"] is FlowResultType.CREATE_ENTRY
    assert configure_result["title"] == "fake_model 001122334455"
    assert configure_result["data"][CONF_HOST] == "fake_host"
    assert configure_result["data"][CONF_PORT] == 1337
    assert configure_result["data"][CONF_NAME] == "fake_model 001122334455"
    assert configure_result["data"][CONF_MODEL] == "fake_model"
    assert configure_result["data"][CONF_MAC] == "001122334455"


async def test_select_manually_discovered_device(hass: HomeAssistant) -> None:
    """Test the full user configuration flow."""

    info = {EISCP_IDENTIFIER: "004815162342", EISCP_MODEL_NAME: "fake_model"}
    receiver = MagicMock()
    receiver.host = "fake_host"
    receiver.port = 12345

    # Mock the dict
    receiver.info.__getitem__.side_effect = info.__getitem__

    # eISCP discovery shows 1 devices discovered
    with patch.object(eiscp.eISCP, "discover", return_value=[receiver]):
        init_result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
        )

        # Empty form triggers manual discovery
        configure_result = await hass.config_entries.flow.async_configure(
            init_result["flow_id"],
            user_input={},
        )

        assert configure_result["type"] is FlowResultType.FORM

        # Empty form triggers manual discovery
        configure_result = await hass.config_entries.flow.async_configure(
            init_result["flow_id"],
            user_input={CONF_DEVICE: "004815162342"},
        )

    assert configure_result["type"] is FlowResultType.CREATE_ENTRY
    assert configure_result["title"] == "fake_model 004815162342"
    assert configure_result["data"][CONF_HOST] == "fake_host"
    assert configure_result["data"][CONF_PORT] == 12345
    assert configure_result["data"][CONF_NAME] == "fake_model 004815162342"
    assert configure_result["data"][CONF_MODEL] == "fake_model"
    assert configure_result["data"][CONF_MAC] == "004815162342"


@pytest.mark.parametrize(
    ("user_input", "error"),
    [
        (
            {CONF_SOURCES: ["list"]},
            "invalid_sources",
        ),
    ],
)
async def test_options_flow_failures(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    user_input: dict[str, Any],
    error: str,
) -> None:
    """Test load and unload entry."""
    await setup_integration(hass, config_entry)

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={**user_input},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
    assert result["errors"]["base"] == error


async def test_options_flow(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Test options flow."""
    await setup_integration(hass, config_entry)

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "receiver_max_volume": 200,
            "maximum_volume": 42,
            "sources": {},
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        "receiver_max_volume": 200,
        "maximum_volume": 42,
        "sources": {},
    }


@pytest.mark.parametrize(
    ("user_input", "error"),
    [
        (
            {CONF_HOST: None},
            "no_host_defined",
        ),
        (
            {CONF_HOST: "127.0.0.1"},
            "cannot_connect",
        ),
    ],
)
@mock.patch("eiscp.eISCP", autospec=eiscp.eISCP)
async def test_import_fail(
    mock_receiver: MagicMock,
    hass: HomeAssistant,
    user_input: dict[str, Any],
    error: str,
) -> None:
    """Test import flow."""

    client = mock_receiver.return_value
    client.info = None

    with patch("homeassistant.components.onkyo.config_flow"):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data=user_input
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == error


@mock.patch("eiscp.eISCP", autospec=eiscp.eISCP)
async def test_import_success(
    mock_receiver: MagicMock,
    mock_setup_entry: AsyncMock,
    hass: HomeAssistant,
) -> None:
    """Test import flow."""

    client = mock_receiver.return_value
    client.info = {EISCP_IDENTIFIER: "001122334455", EISCP_MODEL_NAME: "Test model"}

    with patch("homeassistant.components.onkyo.config_flow"):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=MOCK_ONKYO_CONFIG,
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test model 001122334455"
    assert result["result"].unique_id == "001122334455"
    assert result["data"] == MOCK_ONKYO_CONFIG
    assert len(mock_setup_entry.mock_calls) == 1

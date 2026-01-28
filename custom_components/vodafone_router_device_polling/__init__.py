from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
import logging

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, ENTRY_DATA_HOST, OPTION_PASSWORD, OPTION_SCAN_INTERVAL, OPTION_USERNAME
from .coordinator import VodafoneDeviceCoordinator

_LOGGER = logging.getLogger(__name__)

# TODO: Add mac address to config options so that the user can filter devices by mac address - if empty all devices are included
PLATFORMS = [Platform.BINARY_SENSOR, Platform.DEVICE_TRACKER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vodafone Station integration from a config entry."""
    _LOGGER.info("Setting up Vodafone Station integration for entry: %s", entry.entry_id)

    host = entry.data[ENTRY_DATA_HOST]
    username = entry.options.get(OPTION_USERNAME)
    password = entry.options.get(OPTION_PASSWORD)
    scan_interval = entry.options.get(OPTION_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    _LOGGER.debug("Configuration: host=%s, username=%s, scan_interval=%s", host, username, scan_interval)

    coordinator = VodafoneDeviceCoordinator(
        hass, host=host, username=username, password=password, scan_interval=scan_interval
    )

    try:
        _LOGGER.debug("Attempting initial login and data refresh")
        await coordinator.async_login()
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.info("Initial connection and data refresh successful")
    except Exception as err:
        _LOGGER.error("Failed to connect to Vodafone Station: %s", err, exc_info=True)
        raise ConfigEntryNotReady(f"Cannot connect to Vodafone Station: {err}") from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _LOGGER.debug("Setting up platforms: %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Vodafone Station integration setup completed successfully")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and logout from the Vodafone Station."""
    _LOGGER.info("Unloading Vodafone Station integration for entry: %s", entry.entry_id)

    coordinator: VodafoneDeviceCoordinator = hass.data[DOMAIN][entry.entry_id]

    try:
        _LOGGER.debug("Attempting to logout from Vodafone Station")
        await coordinator.async_logout()
        _LOGGER.info("Successfully logged out from Vodafone Station")
    except Exception as err:
        _LOGGER.warning("Failed to logout from Vodafone Station: %s", err)

    # Unload platforms
    _LOGGER.debug("Unloading platforms: %s", PLATFORMS)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        _LOGGER.debug("Platforms unloaded successfully")
    else:
        _LOGGER.warning("Some platforms failed to unload")

    # Remove from hass.data
    hass.data[DOMAIN].pop(entry.entry_id, None)
    _LOGGER.info("Vodafone Station integration unloaded")

    return unload_ok

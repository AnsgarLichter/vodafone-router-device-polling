from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from voluptuous import Any
from .const import (
    DEVICE_PROPERTY_HOSTNAME,
    DEVICE_PROPERTY_MAC_ADDRESS,
    DEVICE_PROPERTY_NAME,
    DOMAIN,
    ROUTER_PROPERTY_LAN_DEVICES,
    ROUTER_PROPERTY_WLAN_DEVICES,
)
from .coordinator import VodafoneDeviceCoordinator
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vodafone Station devices as binary sensors."""
    _LOGGER.info(
        "Setting up Vodafone binary sensor entities for entry: %s", entry.entry_id
    )

    coordinator: VodafoneDeviceCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Coordinator is already logged in and has data from __init__.py
    _LOGGER.debug("Using coordinator data for binary sensor setup (already logged in)")

    _LOGGER.debug("Creating binary sensor entities from connected devices")
    sensors = []
    total_devices = 0

    for dev_list_name in [ROUTER_PROPERTY_LAN_DEVICES, ROUTER_PROPERTY_WLAN_DEVICES]:
        devices = coordinator.data.get(dev_list_name, [])
        _LOGGER.debug(
            "Processing %s devices from %s for binary sensors",
            len(devices),
            dev_list_name,
        )

        for device in devices:
            total_devices += 1
            if not device.get(DEVICE_PROPERTY_MAC_ADDRESS):
                _LOGGER.warning("Skipping device without MAC address: %s", device)
                continue

            _LOGGER.debug(
                "Creating binary sensor for device: %s (%s)",
                device.get(DEVICE_PROPERTY_HOSTNAME, "Unknown"),
                device.get(DEVICE_PROPERTY_MAC_ADDRESS),
            )
            sensors.append(VodafoneDeviceBinarySensor(coordinator, device))

    _LOGGER.info(
        "Created %s binary sensor entities from %s total devices",
        len(sensors),
        total_devices,
    )
    async_add_entities(sensors)


class VodafoneDeviceBinarySensor(BinarySensorEntity):
    """Binary sensor representing a Vodafone Station connected device."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: VodafoneDeviceCoordinator, device: dict[str, Any]):
        self.coordinator = coordinator
        self.device = device
        self.mac = device.get(DEVICE_PROPERTY_MAC_ADDRESS)
        self.name = (
            device.get(DEVICE_PROPERTY_HOSTNAME)
            or device.get(DEVICE_PROPERTY_NAME)
            or self.mac
        )
        # MAC is guaranteed here because we filtered earlier
        self._attr_name = f"{self.name} Sensor"
        self._attr_unique_id = f"vodafone_{self.mac.replace(':', '')}_sensor"

        _LOGGER.debug(
            "Initialized binary sensor for %s (MAC: %s, unique_id: %s)",
            self._attr_name,
            self.mac,
            self._attr_unique_id,
        )

    @property
    def is_on(self) -> bool:
        """Return True if device is connected."""
        connected_macs = {
            d.get(DEVICE_PROPERTY_MAC_ADDRESS)
            for d in self.coordinator.data.get(ROUTER_PROPERTY_LAN_DEVICES, [])
        }
        connected_macs.update(
            {
                d.get(DEVICE_PROPERTY_MAC_ADDRESS)
                for d in self.coordinator.data.get(ROUTER_PROPERTY_WLAN_DEVICES, [])
            }
        )
        is_connected = self.mac in connected_macs
        _LOGGER.debug(
            "Binary sensor %s (%s) state: %s",
            self._attr_name,
            self.mac,
            "ON" if is_connected else "OFF",
        )
        return is_connected

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self) -> None:
        """Register for coordinator updates."""
        _LOGGER.debug(
            "Adding binary sensor %s (%s) to Home Assistant", self._attr_name, self.mac
        )
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
        _LOGGER.debug(
            "Registered binary sensor %s for coordinator updates", self._attr_name
        )

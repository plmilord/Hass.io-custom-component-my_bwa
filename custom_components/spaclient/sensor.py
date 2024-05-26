"""Support for Spa Client sensors."""
# Import the device class from the component that you want to support
from . import SpaClientDevice
from .const import _LOGGER, DOMAIN, ICONS, FAULT_MSG, SPA
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Spa Client sensors."""

    spaclient = hass.data[DOMAIN][config_entry.entry_id][SPA]
    entities = []

    entities.append(SpaFaultLog(spaclient, config_entry))

    async_add_entities(entities, True)


class SpaFaultLog(SpaClientDevice, SensorEntity):
    """Representation of a sensor."""

    def __init__(self, spaclient, config_entry):
        """Initialize the device."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._sensor_type = None
        self._icon = ICONS.get('Fault Log')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._spaclient.get_macaddr().replace(':', '')}#fault_log"

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Last Known Fault'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def native_value(self):
        """Return the state of this sensor."""
        return FAULT_MSG.get(self._spaclient.get_fault_log_msg_code())

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()

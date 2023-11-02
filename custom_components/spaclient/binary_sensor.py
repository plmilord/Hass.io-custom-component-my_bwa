"""Support for Spa Client binary sensors."""
# Import the device class from the component that you want to support
from . import SpaClientDevice
from .const import _LOGGER, DOMAIN, ICONS, SPA
from homeassistant.components.binary_sensor import BinarySensorEntity, DEVICE_CLASS_CONNECTIVITY

from datetime import timedelta
SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Spa Client binary sensors."""

    spaclient = hass.data[DOMAIN][config_entry.entry_id][SPA]
    entities = []

    circ_pump_array = spaclient.get_circ_pump_list()

    if circ_pump_array[0] != 0:
        entities.append(CircPump(spaclient, config_entry))

    for i in range(0, 2):
        entities.append(FilterCycle(i + 1, spaclient, config_entry))

    entities.append(SpaGateway(spaclient, config_entry))

    async_add_entities(entities, True)


class CircPump(SpaClientDevice, BinarySensorEntity):
    """Representation of a binary sensor."""

    def __init__(self, spaclient, config_entry):
        """Initialize the device."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._sensor_type = None
        self._icon = ICONS.get('Circulation Pump')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._spaclient.get_macaddr().replace(':', '')}#circulation_pump"

    @property
    def device_class(self):
        """Return the class of this binary sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return 'Circulation Pump'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self._spaclient.get_circ_pump()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


class FilterCycle(SpaClientDevice, BinarySensorEntity):
    """Representation of an Auxiliary switch."""

    def __init__(self, filter_num, spaclient, config_entry):
        """Initialize the device."""
        super().__init__(spaclient, config_entry)
        self._filter_num = filter_num
        self._spaclient = spaclient
        self._sensor_type = None
        self._icon = ICONS.get('Filter Cycle')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._spaclient.get_macaddr().replace(':', '')}#filter_cycle_{str(self._filter_num)}_status"

    @property
    def device_class(self):
        """Return the class of this binary sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return 'Filter Cycle ' + str(self._filter_num) + ' Status'

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        attrs = {}
        attrs["Begins"] = self._spaclient.get_filter_begins(self._filter_num)
        attrs["Runs"] = self._spaclient.get_filter_runs(self._filter_num)
        attrs["Ends"] = self._spaclient.get_filter_ends(self._filter_num)
        return attrs

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_filter_mode(self._filter_num)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


class SpaGateway(SpaClientDevice, BinarySensorEntity):
    """Representation of a binary sensor."""

    def __init__(self, spaclient, config_entry):
        """Initialize the device."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._sensor_type = DEVICE_CLASS_CONNECTIVITY

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._spaclient.get_macaddr().replace(':', '')}#bwa_wi_fi_module"

    @property
    def device_class(self):
        """Return the class of this binary sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return 'bwa Wi-Fi Module'

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self._spaclient.get_gateway_status()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()

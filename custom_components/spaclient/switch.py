import logging

# Import the device class from the component that you want to support
from custom_components import spaclient
from homeassistant.components.switch import SwitchEntity
from datetime import timedelta

from .const import (
    ICONS,
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = spaclient.INTERVAL

nb_toggle = spaclient.NB_TOGGLE


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    spa_data = spaclient.NETWORK
    async_add_entities([SpaPump(1, spa_data), SpaPump(2, spa_data), SpaPump(3, spa_data)])
    async_add_entities([HeatMode(spa_data), TempRange(spa_data)])


class SpaPump(SwitchEntity):
    """Representation of a Spa Pump switch."""

    def __init__(self, pump_num, data):
        """Initialise the device."""
        self._spa = data.spa
        self._pump_num = pump_num
        self._icon = ICONS.get('Spa Pump ' + str(self._pump_num))

    @property
    def name(self):
        """Return the name of the device."""
        return 'Spa Pump ' + str(self._pump_num)

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attrs = {}

        attrs["Current Temp"] = self._spa.get_current_temp()
        attrs["Time"] = self._spa.get_current_time()
        attrs["Set Temp"] = self._spa.get_set_temp()
        attrs["Pump 1"] = self._spa.get_pump(1)
        attrs["Pump 2"] = self._spa.get_pump(2)
        attrs["Pump 3"] = self._spa.get_pump(3)
        attrs["Temperature Range"] = self._spa.get_temp_range()
        attrs["Heat Mode"] = self._spa.get_heat_mode()

        return attrs

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spa.get_pump(self._pump_num) != "Off"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        _LOGGER.info("Spa Pump %s status %s", self._pump_num, self._spa.get_pump(self._pump_num))
        _LOGGER.info("Turning on Spa Pump %s", self._pump_num)
        self._spa.set_pump(self._pump_num, "High", nb_toggle)

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        _LOGGER.info("Spa Pump %s status %s", self._pump_num, self._spa.get_pump(self._pump_num))
        if self._spa.get_pump(self._pump_num) == "Low":
            _LOGGER.info("Turning on Spa Pump %s", self._pump_num)
        if self._spa.get_pump(self._pump_num) == "High":
            _LOGGER.info("Turning off Spa Pump %s", self._pump_num)
        self._spa.set_pump(self._pump_num, "Off", nb_toggle)

    async def async_update(self):
        """Update the state of the switch."""
        self._spa.read_all_msg()


class HeatMode(SwitchEntity):
    """Representation of the Heat Mode switch."""

    def __init__(self, data):
        """Initialise the switch."""
        self._spa = data.spa
        self._icon = ICONS.get('Heat Mode')

    @property
    def name(self):
        """Return the name of the device."""
        return 'Heat Mode'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spa.get_heat_mode() != "Rest"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        self._spa.set_heat_mode("Ready")
        _LOGGER.info("Heat Mode changed to %s", self._spa.get_heat_mode())

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spa.set_heat_mode("Rest")
        _LOGGER.info("Heat Mode changed to %s", self._spa.get_heat_mode())

    async def async_update(self):
        """Update the state of the switch."""
        self._spa.read_all_msg()


class TempRange(SwitchEntity):
    """Representation of the Temperature Range switch."""

    def __init__(self, data):
        """Initialise the switch."""
        self._spa = data.spa
        self._icon = ICONS.get('Temperature Range')

    @property
    def name(self):
        """Return the name of the device."""
        return 'Temperature Range'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spa.get_temp_range() != "Low"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        self._spa.set_temp_range("High")
        _LOGGER.info("Temperature Range changed to %s", self._spa.get_temp_range())

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spa.set_temp_range("Low")
        _LOGGER.info("Temperature Range changed to %s", self._spa.get_temp_range())

    async def async_update(self):
        """Update the state of the switch."""
        self._spa.read_all_msg()

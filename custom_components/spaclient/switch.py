"""Support for Spa Client switches."""
# Import the device class from the component that you want to support
from . import SpaClientDevice
from .const import _LOGGER, DOMAIN, ICONS, SPA
from homeassistant.components.switch import SwitchEntity

from datetime import timedelta
SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the Spa Client switches."""

    spaclient = hass.data[DOMAIN][config_entry.entry_id][SPA]
    entities = []

    pump_array = spaclient.get_pump_list()
    blower_array = spaclient.get_blower_list()
    mister_array = spaclient.get_mister_list()
    aux_array = spaclient.get_aux_list()

    for i in range(0, 6):
        if pump_array[i] != 0:
            entities.append(SpaPump(i + 1, spaclient, config_entry))
    if blower_array[0] != 0:
        entities.append(Blower(spaclient, config_entry))
    if mister_array[0] != 0:
        entities.append(Mister(spaclient, config_entry))
    for i in range(0, 2):
        if aux_array[i] != 0:
            entities.append(SpaAux(i + 1, spaclient, config_entry))

    entities.append(HeatMode(spaclient, config_entry))
    entities.append(TempRange(spaclient, config_entry))
    entities.append(EnableFilterCycle2(spaclient, config_entry))

    async_add_entities(entities, True)


class SpaPump(SpaClientDevice, SwitchEntity):
    """Representation of a Pump switch."""

    def __init__(self, pump_num, spaclient, config_entry):
        """Initialise the device."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._pump_num = pump_num
        self._icon = ICONS.get('Pump ' + str(self._pump_num))

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return 'Pump ' + str(self._pump_num)

    @property
    def name(self):
        """Return the name of the device."""
        return 'Pump ' + str(self._pump_num)

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attrs = {}
        attrs['Pump ' + str(self._pump_num)] = self._spaclient.get_pump(self._pump_num)
        return attrs

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_pump(self._pump_num) != "Off"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        #_LOGGER.info("Pump %s status %s", self._pump_num, self._spaclient.get_pump(self._pump_num))
        #_LOGGER.info("Turning On Pump %s", self._pump_num)
        if self._spaclient.pump_array[self._pump_num - 1] == 1:
            self._spaclient.set_pump(self._pump_num, "High")
            return

        self._spaclient.set_pump(self._pump_num, "Low")

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        #_LOGGER.info("Pump %s status %s", self._pump_num, self._spaclient.get_pump(self._pump_num))
        #if self._spaclient.get_pump(self._pump_num) == "Low":
            #_LOGGER.info("Set to High Pump %s", self._pump_num)
        #if self._spaclient.get_pump(self._pump_num) == "High":
            #_LOGGER.info("Turning Off Pump %s", self._pump_num)
        if self._spaclient.get_pump(self._pump_num) == "Low":
            self._spaclient.set_pump(self._pump_num, "High")
            return

        self._spaclient.set_pump(self._pump_num, "Off")


class Blower(SpaClientDevice, SwitchEntity):
    """Representation of a Blower switch."""

    def __init__(self, spaclient, config_entry):
        """Initialise the switch."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._icon = ICONS.get('Blower')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return 'Blower'

    @property
    def name(self):
        """Return the name of the device."""
        return 'Blower'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attrs = {}
        attrs["Blower"] = self._spaclient.get_blower()
        return attrs

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_blower() != "Off"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        self._spaclient.set_blower("High")
        #_LOGGER.info("Blower changed to %s", self._spaclient.get_blower())

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_blower("Off")
        #_LOGGER.info("Blower changed to %s", self._spaclient.get_blower())


class Mister(SpaClientDevice, SwitchEntity):
    """Representation of a Mister switch."""

    def __init__(self, spaclient, config_entry):
        """Initialise the switch."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._icon = ICONS.get('Mister')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return 'Mister'

    @property
    def name(self):
        """Return the name of the device."""
        return 'Mister'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_mister() != "Off"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        #_LOGGER.info("Turning On Mister")
        self._spaclient.set_mister("On")

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        #_LOGGER.info("Turning Off Mister")
        self._spaclient.set_mister("Off")


class SpaAux(SpaClientDevice, SwitchEntity):
    """Representation of an Auxiliary switch."""

    def __init__(self, aux_num, spaclient, config_entry):
        """Initialise the device."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._aux_num = aux_num
        self._icon = ICONS.get('Auxiliary ' + str(self._aux_num))

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return 'Auxiliary ' + str(self._aux_num)

    @property
    def name(self):
        """Return the name of the device."""
        return 'Auxiliary ' + str(self._aux_num)

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_aux(self._aux_num) != "Off"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        #_LOGGER.info("Turning On Auxiliary %s", self._aux_num)
        self._spaclient.set_aux(self._aux_num, "On")

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        #_LOGGER.info("Turning Off Auxiliary %s", self._aux_num)
        self._spaclient.set_aux(self._aux_num, "Off")


class HeatMode(SpaClientDevice, SwitchEntity):
    """Representation of a Heat Mode switch."""

    def __init__(self, spaclient, config_entry):
        """Initialise the switch."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._icon = ICONS.get('Heat Mode')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return 'Heat Mode'

    @property
    def name(self):
        """Return the name of the device."""
        return 'Heat Mode'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attrs = {}
        attrs["Heat Mode"] = self._spaclient.get_heat_mode()
        return attrs

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_heat_mode() != "Rest"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        self._spaclient.set_heat_mode("Ready")
        #_LOGGER.info("Heat Mode changed to %s", self._spaclient.get_heat_mode())

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_heat_mode("Rest")
        #_LOGGER.info("Heat Mode changed to %s", self._spaclient.get_heat_mode())


class TempRange(SpaClientDevice, SwitchEntity):
    """Representation of a Temperature Range switch."""

    def __init__(self, spaclient, config_entry):
        """Initialise the switch."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._icon = ICONS.get('Temperature Range')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return 'Temperature Range'

    @property
    def name(self):
        """Return the name of the device."""
        return 'Temperature Range'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attrs = {}
        attrs["Temperature Range"] = self._spaclient.get_temp_range()
        return attrs

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_temp_range() != "Low"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        self._spaclient.set_temp_range("High")
        #_LOGGER.info("Temperature Range changed to %s", self._spaclient.get_temp_range())

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_temp_range("Low")
        #_LOGGER.info("Temperature Range changed to %s", self._spaclient.get_temp_range())


class EnableFilterCycle2(SpaClientDevice, SwitchEntity):
    """Representation of a Temperature Range switch."""

    def __init__(self, spaclient, config_entry):
        """Initialise the switch."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._icon = ICONS.get('Filter Cycle')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return 'Enable Filter Cycle 2'

    @property
    def name(self):
        """Return the name of the device."""
        return 'Filter Cycle 2'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_filter2_enabled()

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        #_LOGGER.info("Turning On Filter Cycle 2")
        self._spaclient.set_filter2_enabled(1)

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        #_LOGGER.info("Turning Off Filter Cycle 2")
        self._spaclient.set_filter2_enabled(0)

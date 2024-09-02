"""Support for Spa Client switches."""
# Import the device class from the component that you want to support
from . import SpaClientDevice
from .const import _LOGGER, DOMAIN, ICONS, SPA
from datetime import timedelta
from homeassistant.components.switch import SwitchEntity

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the Spa Client switches."""

    spaclient = hass.data[DOMAIN][config_entry.entry_id][SPA]
    entities = []

    aux_array = spaclient.get_aux_list()
    blower_array = spaclient.get_blower_list()
    mister_array = spaclient.get_mister_list()
    pump_array = spaclient.get_pump_list()

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

    entities.append(EnableFilterCycle2(spaclient, config_entry))
    entities.append(HeatMode(spaclient, config_entry))
    entities.append(HoldMode(spaclient, config_entry))
    entities.append(StandbyMode(spaclient, config_entry))
    entities.append(TempRange(spaclient, config_entry))

    async_add_entities(entities, True)


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
        return f"{self._spaclient.get_macaddr().replace(':', '')}#auxiliary_{str(self._aux_num)}"

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
        self._spaclient.set_aux(self._aux_num, "On")

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_aux(self._aux_num, "Off")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


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
        return f"{self._spaclient.get_macaddr().replace(':', '')}#blower"

    @property
    def name(self):
        """Return the name of the device."""
        return 'Blower'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def extra_state_attributes(self):
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
        self._spaclient.set_blower("On")

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_blower("Off")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


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
        return f"{self._spaclient.get_macaddr().replace(':', '')}#mister"

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
        self._spaclient.set_mister("On")

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_mister("Off")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


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
        return f"{self._spaclient.get_macaddr().replace(':', '')}#pump_{str(self._pump_num)}"

    @property
    def name(self):
        """Return the name of the device."""
        return 'Pump ' + str(self._pump_num)

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def extra_state_attributes(self):
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
        if self._spaclient.cfg_pump_array[self._pump_num - 1] == 1:
            return self._spaclient.set_pump(self._pump_num, "High")

        self._spaclient.set_pump(self._pump_num, "Low")

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        if self._spaclient.get_pump(self._pump_num) == "Low":
            return self._spaclient.set_pump(self._pump_num, "High")

        self._spaclient.set_pump(self._pump_num, "Off")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


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
        return f"{self._spaclient.get_macaddr().replace(':', '')}#enable_filter_cycle_2"

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
        self._spaclient.set_filter2_enabled(1)

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_filter2_enabled(0)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


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
        return f"{self._spaclient.get_macaddr().replace(':', '')}#heat_mode"

    @property
    def name(self):
        """Return the name of the device."""
        return 'Heat Mode'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def extra_state_attributes(self):
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

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_heat_mode("Rest")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


class HoldMode(SpaClientDevice, SwitchEntity):
    """Representation of a Hold Mode switch."""

    def __init__(self, spaclient, config_entry):
        """Initialise the switch."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._icon = ICONS.get('Hold Mode')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._spaclient.get_macaddr().replace(':', '')}#hold_mode"

    @property
    def name(self):
        """Return the name of the device."""
        return 'Hold Mode'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        attrs = {}
        attrs["Remaining Time"] = self._spaclient.get_hold_mode_remain_time()
        return attrs

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_hold_mode()

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        self._spaclient.set_hold_mode(1)

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_hold_mode(0)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


class StandbyMode(SpaClientDevice, SwitchEntity):
    """Representation of a Standby Mode switch."""

    def __init__(self, spaclient, config_entry):
        """Initialise the switch."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._icon = ICONS.get('Standby Mode')

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._spaclient.get_macaddr().replace(':', '')}#standby_mode"

    @property
    def name(self):
        """Return the name of the device."""
        return 'Standby Mode'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._spaclient.get_standby_mode()

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        self._spaclient.set_standby_mode()

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_standby_mode()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()


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
        return f"{self._spaclient.get_macaddr().replace(':', '')}#temperature_range"

    @property
    def name(self):
        """Return the name of the device."""
        return 'Temperature Range'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def extra_state_attributes(self):
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

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._spaclient.set_temp_range("Low")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()

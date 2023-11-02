"""Support for Spa Client Filter Cycle times."""
# Import the device class from the component that you want to support
from . import SpaClientDevice
from .const import _LOGGER, DOMAIN, FILTER_CYCLE_TIMES, SPA
from homeassistant.components.time import TimeEntity

from datetime import time, timedelta
SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the Spa Client times."""

    spaclient = hass.data[DOMAIN][config_entry.entry_id][SPA]
    entities = []

    for cycle_times in FILTER_CYCLE_TIMES:
        for i in range(0, 2):
            entities.append(FilterCycle(cycle_times, i + 1, spaclient, config_entry))

    async_add_entities(entities, True)


class FilterCycle(SpaClientDevice, TimeEntity):
    """Representation of a time."""

    def __init__(self, cycle_times, filter_num, spaclient, config_entry):
        """Initialize the device."""
        super().__init__(spaclient, config_entry)
        self._cycle_times = cycle_times
        self._filter_num = filter_num
        self._spaclient = spaclient

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        if self._cycle_times == 'Begins':
            return f"{self._spaclient.get_macaddr().replace(':', '')}#filter_cycle_{str(self._filter_num)}_begins"
        if self._cycle_times == 'Runs':
            return f"{self._spaclient.get_macaddr().replace(':', '')}#filter_cycle_{str(self._filter_num)}_runs"

    @property
    def name(self):
        """Return the name of the device."""
        if self._cycle_times == 'Begins':
            return 'Filter Cycle ' + str(self._filter_num) + ' Begins'
        if self._cycle_times == 'Runs':
            return 'Filter Cycle ' + str(self._filter_num) + ' Runs'

    @property
    def native_value(self) -> time | None:
        """Return the value reported by the time."""
        if self._cycle_times == 'Begins':
            return time(self._spaclient.get_filter_begins_hour(self._filter_num), self._spaclient.get_filter_begins_minute(self._filter_num))
        if self._cycle_times == 'Runs':
            return time(self._spaclient.get_filter_runs_hour(self._filter_num), self._spaclient.get_filter_runs_minute(self._filter_num))

    async def async_set_value(self, value: time) -> None:
        """Update the current value."""
        if self._cycle_times == 'Begins':
            return self._spaclient.set_filter_cycle_begins_time(self._filter_num, value)
        if self._cycle_times == 'Runs':
            return self._spaclient.set_filter_cycle_runs_time(self._filter_num, value)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()

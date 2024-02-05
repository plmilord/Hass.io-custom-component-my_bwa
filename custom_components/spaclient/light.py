"""Support for Spa Client lights."""
# Import the device class from the component that you want to support
from . import SpaClientDevice
from .const import _LOGGER, DOMAIN, SPA
from datetime import timedelta
from homeassistant.components.light import LightEntity

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the Spa Client lights."""

    spaclient = hass.data[DOMAIN][config_entry.entry_id][SPA]
    entities = []

    light_array = spaclient.get_light_list()

    for i in range(0, 2):
        if light_array[i] != 0:
            entities.append(SpaLight(i + 1, spaclient, config_entry))

    async_add_entities(entities, True)


class SpaLight(SpaClientDevice, LightEntity):
    """Representation of a light."""

    def __init__(self, light_num, spaclient, config_entry):
        """Initialize the device."""
        super().__init__(spaclient, config_entry)
        self._light_num = light_num
        self._spaclient = spaclient

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._spaclient.get_macaddr().replace(':', '')}#light_{str(self._light_num)}"

    @property
    def name(self):
        """Return the name of the device."""
        return 'Light ' + str(self._light_num)

    @property
    def is_on(self):
        """Return true if light is on."""
        #_LOGGER.info("Update Light %s state", self._light_num)
        return self._spaclient.get_light(self._light_num)

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        #_LOGGER.info("Turning On Light %s", self._light_num)
        self._spaclient.set_light(self._light_num, True)

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        #_LOGGER.info("Turning Off Light %s", self._light_num)
        self._spaclient.set_light(self._light_num, False)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._spaclient.get_gateway_status()

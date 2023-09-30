"""Support for Spa Client climate device."""
# Import the device class from the component that you want to support
from . import SpaClientDevice
from .const import _LOGGER, DOMAIN, ICONS, SPA
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import SUPPORT_TARGET_TEMPERATURE, HVAC_MODE_HEAT, HVAC_MODE_OFF
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.util.unit_conversion import TemperatureConverter

from datetime import timedelta
SCAN_INTERVAL = timedelta(seconds=1)

SUPPORT_HVAC = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the Spa Client climate device."""

    spaclient = hass.data[DOMAIN][config_entry.entry_id][SPA]
    entities = []

    entities.append(SpaThermostat(spaclient, config_entry))

    async_add_entities(entities, True)


class SpaThermostat(SpaClientDevice, ClimateEntity):
    """Representation of a climate device."""

    def __init__(self, spaclient, config_entry):
        """Initialize the device."""
        super().__init__(spaclient, config_entry)
        self._spaclient = spaclient
        self._icon = ICONS.get('Spa Thermostat')

    @property
    def name(self):
        """Return the name of the device."""
        return 'Spa Thermostat'

    @property
    def icon(self):
        """Return the icon of the device."""
        return self._icon

    @property
    def hvac_mode(self):
        """Return current HVAC mode."""
        if self._spaclient.get_heating():
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        """Return available HVAC modes."""
        return SUPPORT_HVAC

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        if self._spaclient.get_current_temp() != None:
            if self.hass.config.units.temperature_unit == TEMP_CELSIUS and self._spaclient.temp_scale == "Fahrenheit":
                return round(TemperatureConverter.convert(self._spaclient.get_current_temp(), TEMP_FAHRENHEIT, TEMP_CELSIUS) * 2) / 2
            if self.hass.config.units.temperature_unit == TEMP_CELSIUS and self._spaclient.temp_scale == "Celsius":
                return self._spaclient.get_current_temp() / 2
            if self.hass.config.units.temperature_unit == TEMP_FAHRENHEIT and self._spaclient.temp_scale == "Celsius":
                return round(TemperatureConverter.convert(self._spaclient.get_current_temp() / 2, TEMP_CELSIUS, TEMP_FAHRENHEIT) * 2) / 2
            return self._spaclient.get_current_temp()
        return None

    @property
    def target_temperature(self):
        """Return the target temperature."""
        if self.hass.config.units.temperature_unit == TEMP_CELSIUS and self._spaclient.temp_scale == "Fahrenheit":
            return round(TemperatureConverter.convert(self._spaclient.get_set_temp(), TEMP_FAHRENHEIT, TEMP_CELSIUS) * 2) / 2
        if self.hass.config.units.temperature_unit == TEMP_CELSIUS and self._spaclient.temp_scale == "Celsius":
            return self._spaclient.get_set_temp() / 2
        if self.hass.config.units.temperature_unit == TEMP_FAHRENHEIT and self._spaclient.temp_scale == "Celsius":
            return round(TemperatureConverter.convert(self._spaclient.get_set_temp() / 2, TEMP_CELSIUS, TEMP_FAHRENHEIT) * 2) / 2
        return self._spaclient.get_set_temp()

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs[ATTR_TEMPERATURE]
        if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
            temperature = round(TemperatureConverter.convert(temperature, TEMP_CELSIUS, TEMP_FAHRENHEIT))
        await self._spaclient.set_temperature(temperature)

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target HVAC mode."""
        if self._spaclient.get_heating():
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        if self._spaclient.get_temp_range() == "High":
            return TemperatureConverter.convert(self._spaclient.get_high_range_min(), TEMP_FAHRENHEIT, self.temperature_unit)
        return TemperatureConverter.convert(self._spaclient.get_low_range_min(), TEMP_FAHRENHEIT, self.temperature_unit)

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        if self._spaclient.get_temp_range() == "High":
            return TemperatureConverter.convert(self._spaclient.get_high_range_max(), TEMP_FAHRENHEIT, self.temperature_unit)
        return TemperatureConverter.convert(self._spaclient.get_low_range_max(), TEMP_FAHRENHEIT, self.temperature_unit)

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

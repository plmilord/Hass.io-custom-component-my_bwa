"""The Spa Client integration."""
import asyncio

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

# Import the device class from the component that you want to support
from .const import (
    _LOGGER,
    CONF_SYNC_TIME,
    DATA_LISTENER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ICONS,
    MIN_SCAN_INTERVAL,
    SPA,
    SPACLIENT_COMPONENTS,
    CONF_CHANNEL,
)
from .spaclient import spaclient
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import Entity


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_NAME): cv.string,
                vol.Optional(CONF_CHANNEL): cv.positive_int,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(cv.positive_int, vol.Clamp(min=MIN_SCAN_INTERVAL)),
                vol.Optional(CONF_SYNC_TIME, default=False): bool,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, base_config):
    """Configure the Spa Client component using flow only."""

    hass.data.setdefault(DOMAIN, {})

    if DOMAIN in base_config:
        for entry in base_config[DOMAIN]:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data=entry
                )
            )
    return True


async def async_setup_entry(hass, config_entry):
    """Set up Spa Client from a config entry."""

    conf = config_entry.data
    spa = spaclient(conf[CONF_HOST], conf.get(CONF_CHANNEL))
    hass.data[DOMAIN][config_entry.entry_id] = {
        SPA: spa,
        DATA_LISTENER: [config_entry.add_update_listener(update_listener)],
    }

    connected = await spa.validate_connection()
    if not connected:
        _LOGGER.error("Failed to connect to spa at %s", conf[CONF_HOST])
        raise ConfigEntryNotReady

    # await spa.send_module_identification_request()
    await spa.send_configuration_request()
    await spa.send_information_request()
    await spa.send_additional_information_request()
    await spa.send_filter_cycles_request()

    await update_listener(hass, config_entry)

    hass.loop.create_task(spa.read_all_msg())
    hass.loop.create_task(spa.keep_alive_call())

    for component in SPACLIENT_COMPONENTS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    spa.print_variables()
    return True


async def async_unload_entry(hass, config_entry) -> bool:
    """Unload a config entry."""

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in SPACLIENT_COMPONENTS
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][DATA_LISTENER]: listener()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)
        return True

    return False


async def update_listener(hass, config_entry):
    """Handle options update."""

    if config_entry.options.get(CONF_SYNC_TIME):
        spa = hass.data[DOMAIN][config_entry.entry_id][SPA]

        async def sync_time():
            while config_entry.options.get(CONF_SYNC_TIME):
                await spa.set_current_time()
                await asyncio.sleep(86400)

        hass.loop.create_task(sync_time())


class SpaClientDevice(Entity):
    """Representation of a Spa Client device."""

    def __init__(self, spaclient, config_entry):
        """Initialize the Spa Client device."""
        self._device_name = config_entry.data[CONF_NAME]
        self._spaclient = spaclient
        self._unique_id = "Spa Client"

    async def async_added_to_hass(self):
        """Register state update callback."""

    @property
    def should_poll(self) -> bool:
        """Home Assistant will poll an entity when the should_poll property returns True."""
        return True

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_info(self):
        """Return the device information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._spaclient.get_macaddr())},
            "model": self._spaclient.get_model_name(),
            "manufacturer": "Balboa Water Group",
            "name": self._device_name,
            "sw_version": self._spaclient.get_ssid(),
        }

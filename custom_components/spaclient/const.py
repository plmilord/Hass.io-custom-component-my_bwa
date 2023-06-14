"""Const file for Spa Client."""
import logging

_LOGGER = logging.getLogger(__name__)
CONF_SYNC_TIME = "sync_time"
DATA_LISTENER = "listener"
DEFAULT_SCAN_INTERVAL = 1
DOMAIN = "spaclient"
FILTER_CYCLE_TIMES = ["Begins", "Runs"]
MIN_SCAN_INTERVAL = 1
SPA = "spa"

SPACLIENT_COMPONENTS = [
    "binary_sensor",
    "climate",
    "light",
    "switch",
    "time",
]

ICONS = {
    "Auxiliary 1": "mdi:numeric-1-circle-outline",
    "Auxiliary 2": "mdi:numeric-2-circle-outline",
    "Blower": "mdi:weather-windy",
    "Circulation Pump": "mdi:fan",
    "Filter Cycle": "mdi:sync",
    "Heat Mode": "mdi:alpha-r",
    "Mister": "mdi:auto-fix",
    "Pump 1": "mdi:fan",
    "Pump 2": "mdi:fan",
    "Pump 3": "mdi:fan",
    "Pump 4": "mdi:fan",
    "Pump 5": "mdi:fan",
    "Pump 6": "mdi:fan",
    "Spa Thermostat": "mdi:hot-tub",
    "Temperature Range": "mdi:thermometer-lines",
}

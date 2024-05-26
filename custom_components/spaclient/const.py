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
    "sensor",
    "switch",
    "time",
]

FAULT_MSG = {
    15: "Sensors are out of sync",
    16: "The water flow is low",
    17: "The water flow has failed",
    18: "The settings have been reset",
    19: "Priming Mode",
    20: "The clock has failed",
    21: "The settings have been reset",
    22: "Program memory failure",
    26: "Sensors are out of sync -- Call for service",
    27: "The heater is dry",
    28: "The heater may be dry",
    29: "The water is too hot",
    30: "The heater is too hot",
    31: "Sensor A Fault",
    32: "Sensor B Fault",
    34: "A pump may be stuck on",
    35: "Hot fault",
    36: "The GFCI test failed",
    37: "Standby Mode (Hold Mode)"
}

ICONS = {
    "Auxiliary 1": "mdi:numeric-1-circle-outline",
    "Auxiliary 2": "mdi:numeric-2-circle-outline",
    "Blower": "mdi:weather-windy",
    "Circulation Pump": "mdi:fan",
    "Fault Log": "mdi:archive-alert",
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

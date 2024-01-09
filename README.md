<span align="center">

<a href="https://github.com/plmilord/Hass.io-custom-component-ikamand"><img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-ikamand/master/images/icon.png" width="150"></a>

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/plmilord/Hass.io-custom-component-ikamand.svg)](https://GitHub.com/plmilord/Hass.io-custom-component-ikamand/releases/)
[![HA integration usage](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.ikamand.total)](https://analytics.home-assistant.io/custom_integrations.json)

# Home Assistant custom component - iKamand

</span>

Since the event where Kamado Joe stopped supporting his iKamand service... I tried to find a solution to give a second life to this module and avoid the dump!

**iKamand** is based on similar projects and the work of many people. During installation, all components are created in accordance with the iKamand!

## What you need

- Kamado Joe iKamand Smart Temperature Control and Monitoring Device

### How to connect the iKamand module to your WiFi router

<span align="center">

<img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-ikamand/master/images/connect.png" width="800"></a>

</span>

## Installation

You can install this integration via [HACS](#hacs) or [manually](#manual).

### HACS

Search for the iKamand integration and choose install. Reboot Home Assistant and configure the iKamand integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ikamand)

### Manual

Copy the `custom_components/ikamand` to your custom_components folder. Reboot Home Assistant and configure the iKamand integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ikamand)

## Preview

<span align="center">

<img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-ikamand/master/images/preview_1.png" width="600"></a>

</span>

Entity | Type | Tested | Programmed entity attributes
------ | ---- | ------ | ----------------------------
iKamand | Climate | ✓ | N/A
Fan | Sensor | ✓ | N/A
Probe 1 | Sensor | ✓ | N/A
Probe 2 | Sensor | ✓ | N/A
Probe 3 | Sensor | ✓ | N/A

Option | Tested
------ | ------
Override Home Assistant unit system | Not yet implemented!

## Task List

### To do

- [ ] Bring the ability to configure this custom component via the entries in configuration.yaml
- [ ] Setup an option to override the Home Assistant unit system for this custom component

### Completed

- [x] Better error and exception handling to make this component transparent to the user
- [x] Integrate the main ```ikamand``` program to improve connectivity, better error handling and eliminate dependency
- [x] Make the sensors work properly
- [x] Support Celsius to Fahrenheit

## Inspiration / Credits

- https://github.com/slinkymanbyday/ikamand-ha | Forked project, initial inspiration!
- https://github.com/slinkymanbyday/ikamand | Main program in Python to interface the iKamand module.

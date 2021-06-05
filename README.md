<span align="center">

<a href="https://github.com/plmilord/Hass.io-custom-component-spaclient"><img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-spaclient/master/images/icon.png" width="150"></a>

# Home Assistant custom component - Spa Client

</span>

## What you need

- A Hot Tub Equipped with a Balboa BP System
- bwa™ Wi-Fi Module (50350)
- Reference : http://www.balboawatergroup.com/bwa

## Custom component setup

1-Copy these project files into your Home Assistant ```/config/custom_components``` directory.

2-Install **Spa Client** integration through the Home Assistant integrations menu (you may need to press F5 in your browser to refresh Home Assistant cache files so that it appears in the menu of available integrations).

3-Enjoy!

## Preview

<span align="center">

<a href="https://github.com/plmilord/Hass.io-custom-component-spaclient"><img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-spaclient/master/images/preview.png" width="500"></a>

<a href="https://github.com/plmilord/Hass.io-custom-component-spaclient"><img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-spaclient/master/images/options.png" width="400"></a>

</span>

## Task List

- [x] Create an icon and logo for this custom component
- [x] Allow the installation of this custom component through the Home Assistant integrations menu (use of config_flow.py)
- [ ] Allow the installation of this custom component through HACS
- [ ] Bring back the ability to configure this custom component via the entries in configuration.yaml
- [ ] Add programming capability for filter cycles
- [ ] Change the way I update entities (from polling mode to subscribing to updates)
- [ ] Customize entity IDs with **Spa Client** custom name to allow multiple integrations in the same Home Assistant instance
- [ ] Manage the availability of entities while not connected
- [ ] Implement the other spa messages (fault log, gfi test, etc.)

## Inspiration / Credits

- https://github.com/jmoor3/homeassistant-components | Forked project, initial inspiration!
- https://github.com/ccutrer/balboa_worldwide_app/wiki | Detailed Wiki on bwa protocol.
- https://github.com/garbled1/pybalboa | Main program in Python to interface the bwa module. Source of the CRC function. Very well programmed and documented!
- https://github.com/garbled1/balboa_homeassistan | Balboa Spa Client integration for Home Assistant which sit on previous ```pybalboa``` main program.
- https://github.com/vincedarley/homebridge-plugin-bwaspa | Homebridge Balboa Spa Plugin.

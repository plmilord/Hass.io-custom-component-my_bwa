<span align="center">

<a href="https://github.com/plmilord/Hass.io-custom-component-spaclient"><img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-spaclient/master/images/icon.png" width="150"></a>

# Home Assistant custom component - Spa Client

</span>

Since the event where my spa emptied when it was -30°C outside and it took me a while to find out (luckily, more fear than harm!)... I tried to find a solution to better supervise my spa! Initially, I wanted to replicate my iPhone's **Coast Spas** App in Home Assistant so that I could create notifications, track, control and automate/script some stuff. I was also looking to replicate my home automation in the **Home** App to simplify my family's access to all my different platforms. Home Assistant was the perfect fit for that!

**Spa Client** is inspired by several similar projects and the work of many people. With version 2.0, several elements have been improved in order to represent the App **Coast Spas** as faithfully as possible. During installation, all the components are created according to the configuration of your spa!

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

Several elements have already been validated (with my spa), but several remain to be validated **with your help**. The following table shows what is known to be functional: 

Entity | Type | Tested | Programmed entity attributes
------ | ---- | ------ | ----------------------------
Auxiliary 1 | Switch | ? | N/A
Auxiliary 2 | Switch | ? | N/A
Blower | Switch | ? | N/A
Circulation Pump | Binary sensor | ✓ | N/A
Filter Cycle 1 Status | Binary sensor | ✓ | Begins, Runs, Ends
Filter Cycle 2 | Switch | ✓ | N/A
Filter Cycle 2 Status | Binary sensor | ✓ | Begins, Runs, Ends
Heat Mode | Switch | ✓ | Ready, Rest, Ready in Rest
Light 1 | Light | ✓ | N/A
Light 2 | Light | ? | N/A
Mister | Switch | ? | N/A
Pump 1 | Switch | ✓ | Off, Low, High
Pump 2 | Switch | ✓ | Off, Low, High
Pump 3 | Switch | ✓ | Off, Low, High
Pump 4 | Switch | ? | Off, Low, High
Pump 5 | Switch | ? | Off, Low, High
Pump 6 | Switch | ? | Off, Low, High
Spa Thermostat | Climate | ✓ | N/A
Temperature Range | Switch | ✓ | Low, High
bwa Wi-Fi Module | Binary sensor | ✓ | N/A

Option | Tested
------ | ------
Entities polling rate (seconds) | Not yet implemented!
Time sync with Home Assistant | ✓

✓ = Tested and working properly (represents my spa options)  
? = Need your help to validate if this working properly (I don't have these options on my spa)

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

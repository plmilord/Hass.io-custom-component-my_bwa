# Hass.io custom component - Spa Client

## What you need

- A Hot Tub Equipped with a Balboa BP System
- bwa™ Wi-Fi Module (50350)
- Reference : http://www.balboawatergroup.com/bwa

## Custom component setup

1-Copy these project files into your Home Assistant ```/config``` directory.

```
custom_components/spaclient/__init__.py
custom_components/spaclient/climate.py
custom_components/spaclient/const.py
custom_components/spaclient/light.py
custom_components/spaclient/manifest.json
custom_components/spaclient/spaclient.py
custom_components/spaclient/switch.py
```

2-Edit congifuration.yaml file entry:
```
spaclient:
     spa_ip: 192.168.2.150 # Spa IP-adress, Required
     nb_toggle: 1          # 1 or 2 toggle to action the pumps (default = 1), Optional
     scan_interval: 1      # Poll the devices every x seconds (default = 1), Optional
```     

3-Restart your Hass.io. Wait few minutes (10-20 min.)... While the system installing the ```crc8``` module!

4-Restart your Hass.io. Enjoy!

## Needed python module

The ```crc8``` module is automatically installed when first used of this custom component on Hass.io.

## TODOs

- Add sensors ("Time", "Pump 1", "Pump 2", "Pump 3", "Temperature Range", "Heat Mode")
- Pursue efforts on ```const.py``` file (to centralize global variables; icons; etc.)
- Create a custom component icon and logo
- Add an automatic time synchronization function
- Add the programming capacity of the filtering cycles
- Bring more information to the user in case of connect/receive/send issues

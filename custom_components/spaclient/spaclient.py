import asyncio
import socket

from async_timeout import timeout

import homeassistant.util.dt as dt_util
from homeassistant.util.unit_conversion import TemperatureConverter

# Import the device class from the component that you want to support
from .const import _LOGGER
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from threading import Lock
from collections import deque


def retry(retries=5, timeout_s=2):
    def retry_decorator(fun):
        async def retry_with_timeout(*args, **kwargs):
            for _ in range(retries):
                try:
                    async with timeout(timeout_s):
                        return await fun(*args, **kwargs)
                except asyncio.TimeoutError:
                    pass

        return retry_with_timeout

    return retry_decorator


class spaclient:
    def __init__(self, host_ip, channel_id):
        """socket variables"""
        self.is_connected = False
        self.l = Lock()
        self.reader = None
        self.writer = None
        self.host_ip = host_ip
        self.queue = deque()
        self.channel_id = bytes([channel_id]) if channel_id else None
        self.channel_connected = False

        """ Status update variable """
        self.status_chunk_array = []

        """ Status update variables """
        self.hold_mode = False
        self.priming = False
        self.current_temp = None
        self.hour = 0
        self.minute = 0
        self.heat_mode = "Rest"
        self.temp_scale = "Farenheit"
        self.filter_mode = False
        self.time_scale = "24 Hr"
        self.heating = False
        self.temp_range = "Low"
        self.pump1 = "Off"
        self.pump2 = "Off"
        self.pump3 = "Off"
        self.pump4 = "Off"
        self.pump5 = "Off"
        self.pump6 = "Off"
        self.circ_pump = False
        self.blower = "Off"
        self.light1 = False
        self.light2 = False
        self.mister = "Off"
        self.aux1 = "Off"
        self.aux2 = "Off"
        self.set_temp = 0

        """ Information variables """
        self.model_name = "Unknown"
        self.cfg_sig = "Unknown"
        self.sw_vers = "Unknown"
        self.setup = 0
        self.ssid = "Unknown"
        self.heater_voltage = "Unknown"
        self.heater_type = "Unknown"
        self.dip_switch = "0000000000000000"
        self.information_loaded = False

        """ Configuration variables """
        self.pump_array = [0, 0, 0, 0, 0, 0]
        self.light_array = [0, 0]
        self.circ_pump_array = [0]
        self.blower_array = [0]
        self.mister_array = [0]
        self.aux_array = [0, 0]
        self.configuration_loaded = False

        """ Module identification variables """
        self.macaddr = "Unknown"
        self.idigi_device_id = "Unknown"
        self.module_identification_loaded = False

        """ Filter cycles variables """
        self.filter1_hour = 0
        self.filter1_minute = 0
        self.filter1_duration_hours = 0
        self.filter1_duration_minutes = 0
        self.filter2_enabled = 0
        self.filter2_hour = 0
        self.filter2_minute = 0
        self.filter2_duration_hours = 0
        self.filter2_duration_minutes = 0
        self.filter_cycles_loaded = False

        """ Additional information variables """
        self.low_range_min = 0
        self.low_range_max = 0
        self.high_range_min = 0
        self.high_range_max = 0
        self.nb_of_pumps = 0
        self.additional_information_loaded = False

    async def get_socket(self):
        if self.reader is None or self.writer is None or not self.is_connected:
            self.reader, self.writer = await asyncio.open_connection(self.host_ip, 4257)

        # except socket.error as e:
        #     _LOGGER.info("socket.error = %s", e)  # Validation point
        #     if e.errno != 115:
        #         self.s.close()
        #         self.is_connected = False
        #         return True

        # return True

    async def validate_connection(self):
        count = 0

        await self.get_socket()

        while count < 20 and self.is_connected != True:
            await self.read_msg()
            count += 1

        if self.is_connected == False:
            self.writer.close()
            await self.writer.wait_closed()
            self.writer = None
            self.reader = None
            return False

        async with timeout(5):
            while not self.channel_connected:
                await self.read_msg()

        if not self.channel_connected:
            self.writer.close()
            await self.writer.wait_closed()

        return self.is_connected and self.channel_connected

    def parse_status_update(self, byte_array):
        """Parse a status update from the spa.

            SSID       Length
        M100_210 V6.0    28
        M100_220 V20.0   29
        M100_201 V44.0   32

        MS: Message Start (always 0x7e "~")
        ML: Message Length
        MT: Message Type
        CS: Checksum (CRC-8 with 0x02 initial value, and 0x02 final XOR)
        ME: Message End (always 0x7e "~")

                         00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
        MS ML MT MT MT   F0 F1 CT HH MM F2 06 TA TB F3 F4 P1 P2 F5 LF F6 16 17 18 CU ST AB 22 23 M8 25 26   CS ME
        7E 20 FF AF 13                                                                                         7E

        F0: 0x00 = Running
            0x01 = Initializing
            0x05 = Hold Mode
            0x14 = A/B Temps ON?
            0x17 = Test Mode
        F1: 0x00 = Idle
            0x01 = Priming Mode
            0x02 = Post-Settings Reset?
            0x03 = Reminder
            0x04 = Stage 1?
            0x05 = Stage 3?
            0x42 = Stage 2?
        CT: Current Temperature (divide by two if in Celsius; 0xFF if unknown)
        HH: Hour (always 0-24, even in 12 hour mode; flag is used to control display)
        MM: Minute (0-59)
        F2: 0x03 = Heating Mode (0 = Ready, 1 = Rest, 3 = Ready in rest)
        06: Reminder Type (0x00 = None, 0x0A = Check the pH, 0x09 = Check the sanitizer)
        TA: Sensor A Temperature / Hold Timer (Minutes if Hold Mode else Temperature (scaled by Temperature Scale) if A/B Temps else 0x00)
        TB: Sensor B Temperature (0x00 if A/B Temps if OFF else Temperature (scaled by Temperature Scale))
        F3: 0x01 = Temperature Scale (0 = Fahrenheit, 1 = Celsius)
            0x02 = 24 Hour Time (0 = 12 hour time, 1 = 24 hour time)
            0x0c = Filter Mode (0 = OFF, 1 = Cycle 1, 2 = Cycle 2, 3 = Cycle 1 and 2)
        F4: 0x30 = Heating (0 = OFF, 1 = Heating, 2 = Heat Waiting)
            0x04 = Temperature Range (0 = Low, 1 = High)
        P1: Pump status: 0x03 for pump 1 * Valid values for each pump are 0 = OFF, 1 = Low, 2 = High
                         0x0C for pump 2 (or, shift two bits right, and then mask to 0x03)
                         0x30 for pump 3 (or, shift 4 bits right, and then mask to 0x03)
                         0xC0 for pump 4 (or, shift 6 bits right, and then mask to 0x03)
        P2: Pump status: 0x03 for pump 5
                         0xC0 for pump 6 (or, shift 6 bits right, and then mask to 0x03)
        F5: 0x02 = Circulation pump (0 = OFF, 1 = ON)
            0x0C = Blower (0 = OFF, 3 = ON)
        LF: Light 1: 0x03 == 0x03 for ON
            Light 2: 0xC0 == 0x03 for ON (or, shift 6 bits right, and then mask to 0x03)
        F6: 0x01 = Mister
            0x08 = Aux1
            0x10 = Aux2
        16: ?
        17: ?
        18: 0x00 = Reminder
            0x04 = Warning ("The settings have been reset")?
        CU: 0x00 = Clean-up Cycle (0x00 = N/A?, 0x04 = OFF, 0x0C = ON?)
            0x20 = Notification	(0 = No, 1 = Yes)
        ST: Set Temperature
        AB: 0x02 = Sensor A/B Temperatures	(0 = No, 1 = Yes)
            0x04 = Timeouts	(0 = Normal, 1 = 8h)
            0x08 = Settings Locked / Test Mode: Temp Limits	(0 = No, 1 = Yes)
        22: ?
        23: ?
        M8: M8 Cycle Time (0 = OFF, 30, 60, 90, or 120 (in minutes))
        25: ?
        26: ?

        """

        self.hold_mode = byte_array[0] & 0x05 == 1
        self.priming = byte_array[1] & 0x01 == 1
        self.current_temp = byte_array[2] if (byte_array[2] != 255) else None
        self.hour = byte_array[3]
        self.minute = byte_array[4]
        self.heat_mode = ("Ready", "Rest", "Ready in Rest")[byte_array[5]]
        flag3 = byte_array[9]
        self.temp_scale = "Fahrenheit" if (flag3 & 0x01 == 0) else "Celsius"
        self.time_scale = "12 Hr" if (flag3 & 0x02 == 0) else "24 Hr"
        self.filter_mode = (flag3 & 0x0C) >> 2
        flag4 = byte_array[10]
        self.heating = (flag4 & 0x30) >> 4
        self.temp_range = "Low" if (flag4 & 0x04) >> 2 == 0 else "High"
        self.pump1 = ("Off", "Low", "High")[byte_array[11] & 0x03]
        self.pump2 = ("Off", "Low", "High")[byte_array[11] >> 2 & 0x03]
        self.pump3 = ("Off", "Low", "High")[byte_array[11] >> 4 & 0x03]
        self.pump4 = ("Off", "Low", "High")[byte_array[11] >> 6 & 0x03]
        self.pump5 = ("Off", "Low", "High")[byte_array[12] & 0x03]
        self.pump6 = ("Off", "Low", "High")[byte_array[12] >> 6 & 0x03]
        flag5 = byte_array[13]
        self.circ_pump = flag5 & 0x02
        self.blower = "Off" if (flag5 & 0x0C) >> 2 == 0 else "On"
        self.light1 = byte_array[14] & 0x03 == 0x03
        self.light2 = byte_array[14] >> 6 & 0x03 == 0x03
        flag6 = byte_array[15]
        self.mister = "Off" if (flag6 & 0x01) == 0 else "On"
        self.aux1 = flag6 & 0x08
        self.aux2 = flag6 & 0x10
        self.set_temp = byte_array[20]

    def parse_filter_cycles_response(self, byte_array):
        """Parse filter cycles response.

                         00 01 02 03 04 05 06 07
        MS ML MT MT MT   1H 1M 1D 1E 2H 2M 2D 2E   CS ME
        7E 0D 0A BF 23                                7E

        1H: Filter 1 start hour (always 0-24)
        1M: Filter 1 start minute
        1D: Filter 1 duration hours
        1E: Filter 1 duration minutes
        2H: Filter 2 start hour, masking out the high order bit, which is used as an enable/disable flag
        2M: Filter 2 start minute
        2D: Filter 2 duration hours
        2E: Filter 2 duration minutes

        """

        self.filter1_hour = byte_array[0]
        self.filter1_minute = byte_array[1]
        self.filter1_duration_hours = byte_array[2]
        self.filter1_duration_minutes = byte_array[3]
        self.filter2_enabled = byte_array[4] >> 7
        self.filter2_hour = byte_array[4] ^ (self.filter2_enabled << 7)
        self.filter2_minute = byte_array[5]
        self.filter2_duration_hours = byte_array[6]
        self.filter2_duration_minutes = byte_array[7]

        self.filter_cycles_loaded = True

    def parse_information_response(self, byte_array):
        """Parse information response.

                         00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
        MS ML MT MT MT   I0 I1 V0 V1 M0 M1 M2 M3 M4 M5 M6 M7 SU S0 S1 S2 S3 HV HT D0 D1   CS ME
        7E 1A 0A BF 24                                                                       7E

        I0-I1: Software ID (SSID) (Displayed (in decimal) as "M<I0>_<I1> V<V0>[.<V1>]"
        V0-V1
        M0-M7: System Model Number (ASCII-encoded string)
        SU   : Current Configuration Setup Number
        S1-S3: Configuration Signature (Checksum of the system configuration file)
        HV   : Heat Voltage (0x01 = 240, other = Unknown)
        HT   : Heater Type (0x0A = Standard, other = Unknown)
        D0-D1: DIP Switch Settings (bit 0 of Byte 19 is position 1)

        """

        model = [
            byte_array[4],
            byte_array[5],
            byte_array[6],
            byte_array[7],
            byte_array[8],
            byte_array[9],
            byte_array[10],
            byte_array[11],
        ]
        model_name = "".join(map(chr, model))
        self.model_name = model_name.strip()

        self.sw_vers = f"{str(byte_array[2])}.{str(byte_array[3])}"
        self.setup = byte_array[12]
        self.ssid = f"M{str(byte_array[0])}_{str(byte_array[1])} V{self.sw_vers}"
        self.cfg_sig = (
            f"{byte_array[13]:x}{byte_array[14]:x}{byte_array[15]:x}{byte_array[16]:x}"
        )
        self.heater_voltage = 240 if byte_array[17] == 0x01 else "Unknown"
        self.heater_type = "Standard" if byte_array[18] == 0x0A else "Unknown"
        self.dip_switch = f"{byte_array[19]:08b}{byte_array[20]:08b}"

        self.information_loaded = True

    def parse_additional_information_response(self, byte_array):
        """Parse additional information response.

                         00 01 02 03 04 05 06 07 08
        MS ML MT MT MT   00 01 LL LH HL HH 06 07 08   CS ME
        7E 0E 0A BF 25                                   7E

        00: ?
        01: ?
        LL: Low Low - Low range temperature's minimum in Fahrenheit
        LH: Low High - Low range temperature's maximum in Fahrenheit
        HL: High Low - High range temperature's minimum in Fahrenheit
        HH: High High - High range temperature's maximum in Fahrenheit
        06: ?
        07: Number of pumps
        08: ?

        """

        self.low_range_min = byte_array[2]
        self.low_range_max = byte_array[3]
        self.high_range_min = byte_array[4]
        self.high_range_max = byte_array[5]

        self.nb_of_pumps = (
            (byte_array[7] & 0x01)
            + (byte_array[7] >> 1 & 0x01)
            + (byte_array[7] >> 2 & 0x01)
            + (byte_array[7] >> 3 & 0x01)
            + (byte_array[7] >> 4 & 0x01)
            + (byte_array[7] >> 5 & 0x01)
        )

        self.additional_information_loaded = True

    def parse_preferences_response(self, byte_array):
        """Parse preferences response.

                         00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17
        MS ML MT MT MT   00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17   CS ME
        7E 17 0A BF 26                                                              7E

        00: ?
        01: Reminders (0 = OFF, 1 = OFF)
        02: ?
        03: Temperature Scale (0 = 1°F, 1 = 0.5°C)
        04: Clock Mode (0 = 12-hour, 1 = 24-hour)
        05: Clean-up Cycle (0 = OFF, 1-8 (30 minute increments))
        06: Dolphin Address (0 = None, 1-7 = Address)
        07: ?
        08: M8 Artificial Intelligence (0 = OFF, 1 = ON)
        09-17: ?

        """

        return True

    def parse_fault_log_response(self, byte_array):
        """Parse fault log response.

                         00 01 02 03 04 05 06 07 08 09
        MS ML MT MT MT   00 01 02 03 04 05 06 07 08 09   CS ME
        7E 0F 0A BF 28                                      7E

        00: Total Entries (0-24)
        01: Entry Number (0-23 (0=Entry #1))
        02: Message Code
        03: Days Ago (0-255?)
        04: Time: Hour (0-24)
        05: Time: Minute (0-59)
        06: Flags TODO
        07: Set Temperature (Temperature scaled by Temperature Scale)
        08: Sensor A Temperature (Temperature scaled by Temperature Scale)
        09: Sensor B Temperature (Temperature scaled by Temperature Scale)

        """

        return True

    def parse_gfci_test_response(self, byte_array):
        """Parse fault log response.

                         00
        MS ML MT MT MT   00   CS ME
        7E 06 0A BF 2B           7E

        00: 0x00 = N/A ? or FAIL?
            0x01 = PASS

        """

        return True

    def parse_configuration_response(self, byte_array):
        """Parse a panel config response.

                         00 01 02 03 04 05
        MS ML MT MT MT   00 01 02 03 04 05   CS ME
        7E 0B 0A BF 2E                          7E

        00: P4P3P2P1 - Pumps 1-4 (0 = None, 1 = 1-speed, 2 = 2-speed)
        01: P6xxxxP5 - Pumps 5-6 (0 = None, 1 = 1-speed, 2 = 2-speed)
        02: L2xxxxL1 - Lights (0 = None, 1 = Present)
        03: CxxxxxBL - Circulation pump, Blower (0 = None, 1 = Present)
        04: xxMIxxAA - Mister, Aux2, Aux1 (0 = None, 1 = Present)
        05: ?

        """

        self.pump_array[0] = int((byte_array[0] & 0x03))
        self.pump_array[1] = int((byte_array[0] & 0x0C) >> 2)
        self.pump_array[2] = int((byte_array[0] & 0x30) >> 4)
        self.pump_array[3] = int((byte_array[0] & 0xC0) >> 6)
        self.pump_array[4] = int((byte_array[1] & 0x03))
        self.pump_array[5] = int((byte_array[1] & 0xC0) >> 6)

        self.light_array[0] = int((byte_array[2] & 0x03) != 0)
        self.light_array[1] = int((byte_array[2] & 0xC0) != 0)

        self.circ_pump_array[0] = int((byte_array[3] & 0x80) != 0)
        self.blower_array[0] = int((byte_array[3] & 0x03) != 0)
        self.mister_array[0] = int((byte_array[4] & 0x30) != 0)

        self.aux_array[0] = int((byte_array[4] & 0x01) != 0)
        self.aux_array[1] = int((byte_array[4] & 0x02) != 0)

        self.configuration_loaded = True

    def parse_module_identification_response(self, byte_array):
        """Parse a module identification response.

                         00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
        MS ML MT MT MT   00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24   CS ME
        7E 1E 0A BF 94                                                                                   7E

        00-02: ?
        03-08: MAC address
        09-24: iDigi device id (used to communicate with Balboa cloud API)

        """

        self.macaddr = f"{byte_array[3]:02x}:{byte_array[4]:02x}:{byte_array[5]:02x}:{byte_array[6]:02x}:{byte_array[7]:02x}:{byte_array[8]:02x}"
        self.idigi_device_id = f"{byte_array[9:13].hex()}-{byte_array[13:17].hex()}-{byte_array[17:21].hex()}-{byte_array[21:25].hex()}".upper()

        self.module_identification_loaded = True

    def get_current_temp(self):
        return self.current_temp

    def get_current_time(self):
        return "%d:%02d" % (self.hour, self.minute)

    def get_heat_mode(self):
        return self.heat_mode

    def get_heating(self):
        return self.heating

    def get_temp_range(self):
        return self.temp_range

    def get_pump(self, pump_num):
        if pump_num == 1:
            return self.get_pump1()
        elif pump_num == 2:
            return self.get_pump2()
        elif pump_num == 3:
            return self.get_pump3()
        elif pump_num == 4:
            return self.get_pump4()
        elif pump_num == 5:
            return self.get_pump5()
        else:
            return self.get_pump6()

    def get_pump1(self):
        return self.pump1

    def get_pump2(self):
        return self.pump2

    def get_pump3(self):
        return self.pump3

    def get_pump4(self):
        return self.pump4

    def get_pump5(self):
        return self.pump5

    def get_pump6(self):
        return self.pump6

    def get_circ_pump(self):
        return self.circ_pump

    def get_blower(self):
        return self.blower

    def get_light(self, light_num):
        if light_num == 1:
            return self.get_light1()
        else:
            return self.get_light2()

    def get_light1(self):
        return self.light1

    def get_light2(self):
        return self.light2

    def get_mister(self):
        return self.mister

    def get_aux(self, aux_num):
        if aux_num == 1:
            return self.get_aux1()
        else:
            return self.get_aux2()

    def get_aux1(self):
        return self.aux1

    def get_aux2(self):
        return self.aux2

    def get_set_temp(self):
        return self.set_temp

    def get_low_range_min(self):
        return self.low_range_min

    def get_low_range_max(self):
        return self.low_range_max

    def get_high_range_min(self):
        return self.high_range_min

    def get_high_range_max(self):
        return self.high_range_max

    def get_pump_list(self):
        return self.pump_array

    def get_light_list(self):
        return self.light_array

    def get_circ_pump_list(self):
        return self.circ_pump_array

    def get_blower_list(self):
        return self.blower_array

    def get_mister_list(self):
        return self.mister_array

    def get_aux_list(self):
        return self.aux_array

    def get_model_name(self):
        return self.model_name

    def get_ssid(self):
        return self.ssid

    def get_macaddr(self):
        return self.macaddr

    def get_gateway_status(self):
        return self.is_connected

    def get_filter2_enabled(self):
        return self.filter2_enabled

    def get_filter_begins(self, filter_num):
        if filter_num == 1:
            return "%02d:%02d" % (self.filter1_hour, self.filter1_minute)
        else:
            return "%02d:%02d" % (self.filter2_hour, self.filter2_minute)

    def get_filter_runs(self, filter_num):
        if filter_num == 1:
            return f"{self.filter1_duration_hours} hours | {self.filter1_duration_minutes} minutes"
        else:
            return f"{self.filter2_duration_hours} hours | {self.filter2_duration_minutes} minutes"

    def get_filter_ends(self, filter_num):
        if filter_num == 1:
            if self.filter1_hour + self.filter1_duration_hours >= 24:
                return "%02d:%02d" % (
                    self.filter1_hour + self.filter1_duration_hours - 24,
                    self.filter1_minute + self.filter1_duration_minutes,
                )
            return "%02d:%02d" % (
                self.filter1_hour + self.filter1_duration_hours,
                self.filter1_minute + self.filter1_duration_minutes,
            )
        else:
            if self.filter2_hour + self.filter2_duration_hours >= 24:
                return "%02d:%02d" % (
                    self.filter2_hour + self.filter2_duration_hours - 24,
                    self.filter2_minute + self.filter2_duration_minutes,
                )
            return "%02d:%02d" % (
                self.filter2_hour + self.filter2_duration_hours,
                self.filter2_minute + self.filter2_duration_minutes,
            )

    def get_filter_mode(self, filter_num):
        if filter_num == 1:
            if self.filter_mode == 1 or self.filter_mode == 3:
                return True
        else:
            if self.filter_mode == 2 or self.filter_mode == 3:
                return True
        return False

    def compute_checksum(self, length, payload):
        crc = 0xB5
        for cur in range(length):
            for i in range(8):
                bit = crc & 0x80
                crc = ((crc << 1) & 0xFF) | ((payload[cur] >> (7 - i)) & 0x01)
                if bit:
                    crc = crc ^ 0x07
            crc &= 0xFF
        for i in range(8):
            bit = crc & 0x80
            crc = (crc << 1) & 0xFF
            if bit:
                crc ^= 0x07
        return crc ^ 0x02

    async def read_msg(self):
        acqruired = self.l.acquire(True, 5)

        if not acqruired:
            raise Exception("Could not acquire lock")
        try:
            len_chunk = await self.reader.readexactly(2)
        except IOError as e:
            # _LOGGER.info("1. read_msg - e.errno = %s", e) #Validation point
            self.l.release()
            return True

        if len_chunk == b"~" or len_chunk == b"" or len(len_chunk) == 0:
            # _LOGGER.info("2. read_msg - len_chunk = %s ; len(len_chunk) = %s", len_chunk, len(len_chunk)) #Validation point
            self.l.release()
            return True

        if len(len_chunk) == 1:
            _LOGGER.info("Invalid message %s", hex(len_chunk))
            self.l.release()
            return True

        length = len_chunk[1]

        if int(length) == 0:
            # _LOGGER.info("3. read_msg - int(length) = 0") #Validation point
            self.l.release()
            return True

        try:
            chunk = await self.reader.readexactly(length)
        except IOError as e:
            # _LOGGER.info("4. read_msg - e.errno = %s", e) #Validation point
            if e.errno != 11:
                self.get_socket()
            self.l.release()
            return True

        self.l.release()

        if len(chunk) != length:
            return True

        data = chunk[:-2]

        message = bytes([length]) + data
        crc = chunk[-2]

        calculated_crc = self.compute_checksum(len(message), message)

        if crc != calculated_crc:
            _LOGGER.warning("Invalid CRC %s", chunk.hex())
            return True

        if chunk != self.status_chunk_array:
            if not self.channel_connected or not self.channel_id:
                if chunk[0] == 0xFE and chunk[2] == 2:
                    self.channel_id = bytes([chunk[3]])
                    _LOGGER.info(
                        "Client ID Response for channel %s", str(self.channel_id)
                    )
                    if self.channel_id[0] > 0x2F:
                        self.channel_id = bytes([0x2F])

                    await self.send_message_sync(
                        self.channel_id + b"\xbf\x03", bytes([])
                    )

                if chunk[0] == 0xFE and chunk[2] == 0:
                    _LOGGER.info("New client request. Requesting channel")

                    await self.send_message_sync(b"\xfe\xbf\x01", b"\x02\xf1\x73")
            if chunk[0:3] == b"\xff\xaf\x13" and (
                (
                    self.configuration_loaded
                    and self.information_loaded
                    and self.additional_information_loaded
                )
                or (self.is_connected == False)
            ):
                # _LOGGER.info("Status update = %s", chunk[3:]) #Validation point
                self.parse_status_update(chunk[3:])
                self.status_chunk_array = chunk
                self.is_connected = True
                return True

            if self.channel_id and chunk[0] == self.channel_id[0]:
                if chunk[1:3] == b"\xbf\x23":
                    # _LOGGER.info("Filter cycles response = %s", chunk[3:]) #Validation point
                    self.parse_filter_cycles_response(chunk[3:])
                    return True

                if chunk[1:3] == b"\xbf\x24" and self.information_loaded != True:
                    # _LOGGER.info("Information response = %s", chunk[3:]) #Validation point
                    self.parse_information_response(chunk[3:])
                    return True

                if (
                    chunk[1:3] == b"\xbf\x25"
                    and self.additional_information_loaded != True
                ):
                    # _LOGGER.info("Additional information response = %s", chunk[3:]) #Validation point
                    self.parse_additional_information_response(chunk[3:])
                    return True

                if chunk[1:3] == b"\xbf\x26":
                    # _LOGGER.info("Preferences response = %s", chunk[3:]) #Validation point
                    self.parse_preferences_response(chunk[3:])
                    return True

                if chunk[1:3] == b"\xbf\x28":
                    # _LOGGER.info("Fault log response = %s", chunk[3:]) #Validation point
                    self.parse_fault_log_response(chunk[3:])
                    return True

                if chunk[1:3] == b"\xbf\x2b":
                    # _LOGGER.info("GFCI test response = %s", chunk[3:]) #Validation point
                    self.parse_gfci_test_response(chunk[3:])
                    return True

                if chunk[1:3] == b"\xbf\x2e" and self.configuration_loaded != True:
                    # _LOGGER.info("Configuration response = %s", chunk[3:]) #Validation point
                    self.parse_configuration_response(chunk[3:])
                    return True

                if (
                    chunk[1:3] == b"\xbf\x94"
                    and self.module_identification_loaded != True
                ):
                    # _LOGGER.info("Module identification response = %s", chunk[3:]) #Validation point
                    self.parse_module_identification_response(chunk[3:])
                    return True

                # Clear to send for us
                if chunk[2] == 6:
                    self.channel_connected = True
                    if self.queue:
                        message = self.queue.pop()
                        self.writer.write(message)
                        # TODO: highwatermark
                        await self.writer.drain()
                        return True

        return True

    async def read_all_msg(self):
        while True:
            try:
                await self.read_msg()
                await asyncio.sleep(0.01)
            except Exception:
                _LOGGER.exception("Read message error")

    def send_message(self, message_type, payload):
        length = 5 + len(payload)
        checksum = self.compute_checksum(
            length - 1, bytes([length]) + message_type + payload
        )
        prefix = b"\x7e"
        message = (
            prefix
            + bytes([length])
            + message_type
            + payload
            + bytes([checksum])
            + prefix
        )

        self.queue.append(message)

    async def send_message_sync(self, message_type, payload):
        length = 5 + len(payload)
        checksum = self.compute_checksum(
            length - 1, bytes([length]) + message_type + payload
        )
        prefix = b"\x7e"
        message = (
            prefix
            + bytes([length])
            + message_type
            + payload
            + bytes([checksum])
            + prefix
        )

        self.writer.write(message)
        await self.writer.drain()

    async def write(self, message):
        # _LOGGER.info("send_message : %s", message) #Validation point
        self.writer.write(message)
        await self.writer.drain()

    async def send_module_identification_request(self):
        self.send_message(self.channel_id + b"\xbf\x04", bytes([]))
        while self.module_identification_loaded == False:
            await asyncio.sleep(0.05)

    async def keep_alive_call(self):
        while True:
            self.send_message(self.channel_id + b"\xbf\x04", bytes([]))
            await asyncio.sleep(30)

    def send_toggle_message(self, item):
        self.send_message(self.channel_id + b"\xbf\x11", bytes([item]) + b"\x00")

    @retry()
    async def set_temperature(self, temp):
        if self.temp_scale == "Celsius":
            temp = round(TemperatureConverter.convert(temp, TEMP_FAHRENHEIT, TEMP_CELSIUS) * 2)
        self.send_message(self.channel_id + b"\xbf\x20", bytes([int(temp)]))
        while self.set_temp != temp:
            await asyncio.sleep(0.05)

    async def set_current_time(self):
        now = dt_util.utcnow()
        now = dt_util.as_local(now)
        if self.time_scale == "24 Hr":
            self.send_message(
                self.channel_id + b"\xbf\x21",
                bytes([128 + now.hour]) + bytes([now.minute]),
            )
        else:
            self.send_message(
                self.channel_id + b"\xbf\x21",
                bytes([now.hour]) + bytes([now.minute]),
            )

    @retry()
    async def send_configuration_request(self):
        self.send_message(self.channel_id + b"\xbf\x22", b"\x00" + b"\x00" + b"\x01")
        while self.configuration_loaded == False:
            await asyncio.sleep(0.05)

    @retry()
    async def send_filter_cycles_request(self):
        self.send_message(self.channel_id + b"\xbf\x22", b"\x01" + b"\x00" + b"\x00")
        while self.filter_cycles_loaded == False:
            await asyncio.sleep(0.05)

    @retry()
    async def send_information_request(self):
        self.send_message(self.channel_id + b"\xbf\x22", b"\x02" + b"\x00" + b"\x00")
        while self.information_loaded == False:
            await asyncio.sleep(0.05)

    @retry()
    async def send_additional_information_request(self):
        self.send_message(self.channel_id + b"\xbf\x22", b"\x04" + b"\x00" + b"\x00")
        while self.additional_information_loaded == False:
            await asyncio.sleep(0.05)

    def send_preferences_request(self):  # Not use yet!
        self.send_message(self.channel_id + b"\xbf\x22", b"\x08" + b"\x00" + b"\x00")

    def send_fault_log_request(self):  # Not use yet!
        self.send_message(self.channel_id + b"\xbf\x22", b"\x20" + b"\x00" + b"\x00")

    def send_gfci_test_request(self):  # Not use yet!
        self.send_message(self.channel_id + b"\xbf\x22", b"\x80" + b"\x00" + b"\x00")

    def send_filter_cycle_config(self):  # Not use yet!
        self.send_message(
            self.channel_id + b"\xbf\x23",
            bytes([self.filter1_hour])
            + bytes([self.filter1_minute])
            + bytes([self.filter1_duration_hours])
            + bytes([self.filter1_duration_minutes])
            + bytes([int(self.filter2_enabled << 7) + self.filter2_hour])
            + bytes([self.filter2_minute])
            + bytes([self.filter2_duration_hours])
            + bytes([self.filter2_duration_minutes]),
        )

    def set_temperature_scale(self, temperature_scale):  # Not use yet!
        self.send_message(self.channel_id + b"\xbf\x27", bytes([]) + bytes([]))

    def set_pump(self, pump_num, value):
        pump_val = self.pump1
        pump_code = 0x04
        if pump_num == 2:
            pump_val = self.pump2
            pump_code = 0x05
        if pump_num == 3:
            pump_val = self.pump3
            pump_code = 0x06
        if pump_num == 4:
            pump_val = self.pump4
            pump_code = 0x07
        if pump_num == 5:
            pump_val = self.pump5
            pump_code = 0x08
        if pump_num == 6:
            pump_val = self.pump6
            pump_code = 0x09
        if pump_val == value:
            return
        self.send_toggle_message(pump_code)
        if pump_num == 1:
            self.pump1 = value
        if pump_num == 2:
            self.pump2 = value
        if pump_num == 3:
            self.pump3 = value
        if pump_num == 4:
            self.pump4 = value
        if pump_num == 5:
            self.pump5 = value
        if pump_num == 6:
            self.pump6 = value

    def set_blower(self, value):
        if self.blower == value:
            return
        self.send_toggle_message(0x0C)
        self.blower = value

    def set_mister(self, value):
        if self.mister == value:
            return
        self.send_toggle_message(0x0E)
        self.mister = value

    def set_light(self, light_num, value):
        light_val = self.light1
        light_code = 0x11
        if light_num == 2:
            light_val = self.light2
            light_code = 0x12
        if light_val == value:
            return
        self.send_toggle_message(light_code)
        if light_num == 1:
            self.light1 = value
        if light_num == 2:
            self.light2 = value

    def set_aux(self, aux_num, value):
        aux_val = self.aux1
        aux_code = 0x16
        if aux_num == 2:
            aux_val = self.aux2
            aux_code = 0x17
        if aux_val == value:
            return
        self.send_toggle_message(aux_code)
        if aux_num == 1:
            self.aux1 = value
        if aux_num == 2:
            self.aux2 = value

    def set_hold_mode(self, value):
        if self.hold_mode == value:
            return
        self.send_toggle_message(0x3C)
        self.hold_mode = value

    @retry()
    async def set_temp_range(self, value):
        if self.temp_range == value:
            return
        self.send_toggle_message(0x50)

        while self.temp_range != value:
            await asyncio.sleep(0.05)
        self.temp_range = value

    @retry()
    async def set_heat_mode(self, value):
        if self.heat_mode == value:
            return

        self.send_toggle_message(0x51)

        while self.heat_mode != value:
            await asyncio.sleep(0.05)

        self.heat_mode = value

    def set_filter2_enabled(self, value):
        self.filter2_enabled = value
        self.send_filter_cycle_config()

    def print_variables(self):
        _LOGGER.info("")
        _LOGGER.info("======================")
        _LOGGER.info("<< socket variables >>")
        _LOGGER.info("======================")
        _LOGGER.info("self.is_connected = %s", self.is_connected)
        _LOGGER.info("self.l       = %s", self.l)
        _LOGGER.info("self.writer       = %s", self.writer)
        _LOGGER.info("self.reader       = %s", self.reader)
        _LOGGER.info("self.host_ip = %s", self.host_ip)

        _LOGGER.info("")
        _LOGGER.info("=============================")
        _LOGGER.info("<< Status update variables >>")
        _LOGGER.info("=============================")
        _LOGGER.info("self.hold_mode    = %s", self.hold_mode)
        _LOGGER.info("self.priming      = %s", self.priming)
        _LOGGER.info("self.current_temp = %s", self.current_temp)
        _LOGGER.info("self.hour         = %s", self.hour)
        _LOGGER.info("self.minute       = %s", self.minute)
        _LOGGER.info("self.heat_mode    = %s", self.heat_mode)
        _LOGGER.info("self.temp_scale   = %s", self.temp_scale)
        _LOGGER.info("self.filter_mode  = %s", self.filter_mode)
        _LOGGER.info("self.time_scale   = %s", self.time_scale)
        _LOGGER.info("self.heating      = %s", self.heating)
        _LOGGER.info("self.temp_range   = %s", self.temp_range)
        _LOGGER.info("self.pump1        = %s", self.pump1)
        _LOGGER.info("self.pump2        = %s", self.pump2)
        _LOGGER.info("self.pump3        = %s", self.pump3)
        _LOGGER.info("self.pump4        = %s", self.pump4)
        _LOGGER.info("self.pump5        = %s", self.pump5)
        _LOGGER.info("self.pump6        = %s", self.pump6)
        _LOGGER.info("self.circ_pump    = %s", self.circ_pump)
        _LOGGER.info("self.blower       = %s", self.blower)
        _LOGGER.info("self.light1       = %s", self.light1)
        _LOGGER.info("self.light2       = %s", self.light2)
        _LOGGER.info("self.mister       = %s", self.mister)
        _LOGGER.info("self.aux1         = %s", self.aux1)
        _LOGGER.info("self.aux2         = %s", self.aux2)
        _LOGGER.info("self.set_temp     = %s", self.set_temp)

        _LOGGER.info("")
        _LOGGER.info("===========================")
        _LOGGER.info("<< Information variables >>")
        _LOGGER.info("===========================")
        _LOGGER.info("self.information_loaded = %s", self.information_loaded)
        _LOGGER.info("self.model_name     = %s", self.model_name)
        _LOGGER.info("self.cfg_sig        = %s", self.cfg_sig)
        _LOGGER.info("self.sw_vers        = %s", self.sw_vers)
        _LOGGER.info("self.setup          = %s", self.setup)
        _LOGGER.info("self.ssid           = %s", self.ssid)
        _LOGGER.info("self.heater_voltage = %s", self.heater_voltage)
        _LOGGER.info("self.heater_type    = %s", self.heater_type)
        _LOGGER.info("self.dip_switch     = %s", self.dip_switch)

        _LOGGER.info("")
        _LOGGER.info("=============================")
        _LOGGER.info("<< Configuration variables >>")
        _LOGGER.info("=============================")
        _LOGGER.info("self.configuration_loaded = %s", self.configuration_loaded)
        _LOGGER.info("self.pump_array      = %s", self.pump_array)
        _LOGGER.info("self.light_array     = %s", self.light_array)
        _LOGGER.info("self.circ_pump_array = %s", self.circ_pump_array)
        _LOGGER.info("self.blower_array    = %s", self.blower_array)
        _LOGGER.info("self.mister_array    = %s", self.mister_array)
        _LOGGER.info("self.aux_array       = %s", self.aux_array)

        _LOGGER.info("")
        _LOGGER.info("=====================================")
        _LOGGER.info("<< Module identification variables >>")
        _LOGGER.info("=====================================")
        _LOGGER.info(
            "self.module_identification_loaded = %s", self.module_identification_loaded
        )
        _LOGGER.info("self.macaddr         = %s", self.macaddr)
        _LOGGER.info("self.idigi_device_id = %s", self.idigi_device_id)

        _LOGGER.info("")
        _LOGGER.info("=============================")
        _LOGGER.info("<< Filter cycles variables >>")
        _LOGGER.info("=============================")
        _LOGGER.info("self.filter_cycles_loaded = %s", self.filter_cycles_loaded)
        _LOGGER.info("self.filter1_hour             = %s", self.filter1_hour)
        _LOGGER.info("self.filter1_minute           = %s", self.filter1_minute)
        _LOGGER.info("self.filter1_duration_hours   = %s", self.filter1_duration_hours)
        _LOGGER.info(
            "self.filter1_duration_minutes = %s", self.filter1_duration_minutes
        )
        _LOGGER.info("self.filter2_enabled          = %s", self.filter2_enabled)
        _LOGGER.info("self.filter2_hour             = %s", self.filter2_hour)
        _LOGGER.info("self.filter2_minute           = %s", self.filter2_minute)
        _LOGGER.info("self.filter2_duration_hours   = %s", self.filter2_duration_hours)
        _LOGGER.info(
            "self.filter2_duration_minutes = %s", self.filter2_duration_minutes
        )

        _LOGGER.info("")
        _LOGGER.info("======================================")
        _LOGGER.info("<< Additional information variables >>")
        _LOGGER.info("======================================")
        _LOGGER.info(
            "self.additional_information_loaded = %s",
            self.additional_information_loaded,
        )
        _LOGGER.info("self.low_range_min  = %s", self.low_range_min)
        _LOGGER.info("self.low_range_max  = %s", self.low_range_max)
        _LOGGER.info("self.high_range_min = %s", self.high_range_min)
        _LOGGER.info("self.high_range_max = %s", self.high_range_max)
        _LOGGER.info("self.nb_of_pumps    = %s", self.nb_of_pumps)
        _LOGGER.info("")

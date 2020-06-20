import crc8
import logging
import schedule
import socket

# Import the device class from the component that you want to support
from threading import Lock
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.util.temperature import convert as convert_temperature
import homeassistant.util.dt as dt_util

_LOGGER = logging.getLogger(__name__)

class spaclient:
    def __init__(self, socket):
        self.s = socket
        self.light = 0
        self.current_temp = 100
        self.hour = 10
        self.minute = 0
        self.heat_mode = "Ready"
        self.temp_scale = "Farenheit"
        self.temp_range = "High"
        self.pump1 = "Off"
        self.pump2 = "Off"
        self.pump3 = "Off"
        self.set_temp = 100
        self.priming = False
        self.time_scale = "24 Hr"
        self.heating = False
        self.circ_pump = False

        schedule.every().minute.at(':05').do(self.send_config_request)
        schedule.every().hour.at(':05').do(self.set_current_time)

        self.read_all_msg()

    s = None
    ip = None
    l = Lock()
    
    @staticmethod
    def get_socket(host_ip = None):
        if (host_ip):
            spaclient.ip = host_ip
        if spaclient.s is None:
            spaclient.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            spaclient.s.setblocking(0)

        try:
            spaclient.s.connect((spaclient.ip, 4257))
        except socket.error as e:
            if e.errno != 115:
                spaclient.s.close()

        return spaclient.s

    def reconnect_socket():
        spaclient.s = None
        return spaclient.get_socket()

    def handle_status_update(self, byte_array):
        self.priming = byte_array[1] & 0x01 == 1
        self.current_temp = byte_array[2] if (byte_array[2] != 255) else None
        self.hour = byte_array[3]
        self.minute = byte_array[4]
        self.heat_mode = ("Ready", "Rest", "Ready in Rest")[byte_array[5]]
        flag3 = byte_array[9]
        self.temp_scale = "Fahrenheit" if (flag3 & 0x01 == 0) else "Celsius"
        self.time_scale = "12 Hr" if (flag3 & 0x02 == 0) else "24 Hr"
        flag4 = byte_array[10]
        self.heating = flag4 & 0x30
        self.temp_range = "Low" if (flag4 & 0x04 == 0) else "High"
        pump_status = byte_array[11]
        self.pump1 = ("Off", "Low", "High")[pump_status & 0x03]
        self.pump2 = ("Off", "Low", "High")[pump_status >> 2 & 0x03]
        self.pump3 = ("Off", "Low", "High")[pump_status >> 4 & 0x03]
        self.circ_pump = byte_array[13] & 0x02 == 1
        self.light = byte_array[14] & 0x03 == 0x03
        self.set_temp = byte_array[20]
        if self.temp_scale == "Celsius":
            self.set_temp = convert_temperature(self.set_temp / 2, TEMP_CELSIUS, TEMP_FAHRENHEIT)
            if self.current_temp != None:
                self.current_temp = convert_temperature(self.current_temp / 2, TEMP_CELSIUS, TEMP_FAHRENHEIT)

    def get_set_temp(self):
        return self.set_temp

    def get_pump(self, pump_num):
        if pump_num == 1:
            return self.get_pump1()
        elif pump_num == 2:
            return self.get_pump2()
        else:
            return self.get_pump3()

    def get_pump1(self):
        return self.pump1

    def get_pump2(self):
        return self.pump2

    def get_pump3(self):
        return self.pump3

    def get_heating(self):
        return self.heating

    def get_heat_mode(self):
        return self.heat_mode

    def get_temp_range(self):
        return self.temp_range

    def get_current_time(self):
        return "%d:%02d" % (self.hour, self.minute)

    def get_light(self):
        return self.light

    def get_current_temp(self):
        return self.current_temp

    def string_status(self):
        s = ""
        s = s + "Temp: %d, Set Temp: %d, Time: %d:%02d\n" % \
            (self.current_temp, self.set_temp, self.hour, self.minute)
        s = s + "Priming: %s, Heating Mode: %s Temp Scale: %s, Time Scale: %s\n" % \
            (self.priming, self.heat_mode, self.temp_scale, self.time_scale)
        s = s + "Heating: %s, Temp Range: %s, Pump1: %s, Pump2: %s, Pump3: %s, Circ Pump: %s, Light: %s\n" % \
            (self.heating, self.temp_range, self.pump1, self.pump2, self.pump3, self.circ_pump, self.light)
        return s

    def compute_checksum(self, len_bytes, bytes):
        hash = crc8.crc8()
        hash._sum = 0x02
        hash.update(len_bytes)
        hash.update(bytes)
        checksum = hash.digest()[0]
        checksum = checksum ^ 0x02
        return checksum

    def read_msg(self):
        spaclient.l.acquire()

        try:
            len_chunk = spaclient.s.recv(2)
        except IOError as e:
            #_LOGGER.info("1. False - e.errno = %s", e.errno) #Validation point
            if e.errno != 11:
                spaclient.s = spaclient.reconnect_socket()
            spaclient.l.release()
            return False

        if len_chunk == b'' or len(len_chunk) == 0:
            #_LOGGER.info("2. False - len_chunk = %s ; len(len_chunk) = %s", len_chunk, len(len_chunk)) #Validation point
            spaclient.l.release() #Addition...
            return False

        length = len_chunk[1]

        if int(length) == 0:
            #_LOGGER.info("3. False - int(length) = 0") #Validation point
            spaclient.l.release()
            return False

        try:
            chunk = spaclient.s.recv(length)
        except IOError as e:
            #_LOGGER.info("4. False - e.errno = %s", e.errno) #Validation point
            if e.errno != 11:
                spaclient.s = spaclient.reconnect_socket()
            spaclient.l.release()
            return False

        spaclient.l.release()

        if chunk[0:3] == b'\xff\xaf\x13':
            #_LOGGER.info("5. True - chunk[:] = %s", chunk[:]) #Validation point
            self.handle_status_update(chunk[3:])

        return True

    def read_all_msg(self):
        schedule.run_pending()
        while (self.read_msg()):
            True

    def send_message(self, type, payload):
        _LOGGER.info("payload = %s", payload) #Validation point
        length = 5 + len(payload)
        checksum = self.compute_checksum(bytes([length]), type + payload)
        prefix = b'\x7e'
        message = prefix + bytes([length]) + type + payload + \
            bytes([checksum]) + prefix

        try:
            spaclient.s.send(message)
        except IOError as e:
            spaclient.s = spaclient.reconnect_socket()
            spaclient.s.send(message)

    def send_config_request(self):
        self.send_message(b'\x0a\xbf\x04', bytes([]))

    def send_toggle_message(self, item):
        self.send_message(b'\x0a\xbf\x11', bytes([item]) + b'\x00')

    def set_temperature(self, temp):
        self.set_temp = int(temp)
        if self.temp_scale == "Celsius":
            temp = convert_temperature(temp, TEMP_FAHRENHEIT, TEMP_CELSIUS) * 2
        self.send_message(b'\x0a\xbf\x20', bytes([int(temp)]))

    def set_current_time(self):
        now = dt_util.utcnow()
        now = dt_util.as_local(now)
        if self.time_scale == "24 Hr":
            self.send_message(b'\x0a\xbf\x21', bytes([128 + now.hour]) + bytes([now.minute]))
        else:
            self.send_message(b'\x0a\xbf\x21', bytes([now.hour]) + bytes([now.minute]))

    def set_light(self, value):
        if self.light == value:
            return
        self.send_toggle_message(0x11)
        self.light = value

    def set_pump(self, pump_num, value, nb_toggle):
        pump_val = self.pump1
        pump_code = 0x04
        if pump_num == 2:
            pump_val = self.pump2
            pump_code = 0x05
        if pump_num == 3:
            pump_val = self.pump3
            pump_code = 0x06
        if pump_val == value:
            return
        self.send_toggle_message(pump_code)
        if nb_toggle == 2:
            self.send_toggle_message(pump_code)
        if pump_num == 1:
            self.pump1 = value
        if pump_num == 2:
            self.pump2 = value
        if pump_num == 3:
            self.pump3 = value

    def set_heat_mode(self, value):
        if self.heat_mode == value:
            return
        self.send_toggle_message(0x51)
        self.heat_mode = value

    def set_temp_range(self, value):
        if self.temp_range == value:
            return
        self.send_toggle_message(0x50)
        self.temp_range = value

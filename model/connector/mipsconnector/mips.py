import sys
import glob
import serial
from model.connector.mipsconnector.serialportconnector import SerialPortConnector

class MIPS(object):
    def __init__(self):
        self.connector = SerialPortConnector()

    def connect(self, portName = "", baudRate = 115200, parity = serial.PARITY_NONE, stopBits = serial.STOPBITS_ONE, flowControl = serial.SEVENBITS):
        return self.connector.connect(portName, baudRate, parity, stopBits, flowControl)

    def disconnect(self):
        self.connector.disconnect()

    def is_open(self):
        return self.connector.is_open()

    def send_command(self, inputData):
        return self.connector.send_command(inputData)

    def send_message(self, inputData):
        return self.connector.send_message(inputData)

    def check_power(self):
        return self.send_message(b'GDCPWR\n')

    def set_power(self, state):
        if state:
            return self.send_command(b'SDCPWR,ON\n')
        else:
            return self.send_command(b'SDCPWR,OFF\n')

    def get_emission_current(self):
        return float(self.send_message(b'GFLECUR\n'))

    def get_number_of_channels(self):
        return int(float(self.send_message(b'GCHAN,DCB\n')))

    def get_firmware_version(self):
        return self.send_message(b'GVER\n')

    # Return the actual voltage measured on channel (actual sampling)
    def get_channel_measured_voltage(self, channel):
        return float(self.send_message(b'GDCBV,%d\n' % channel))

    # Return the current voltage setting programmed for the channel (target voltage)
    def get_channel_programmed_voltage(self, channel):
        return float(self.send_message(b'GDCB,%d\n' % channel))

    # Program a new voltage target for the channel
    def set_channel_programmed_voltage(self, channel, value):
        return self.send_command(b'SDCB,%d,%f\n' % (channel, value))

    def get_offset_voltage(self, channel):
        return int(float(self.send_message(b'GDCBOF,%d\n' % channel)))

    def get_max_range(self, channel):
        return int(float(self.send_message(b'GDCMAX,%d\n' % channel)))

    def get_min_range(self, channel):
        return int(float(self.send_message(b'GDCMIN,%d\n' % channel)))

    def set_offset_voltage(self, channel, value):
        return self.send_command(b'SDCBOF,%d,%d\n' % (channel, value))

    def check_filament_state(self, channel):
        res = self.send_message(b'GFLENA,%d\n' % channel)
        if res == 'ON':
            return True
        else:
            return False

    def set_filament_state(self, channel, state):
        if state:
            self.send_command(b'SFLENA,%d,ON\n' % channel)
        else:
            self.send_command(b'SFLENA,%d,OFF\n' % channel)
        return True
    
    def get_filament_direction(self, channel):
        res = self.send_message(b'GFLDIR,%d\n' % channel)
        if res == 'FWD':
            return True
        else:
            return False
        
    def set_filament_direction(self, channel, direction):
        if direction:
            self.send_command(b'SFLDIR,%d,FWD\n' % channel)
        else:
            self.send_command(b'SFLDIR,%d,REV\n' % channel)
        return True
            
    # Note: Unclear why filament has a separate set of commands which also requires channel input parameter

    # Return the measured current on the filament (actual sampling)
    def get_filament_measured_current(self, channel):
        strVal = self.send_message(b'GFLAI,%d\n' % channel)
        try:
            flVal = float(strVal)
            return flVal
        except:
            return 0.0

    def get_filament_measured_voltage(self, channel):
        strVal = self.send_message(b'GFLASV,%d\n' % channel)
        try:
            flVal = float(strVal)
            return flVal
        except:
            return 0.0        
                     
    # Return the target current for the filament (target current)
    def get_filament_programmed_current(self, channel):
        strVal = self.send_message(b'GFLI,%d\n' % channel)
        try:
            flVal = float(strVal)
            return flVal
        except:
            return 0.0

    # Program a new current target for the filament
    def set_filament_programmed_current(self, channel, value):
        self.send_command(b'SFLI,%d,%f\n' % (channel, value))
        return True

    def serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
    
    def check_disconnect(self):
        self.connector.send_message_test(b'GCHAN,DCB\n')

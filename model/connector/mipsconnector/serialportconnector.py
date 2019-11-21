import serial
import re
import sys
import time

class MIPSCommunicationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SerialPortConnector(object):
    def __init__(self):
        SerialPortConnector.portName = ""
        SerialPortConnector.baudRate = 115200
        SerialPortConnector.parity = serial.PARITY_NONE
        SerialPortConnector.stopBits = serial.STOPBITS_ONE
        SerialPortConnector.flowControl = serial.SEVENBITS
        SerialPortConnector.pyserial = None

    def connect(self, portName, baudRate, parity, stopBits, flowControl):
        self.baudRate = baudRate
        self.parity = parity
        self.stopBits = stopBits
        self.flowControl = flowControl
        
        if len(portName) > 0:
            self.portName = portName
        else:
            ports = serial.tools.list_ports.comports()
            trimmedPorts = []
        
            for port in ports:
                if port[2] != 'n/a':
                    trimmedPorts.append(port)
        
            arduino = "arduino"
            ardPort = 0
            found = False
            for port in trimmedPorts:
                if arduino in port[0].lower() or arduino in port[1].lower() or arduino in port[2].lower():
                    self.portName = port[0]
                    found = True
                    break
        
            if found == False:
                print("Can't find port")
                raise Exception("Can't find port")
        try:
            self.pyserial = serial.Serial(
                port=self.portName,
                baudrate=self.baudRate,
                parity=self.parity,
                stopbits=self.stopBits,
                bytesize=self.flowControl
            )

            if not self.pyserial.isOpen():
                return False
            return True
        except serial.serialutil.SerialException as err:
            print(err)
            return False
        except:
            e = sys.exc_info()[0]
            print(e)
            return False

    def disconnect(self):
        if self.pyserial is not None:
            if self.pyserial.isOpen():
                self.pyserial.close()

    def is_open(self):
        if self.pyserial is not None:
            return self.pyserial.isOpen()
        return False

    def send_command(self, inputCommand):
        if not self.is_open():
            raise MIPSCommunicationError("port not connected")

        self.pyserial.write(inputCommand + b'\r\n')
        out = ''
        lineFound = False
        startTime = time.time()
        while not lineFound:
            rLen = self.pyserial.inWaiting()
            if rLen > 0:
                newChar = self.pyserial.read(1)
                out += newChar.decode("utf-8")
                if newChar == b'\n':
                    lineFound = True
            else:
                if (time.time() - startTime) > 5:
                    raise MIPSCommunicationError("timeout detected")

        return True

    def send_message(self, inputCommand):
        if not self.is_open():
            raise MIPSCommunicationError("port not connected")

        self.pyserial.write(inputCommand + b'\r\n')
        out = ''
        lineFound = False
        startTime = time.time()
        while not lineFound:
            rLen = self.pyserial.inWaiting()
            if rLen > 0:
                newChar = self.pyserial.read(1)
                out += newChar.decode("utf-8")
                if newChar == b'\n':
                    lineFound = True
            else:
                if (time.time() - startTime) > 5:
                    raise MIPSCommunicationError("timeout detected")

        out = re.sub("[^0-9a-zA-Z!?,.\-+\ ]", "", out)
        return out
    

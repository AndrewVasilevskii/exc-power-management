from model.connector.mipsconnector.mips import MIPS
from model.connector.mipsconnector.serialportconnector import MIPSCommunicationError
import serial.tools.list_ports
from configparser import SafeConfigParser

settingsPath = 'settings.ini'
settingsSection = 'main'
settingsKeyPort = 'port'
settingsKeyBaudRate = 'baudRate'
settingsKeyParity = 'parity'
settingsKeyStopBits = 'stopBits'
settingsKeyFlowControl = 'flowControl'

def GetMIPS():
    mips =  MIPS()
    ports = serial.tools.list_ports.comports()
    trimmedPorts = []
    for port in ports:
        if port[2] != 'n/a':
            trimmedPorts.append(port)
    config = SafeConfigParser()
    config.read(settingsPath)
    if not config.has_section(settingsSection):
        raise Exception("Can't found port")
        return
    port = config.get(settingsSection, settingsKeyPort)
    parity = config.get(settingsSection, settingsKeyParity)
    flow = config.getint(settingsSection, settingsKeyFlowControl)
    bits = config.getfloat(settingsSection, settingsKeyStopBits)
    intBits = 0
    try:
        intBits = int(bits)
    except:
        intBits = -1
        
    if intBits > 0:
        bits = intBits
    baud = config.getint(settingsSection, settingsKeyBaudRate)
    for p in trimmedPorts:
        if p[0] == port:
            res = mips.connect(portName=port, baudRate=baud, parity=parity, stopBits=bits, flowControl=flow)
            if res:
                return mips
            else:
                raise Exception("Can't connect to MIPS")
            
    raise Exception("Can't found port")
    return
    

class AutoConnector(object):
    def __init__(self, errorCB, onConnectCB, onCantReconnect):
        self.errorCB = errorCB
        self.onConnectCB = onConnectCB
        self.onCantReconnect = onCantReconnect
        
    def connect(self):
        mips = None
        try:
            mips = GetMIPS()
        except:
            self.onCantReconnect()
            return
        
        try:
            power = mips.check_power()
            if power == "":
                self.errorCB("Communication error")
            elif power == "NO":
                self.errorCB("Error: Power is OFF")
            else:
                self.onConnectCB(mips)
        except MIPSCommunicationError as e:
            self.errorCB("Communication error: %s" % e.value)
            
    def connectWithParams(self, port, baudRate, parity, stopBits, flowControl):
        config = SafeConfigParser()
        config.read(settingsPath)
        if not config.has_section(settingsSection):
            config.add_section(settingsSection)
        config.set(settingsSection, settingsKeyPort, port)
        config.set(settingsSection, settingsKeyBaudRate, baudRate)
        config.set(settingsSection, settingsKeyParity, parity)
        config.set(settingsSection, settingsKeyStopBits, str(stopBits))
        config.set(settingsSection, settingsKeyFlowControl, str(flowControl))

        with open(settingsPath, 'w') as f:
            config.write(f)
        self.connect()

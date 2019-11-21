from model.connector.mipsconnector.serialportconnector import MIPSCommunicationError
from model.appdata import AppData
from model.devicedata import DeviceData
from time import sleep
from model.connector.autoconnector import GetMIPS
import sqlite3
from model.database import createTablesIfNotExists
from model.agilentloop import DATA_DIR
import serial
import logging
from datetime import datetime
import zipfile
import os, glob

LOG_ZIP_DIR = 'logs'

def pullDataZip():
    try:
        path = os.path.join(os.getcwd(), LOG_ZIP_DIR)
        if not os.path.exists(path):
            os.makedirs(path)

        have_to_zip = []
        for file in glob.glob('pullData_*.log'):
            have_to_zip.append(file)
        for log in have_to_zip:
            zip = zipfile.ZipFile(os.path.join(path, log.split('.')[0]) + '.zip', 'w', zipfile.ZIP_DEFLATED)
            zip.write(log)
            try:
                os.remove(log)
            except:
                continue
    except:
        return

def pullData(channelsMaxValues, channelsMinValues, filamentRealCurrent, filamentActualVoltage, emissionValue, channelsRealValues,
            channelsValues, filamentCurrent, filamentMaxCurrent, connectionControlValue, filamentStatus, filamentRealStatus, directionValue, directionRealValue):
    pullDataZip()

    appData = AppData(channelsValues, filamentStatus, filamentCurrent, filamentMaxCurrent, connectionControlValue, directionValue)
    deviceData = DeviceData(channelsMaxValues, channelsMinValues, filamentRealStatus, filamentRealCurrent, filamentActualVoltage, emissionValue, channelsRealValues, directionRealValue)

    start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    current_log_file = 'pullData_%s.log' % start_time
    logger = logging.getLogger('mips')
    hdlr = logging.FileHandler(current_log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    # SPD = Starting pullData
    logger.info('SPD')
    mips = None
    try:
        mips = GetMIPS()
    except:
        return

    channelsDBVals = [0, 0, 0, 0, 0, 0, 0, 0]
    # CTM = Connection to mips
    logger.info('CTM')

    db = sqlite3.connect('db.sqlite')

    createTablesIfNotExists(db)
#    insertMipsData(db, 0, 20, 1)
    filamentDBVal = appData.getFilamentCurrent()

    for channel in range(0, 7):
        channelsDBVals[channel] = appData.getChannelValue(channel)

    appData.setConnectionControlValue(1)
    while True:
        sleep(0.05)
    #    insertMipsData(db, teststep, 20, 2)
        path = os.path.join(os.getcwd(), DATA_DIR)
        step = 0
        while os.path.exists(os.path.join(path, "data_%s.npy" % step)):
            step += 1
        step -= 1
    #    insertMipsData(db,teststep, 20, 3)

        filament_channel = 1
        # == > ========NEW LOOP========
        logger.info('==')
        if appData.getConnectionControlValue() == 0:
            try:
                if not mips.set_filament_state(filament_channel, False):
                    #CNT off = can\'t turn off
                    logger.error('CNT off mips')
            finally:
                #  RDC = received disconnect
                logger.info('RDC')
                mips.disconnect()
                return
        try:
            power = mips.check_power()
            # Pow: = Power is
            logger.info("Pow: " + power)

            channels = mips.get_number_of_channels()
            # CC = channels count
            logger.info("CC: " + str(channels))

            if channels < 1:
                # enCD = error: no channels detected
                logger.info("enCD")

            channelsValues = []
            channelsMaxValues = []
            channelsMinValues = []
        #    insertMipsData(db,teststep, 20, 4)
            for channel in range(1, channels + 1):
        #        insertMipsData(db,teststep, 21, 4)
                # C = Channel
                logger.info("C " +  str(channel))

                mvoltage = mips.get_channel_measured_voltage(channel)
                channelsValues.append(mvoltage)
                maxVal = mips.get_max_range(channel)
                channelsMaxValues.append(maxVal)
        #        insertMipsData(db,teststep, 22, 5)
                minVal = mips.get_min_range(channel)
                channelsMinValues.append(minVal)
                # V = voltage
                logger.info("C {}; V: {}; min: {}; max: {}".format(channel, mvoltage, minVal, maxVal))
        #        insertMipsData(db,teststep, 21, 5)
                pvoltage = mips.get_channel_programmed_voltage(channel)
                # PP = previously programmed
                logger.info("PP V " + str(pvoltage))

                res = mips.set_channel_programmed_voltage(channel, appData.getChannelValue(channel - 1))
                # P = programmed
                logger.info("P V to: %d, res: %d" % (appData.getChannelValue(channel - 1), res))
        #        insertMipsData(db,teststep, 20, 5)
                if appData.getChannelValue(channel - 1) != channelsDBVals[channel - 1]:
                    channelsDBVals[channel - 1] = appData.getChannelValue(channel - 1)
        #            insertMipsData(db, step, channelsDBVals[channel - 1], channel - 1)

        #    insertMipsData(db,teststep, 20, 6)
            emission = mips.get_emission_current()
            deviceData.setCurrentEmission(emission)
            # EMS = EMISSION
            logger.info("EMS: " + str(emission))
            # FLM = FILAMENT
            logger.info("FLM")
            status = mips.check_filament_state(filament_channel)

            if status:
                deviceData.setFilamentRealStatus(1)
            else:
                deviceData.setFilamentRealStatus(0)

            if appData.getFilamentStatus() != deviceData.getFilamentRealStatus():
                if appData.getFilamentStatus() == 1:
                    mips.set_filament_state(filament_channel, True)
                else:
                    mips.set_filament_state(filament_channel, False)

            direction = mips.get_filament_direction(filament_channel)
            if direction is None:
                # Dir = dirrection
                logger.info("Dir NONE")
            else:
                logger.info("Dir " + str(direction))
                if direction:
                    deviceData.setDirectionRealValue(1)
                else:
                    deviceData.setDirectionRealValue(0)

            if appData.getDirectionValue() != deviceData.getDirectionRealValue():
                # Cdir = Changing dirrection
                logger.info("Cdir")
                if appData.getDirectionValue() == 1:
                    # tT = to True
                    logger.info("tT")
                    mips.set_filament_direction(filament_channel, True)
                else:
                    # tF = to False
                    logger.info("tF")
                    res = mips.set_filament_direction(filament_channel, False)
                    if res is None:
                        # Cdir = Changing dirrection
                        logger.info("rcvd none for Cdir")
                    else:
                        logger.info("rcvd true")

            filament_value = mips.get_filament_measured_current(filament_channel)
            mips.set_filament_programmed_current(filament_channel, appData.getFilamentCurrent())
            if appData.getFilamentCurrent() != filamentDBVal:
                filamentDBVal = appData.getFilamentCurrent()
        #        insertMipsData(db, step, filamentDBVal, 8)

        #    insertMipsData(db,teststep, 20, 10)
            logger.info("val: " + str(filament_value))
            filament_voltage = mips.get_filament_measured_voltage(filament_channel)
            logger.info("V: " + str(filament_voltage))
            deviceData.setFilamentRealCurrent(filament_value)
            deviceData.setFilamentActualVoltage(filament_voltage)
            for index in range(channels):
                deviceData.setChannelsMaxValues(index, channelsMaxValues[index])
                deviceData.setChannelsMinValues(index, channelsMinValues[index])
                deviceData.setChannelsRealValues(index, channelsValues[index])

        except MIPSCommunicationError as e:
            # need to reconnect
            # COMM = Communication
            logger.warning("COMM err: %s" % e.value)
            mips.disconnect()
            sleep(1.5)
            mips = tryReconnect()
            if mips is not None:
                logger.warning("Restarted")
            else:
                appData.setConnectionControlValue(0)
                logger.warning("CNT restarted")
                return
        except serial.SerialTimeoutException as e:
            # need to reconnect
            # TOE = TimedoutException
            logger.warning("SerialTOE err: %s" % e.value)
            mips.disconnect()
            sleep(1.5)
            mips = tryReconnect()
            if mips is not None:
                logger.warning("Restarted")
            else:
                appData.setConnectionControlValue(0)
                logger.warning("CNT restarted")
                return
        except Exception as e:
            # Exc = Exception
            logger.warning("Exc err: %s" % e)
            mips.disconnect()
            sleep(1.5)
            mips = tryReconnect()
            if mips is not None:
                logger.warning("Restarted")
            else:
                appData.setConnectionControlValue(0)
                logger.warning("CNT restarted")
                return

def tryReconnect():
    mips = None
    try:
        mips = GetMIPS()
    except:
        return None
    return mips

import numpy as np
import yaml
import time
import shutil
from shutil import copyfile
import os
import sys
import sqlite3
import time
import logging
from model.database import createTablesIfNotExists, getGraphs, getUncalculatedDataIndex, insertCalculatedData

DATA_DIR = 'session_data'

def saveToFile(filename, data):
    with open(filename, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

def calculateLoop(agilentControlValue):

    db = sqlite3.connect('db.sqlite')
    cursor = db.cursor()
    createTablesIfNotExists(db)
    path = os.path.join(os.getcwd(), DATA_DIR)
    while True:
        logging.info('while - true start')
        with agilentControlValue.get_lock():
            if agilentControlValue.value == 0:
                db.close()
                return
        exists_file_counter = 1
        while os.path.exists(os.path.join(path, "data_%s.npy" % exists_file_counter)):
            exists_file_counter += 1
        exists_file_counter -= 1
        if exists_file_counter < 1:
            time.sleep(1)
            continue
        allGr = getGraphs(db)
        for gr in allGr:
            maxVal = getUncalculatedDataIndex(db, gr[0])
            logging.info('Loop sta')
            #for i in xrange(50):
            while(maxVal <= exists_file_counter-1):
                logging.info('loop iterate sta')
                logging.info('taking paths')
                dataFilename = os.path.join(path, "data_%s.npy" % maxVal)
                paramsFilename = os.path.join(path, "param_%s.yml" % maxVal)
                logging.info('file loading')
                data = np.load(dataFilename)
                logging.info('param loading')
                with open(paramsFilename, 'r') as stream:
                    params = yaml.load(stream)
                logging.info('taking data')
                a= 0.0003457908523
                t0=1004.240466
                l1=int((np.sqrt(gr[1] - 1.35)/a+t0 + 0.5)*params['spns'] -params['spstart'])
                l2=int((np.sqrt(gr[1] + 1.8)/a+t0 + 0.5)*params['spns'] -params['spstart'])
    
                peakInt = data[l1:l2].sum()
                peakMax = data[l1:l2].max()

                logging.info('inserting')
                insertCalculatedData(cursor, maxVal, peakInt, peakMax, gr[0])

                maxVal += 1
                logging.info('loop iterate end')
            db.commit()
            logging.info('Loop end')
            time.sleep(1)


def agilentLoop(agilentControlValue):   
#     import unittest
#     reload(unittest)
#      
#     modeldir = os.path.dirname(os.path.realpath(__file__))
#     print modeldir
#     print "parentdir"
#     parentdir = os.path.dirname(modeldir)
#     print parentdir
#     parentdir = os.path.dirname(parentdir)
#     print parentdir
#     parentdir = os.path.dirname(parentdir)
#     print parentdir
#      
#     instrumentdir = os.path.join(parentdir, 'InstrumentPython')
#     print instrumentdir
#     thisdir = os.path.join(instrumentdir, "test")
#     print thisdir
#     if instrumentdir not in sys.path:
#         sys.path.append(instrumentdir)
#     import pycontrol
#     reload(pycontrol)
#     import time
#     print sys.path
#      
#     date = 'today' #'20101010'     # 'today' or 'yyyymmdd'
#     pwd = os.getcwd()
#     print pwd
#      
#     configfile = os.path.join(modeldir, 'ECD.cfg')
#      
#     import pycontrol
#     reload(pycontrol)
#      
#     print sys.path
#      
#     pc = pycontrol.Idaq(cfgfile = configfile)
#     pc.loadOptimizer()
#      
#     settings_pycontrol.debugging = False
#      
#     import Useful, collections
#     import time
#     import Useful as useful
#     useful.add_path_for_instruments(thisdir)
#     import AttrDict
#      
#     pc.instr.ms.set_cal_at0(a=0.34578929031, t0=1.0082508255)
# 
#     path = os.path.join(os.getcwd(), DATA_DIR)
#     
#     if not os.path.exists(path):
#         os.makedirs(path)
#     try:
#         shutil.rmtree(path)
#     finally:
#         os.makedirs(path)
#     while True:    
#         with agilentControlValue.get_lock():
#             if agilentControlValue.value == 0:
#                 return
#     
#         i = 0
#         while os.path.exists(os.path.join(path, "data_%s.npy" % i)):
#             i += 1
# 
#         spec1,param = pc.instr.ms.module.getSpectrum()
#         np.save(os.path.join(path, "data_%s.npy" % i), spec1)
#         saveToFile(os.path.join(path, "param_%s.yml" % i), param)

    
    playSavedData(agilentControlValue)
    return
#     
#     dataFilename = "collected_data1.npy"
#     paramsFilename = "collected_params1.yml"
#     data = np.load(dataFilename)
#     with open(paramsFilename, 'r') as stream:
#         params = yaml.load(stream)
#     maxValue = data.shape[0]
#      
# >>>>>>> Stashed changes
#     path = os.path.join(os.getcwd(), DATA_DIR)
#     if not os.path.exists(path):
#         os.makedirs(path)
#     try:
#         shutil.rmtree(path)
#     finally:
#         os.makedirs(path)
#      
#     sourcePath = os.path.join(os.getcwd(), DATA_DIR + "_source")
#     i = 0
#     while True:
#          
#         with agilentControlValue.get_lock():
#             if agilentControlValue.value == 0:
#                 return
# <<<<<<< Updated upstream
#        
#         specSrc = os.path.join(sourcePath, "data_%s.npy" % i)
#         specDst = os.path.join(path, "data_%s.npy" % i)
#         
#         paramSrc = os.path.join(sourcePath, "param_%s.yml" % i)
#         paramDst = os.path.join(path, "param_%s.yml" % i)    
#         
#         copyfile(specSrc, specDst)
#         copyfile(paramSrc, paramDst)
#         i += 1
#         time.sleep(0.5)
# =======
#         spec1 = data[value]
#         param = params[value]
#         i = 0
#         while os.path.exists(os.path.join(path, "data_%s.npy" % i)):
#             i += 1
#  
#         np.save(os.path.join(path, "data_%s.npy" % i), spec1)
#         saveToFile(os.path.join(path, "param_%s.yml" % i), param)
#         time.sleep(1.5)
#          
#         value = value + 1
#         if value >= maxValue:
#             value = 0
            
def playSavedData(agilentControlValue):
    
    path = os.path.join(os.getcwd(), DATA_DIR)
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        shutil.rmtree(path)
    finally:
        os.makedirs(path)
        
    sourcePath = os.path.join(os.getcwd(), "session_data_source")
    
    exists_file_counter = 0
    while True:
        with agilentControlValue.get_lock():
            if agilentControlValue.value == 0:
                return
        
        if not os.path.exists(os.path.join(sourcePath, "data_%s.npy" % exists_file_counter)):
            return
        
        shutil.copyfile(os.path.join(sourcePath, "param_%s.yml" % exists_file_counter), os.path.join(path, "param_%s.yml" % exists_file_counter))
        shutil.copyfile(os.path.join(sourcePath, "data_%s.npy" % exists_file_counter), os.path.join(path, "data_%s.npy" % exists_file_counter))
        exists_file_counter += 1

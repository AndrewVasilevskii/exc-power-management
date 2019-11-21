
import os, sys

import unittest
reload(unittest)

thisdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.sep.join(thisdir.split(os.path.sep)[0:-1])
instrumentdir = os.path.join(parentdir, 'InstrumentPython')
if parentdir not in sys.path:
    sys.path.append(parentdir)
import pycontrol
reload(pycontrol)
import time


date = 'today' #'20101010'     # 'today' or 'yyyymmdd'
pwd = os.getcwd()

configfile = 'test_ECD.cfg'

        
import pycontrol
reload(pycontrol)


pc = pycontrol.Idaq(cfgfile = configfile)
pc.loadOptimizer()

settings_pycontrol.debugging = False
#pc.read('mlens1')
#
#pc.read('mlens12_diff')

#pc.instr.mips.maxFI = 5.5

import Useful, collections
import time
import Useful as useful
useful.add_path_for_instruments(thisdir)
import AttrDict

celln = 'l1 l2 l3pm1 l4fh l5pm2 l6 fbias fil filV filP'.split()
tunelist = 'l1 l2 l3pm1 l4fh l5pm2 l6 fbias fil'.split()

Vtune = {'l3pm1': -5.4, 'fbias': -14.3, 'l4fh': 4.7, 'l6': -3.4, 'l2': -7.0, 'l1': 18.1, 'l5pm2': 20.8, 'fil': 0.0}
cellzero = {'l3pm1': 0, 'fbias': 0, 'l4fh': 0, 'l6': 0, 'l2': 0, 'l1': 0, 'l5pm2': 0, 'fil': 0}

optprior = dict(l1=24, l2=-7, l3pm1=-10, l4fh=-15, l5pm2=12, l6=-3.4, fbias=-20)
optavg = dict(l1=24.2, l2=-12.7, l3pm1=-0.2, l4fh=-20.6, l5pm2=11.9, l6=3.5, fbias=-24.9)
optnew = dict(l1=27.6, l2=-16.3, l3pm1=2.1, l4fh=-20.5, l5pm2=15.2, l6=0.1, fbias=-24.9)

ecdinit = {'l3pm1': 16.3, 'fbias': 7.44, 'l4fh': 22.28, 'l6': -6.0, 'l2': -20.3, 'l1': 23.3, 'l5pm2': 22.3, 'fil': 1.22}

ecdtune1 = {'l3pm1': 16.309999999999999, 'fbias': 2.4199999999999999, 'l4fh': 23.989999999999998, 'l6': -6.0, 'l2': -20.300000000000001, 'l1': 23.300000000000001, 'l5pm2': 22.300000000000001, 'fil': 1.22}

currentvalues = {'fbias': 7.46,
 'fil': -0.0,
 'filP': 0.0,
 'filV': 1.3999999999999999,
 'l1': 23.300000000000001,
 'l2': -20.309999999999999,
 'l3pm1': 16.309999999999999,
 'l4fh': 22.289999999999999,
 'l5pm2': 22.309999999999999,
 'l6': -6.0}



scanset = AttrDict.AttrDict()

import plotdata as pd
import matplotlib.pyplot as plt
import numpy as np

pc.instr.ms.set_cal_at0(a=0.34578929031, t0=1.0082508255)
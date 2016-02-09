import numpy as np
import re
from pyrelaxd import *
import logging

logger = logging.getLogger(__name__)

def exttrigger (deo):
    reg=(deo.readReg(MPIX2_CONF_REG_OFFSET)[1])
    reg=reg&~MPIX2_CONF_TIMER_USED
    reg=reg&~MPIX2_CONF_BURST_READOUT;
    reg=reg&~MPIX2_CONF_EXT_TRIG_ENABLE
    reg=reg|MPIX2_CONF_SHUTTER_CLOSED
    reg=reg|MPIX2_CONF_EXT_TRIG_ENABLE
    reg=reg&~MPIX2_CONF_EXT_TRIG_FALL
def num (s):
    try:
        return int(s)
    except ValueError:
        return float(s)
def bitn (s):
    return (len(bin(s))-3)

def readDacs(dacfn):
    f=open(dacfn, "r")
    t=[]
    letters=[]
    numbers=[]
    dacs=[]
        
    ii=0
    for line in f.readlines():
        t.append(line)
        ii+=1
    f.close()

    numOfDucsPChip=14
    numofchips=ii/(numOfDucsPChip+1)

    kk=0
    for i in (numOfDucsPChip+1)*np.arange(numofchips):
        t.pop(i-kk)
        kk=kk+1
    for i in range(len(t)):
        letters.append(re.findall('\\d+',t[i].split()[0])[0])
        numbers.append(int(re.findall('\\d+',t[i].split()[0])[0]))
    for i in range(numofchips):
        dacs.append([])
        for j in range(numOfDucsPChip):
            dacs[i].append(numbers[numOfDucsPChip*i+j])

    return dacs


def readHw(dacfn):
    f=open(dacfn, "r")
    t=[]
    hwc=[]
    hwn=[]
    out=[]

    hwpars=[['TestPulseLow',9],['TestPulseHigh',10],['TestPulseFreq',11],
    ['BiasAdjust',12],['MpixVddAdjust',13],
    ['FirstChipNumber',18],['LogVerbose',19],['ParReadout',20],
    ['StorePixelsCfg', 21],['StoreDacs',22],['EraseStoredConfig',23],
    ['ConfTpxClock',24],['ConfRoClockMHz',25],['ConfTpxPreclocks',26],
    ['ConfHvBiasDisable',27]]

    for ii in hwpars:
        hwc.append(ii[0])
        hwn.append(ii[1])
        
    ii=0
    for line in f.readlines():
        t.append(line)
        ii+=1
    f.close()

    for i in range(len(t)):
        tmp=t[i].split(':')
        hwn[hwc.index(tmp[0])]
        out.append([hwn[hwc.index(tmp[0])],num(tmp[1])])
        
    return out


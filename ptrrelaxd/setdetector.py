import time
import sys
from pyrelaxd import *
import numpy as np
import re
import read_parameters as rp
import struct
import logging

logger = logging.getLogger(__name__)

def exttrigger (deo):
    reg=(deo.readReg(MPIX2_CONF_REG_OFFSET)[1])
    reg=reg&~MPIX2_CONF_TIMER_USED
    reg=reg&~MPIX2_CONF_BURST_READOUT;
    reg=reg&~MPIX2_CONF_EXT_TRIG_ENABLE
    reg=reg|MPIX2_CONF_SHUTTER_CLOSED
    reg=reg|MPIX2_CONF_EXT_TRIG_ENABLE
    reg=reg&~MPIX2_CONF_EXT_TRIG_FALLING_EDGE
    reg=reg&~MPIX2_CONF_EXT_TRIG_INHIBIT
    return deo.writeReg(MPIX2_CONF_REG_OFFSET,reg)

def originaltrigger (deo):
    return deo.writeReg(MPIX2_CONF_REG_OFFSET,2124032)

def polarity0 (deo):
    reg=(deo.readReg(MPIX2_CONF_REG_OFFSET)[1])
    reg=reg&~MPIX2_CONF_POLARITY
    return deo.writeReg(MPIX2_CONF_REG_OFFSET,reg)

def polarity1 (deo):
    reg=(deo.readReg(MPIX2_CONF_REG_OFFSET)[1])
    reg=reg&~MPIX2_CONF_POLARITY
    reg=reg|MPIX2_CONF_POLARITY
    return deo.writeReg(MPIX2_CONF_REG_OFFSET,reg)


def setdet(id1,hw):
    if len(hw)!=4:
        #sys.exit('wrong HW parameters')
        return 0

#    fo = open(('det_'+repr(id1)+'_ini.txt'), 'w')
    mpx = MpxModule(id1)
    numofchips=mpx.chipCount()
#    fo.write('number of chips = '+repr(numofchips)+'\n')
#    fo.flush()
    if numofchips <= 0:
#        fo.close()
        logger.error('chips can not be found')
        return None

    ## if not mpx.ping():
    ##    print "Your module does not seem to be functioning, please restart it and try again"

    if mpx.init():
#        fo.close()
        logger.error('mpx.init() failed')
        return None


    mpx.setLogVerbose(True)
    rv, ver, ver2 = mpx.getFirmwareVersion()
#    print("Relaxd firmware version %d.%d.%d" % (ver / 100, (ver / 10) % 10, ver % 10))

    # list the chips and there types (should all be the same)
    name_map = {
                MPX_MXR : 'Medipix2',
                MPX_TPX : 'Timepix'
                }
#    fo.write('Found the following chips:'+'\n')

#    for i in range(numofchips):
#        fo.write("-" + repr(i) + ":"+ mpx.chipName(i)+ "of type"+ repr(name_map[mpx.chipType(i)])+'\n')
#        fo.flush()
    
    chipType = mpx.chipType(0)      # assume they're all the same


    if int(hw[0])==0:
        if mpx.resetMatrix():
            logger.error('mpx.resetMatrix() failed')
            return None
        return mpx

    pixelcfg1=hw[1]
    realdacs1=hw[2]
    hwinfofile1=hw[3]
 #   fo.write("pixelcfg= " +pixelcfg1 + "  realdacs= "+realdacs1+ "  hwinfo= "+ hwinfofile1+'\n')
#    fo.flush()
#    fo.close()
    if mpx.setPixelsCfgFromFile(pixelcfg1,3):
        logger.error('setPixelsCfgFromFile(pixelcfg) failed')
        return None

    if mpx.resetMatrix():
        logger.error('mpx.resetMatrix() failed')
	return None
    time.sleep(3)
    dac=rp.readDacs(realdacs1)
    for j in range(numofchips): 
        logger.info("dacs " + str(j) + ": " + repr(dac[j]))
        if mpx.setFsr(j, dac[j]):
            logger.error('mpx.setFsr(j, dac[j]) failed')
            return None
    hwinfo=rp.readHw(hwinfofile1)
    logger.info("hwinfo " + repr(hwinfo))
    for j in hwinfo:
        if mpx.setHwInfo(j[0], j[1]):
            logger.error('mpx.setHwInfo(j[0], j[1])')
            return None
   
    for j in range(28):
        logger.info (str(j) + "  " +  repr(mpx.getHwInfo(j)))

    if mpx.resetMatrix():
	logger.error('mpx.resetMatrix() failed')
        return None

    return mpx

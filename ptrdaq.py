#!/usr/bin/python
from __future__ import division
import logging
from ptrsparc.ptrsparc import ptrsparc
from ptrrelaxd.ptrrelaxd import ptrrelaxd
from multiprocessing import Process, Pipe, Event
from threading import Timer
import time
import sys
import serial
import rpi
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("fileprefix", help="Prefix for filenames eg /data/agor/run1")
parser.add_argument("-t","--time",type=int,help="Stop after time in seconds",)
parser.add_argument("-n","--nevents",type=int,help="Stop after n events")
parser.add_argument("-d","--display",action="store_true",help="Use event display (experimental)")
args = parser.parse_args()
logger = logging.getLogger(__name__)
def parsePipeMsg(msg,id):
    if (msg.__class__ == logging.LogRecord):
        logmsg = id + ": " + msg.getMessage()
        if (msg.levelno>20):
            logmsg = "\033[91m" + logmsg + "\033[0m" #red
        logger.log(msg.levelno,logmsg)
    elif (type(msg)==int and args.nevents>0):
        if (msg>args.nevents):
            stoprun()
def process(data):
    lines = data.split("\r\n")
    for i in lines:
        if len(i)==72:
           logger.info(i)

def stoprun():
    global running
    if (running): 
        logger.info("Stopping run...")
        rpi.on()
        time.sleep(0.1)
        events[0].set()
        events[1].set()
        events[2].set()
        global hisparcPipe
        global gp1Pipe
        global gp2Pipe
        hisparcPipe.send("stop")
        gp1Pipe.send("stop")
        gp2Pipe.send("stop")
        running=False

if __name__ == "__main__":
    try:
        prefix = args.fileprefix
        logger.setLevel(logging.INFO)
        ch1 = logging.StreamHandler()
        ch1.setLevel(logging.INFO)
        ch2 = logging.FileHandler(prefix+"_log.txt")
        ch2.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',"%Y-%m-%d %H:%M:%S")
        ch1.setFormatter(formatter)
        ch2.setFormatter(formatter)
        logger.addHandler(ch1)
        logger.addHandler(ch2)
        logger.info("Starting "+prefix)
        events = [Event() for i in range(0,4)]
        #logger.info("Caen info:")
        #logger.info("           VMON  IMON    V0     V1    I0    I1    RUP   RDW TRIP  STATUS RAMP")
        #ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
        #ser.write("2")
        #process(ser.read(2048))
        #ser.write("a")
        #process(ser.read(2048))
        #ser.write("p")
        #process(ser.read(2048))
        #ser.write("p")
        #process(ser.read(2048))
        #ser.write("2") 
        rpi.on()
        time.sleep(0.1)
        events[0].set()
        events[1].set()
        events[2].set()
        events[3].set()
       # hisparcPipe,b = Pipe()
       # hisparcProcess = Process(target=ptrsparc,args=(b,events[0],[events[1],events[2]],events[3],prefix+"_calo.root"))
       # hisparcProcess.start()
        hisparc = ptrsparc()
        hisparc.filename=prefix+"_calo.root"
        hisparcPipe = hisparc.pipeEnd
        hisparc.start()

        gp1 = ptrrelaxd()
        gp1.filename=prefix+"_1.root"
        gp1.id = 1
        gp1.useConfig = 1
        gp1.bpc = "ptrrelaxd/settings/chamber1.bpc"
        gp1.dacs = "ptrrelaxd/settings/chamber1.bpc.dacs"
        gp1.hwdacs = "ptrrelaxd/settings/chamber1.hw.dacs"
        gp1.display = args.display
        gp1Pipe = gp1.pipeEnd
        gp1.start()
        
        gp2 = ptrrelaxd()
        gp2.filename=prefix+"_2.root"
        gp2.id = 2
        gp2.useConfig = 1
        gp2.bpc = "ptrrelaxd/settings/chamber_new_append.bpc"
        gp2.dacs = "ptrrelaxd/settings/chamber_new_append.bpc.dacs"
        gp2.hwdacs = "ptrrelaxd/settings/chamber3.hw.dacs"
        gp2.display = args.display
        gp2Pipe = gp2.pipeEnd
        gp2.start()

        t=Timer(10,rpi.off)
        t.start()
        running = True
        starttime = int(round(time.time() * 1000))+10000
        while running:
            try:
                while (hisparcPipe.poll()):
                    parsePipeMsg(hisparcPipe.recv(),"HiSPARC")
                while (gp1Pipe.poll()):
                    parsePipeMsg(gp1Pipe.recv(),"Gridpix 1")
                while (gp2Pipe.poll()):
                    parsePipeMsg(gp2Pipe.recv(),"Gridpix 2")
                if (args.time>0):
                    if (int(round(time.time()*1000))>starttime+1000*(args.time)):
                        stoprun()
                time.sleep(0.01)
            except KeyboardInterrupt:
                stoprun()

        logger.info("waiting for hisparc to finish...")
        hisparc.join()
        while (hisparcPipe.poll()):
            parsePipeMsg(hisparcPipe.recv(),"HiSPARC")

        logger.info("waiting for gp1 to finish...")
        gp1.join()
        while (gp1Pipe.poll()):
            parsePipeMsg(gp1Pipe.recv(),"Gridpix 1")

        logger.info("waiting for gp2 to finish...")
#        time.sleep(2)
        gp2.join()
        while (gp2Pipe.poll()):
            parsePipeMsg(gp2Pipe.recv(),"Gridpix 2")

        logger.info("done")
    except:
        print "error?"
        print sys.exc_info()[0]

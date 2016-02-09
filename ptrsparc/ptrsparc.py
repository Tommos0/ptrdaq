import logging
from ftdi import FtdiChip
from align_adcs import AlignADCs
import messages
from config import *
import time
import sys
import signal
from datawriter import dataWriter
from multiprocessing import Process,Pipe

logger = logging.getLogger('')
READSIZE = 1 * 64 * 1024
PRECOIN = 600
POSTCOIN = 400

#log handler to pass log through pipe
class pipeHandler(logging.Handler):
    def __init__(self,pipe):
        logging.Handler.__init__(self)
        self.pipe = pipe
    def write(self,data):
        self.emit(data)
    def emit(self,record):
        self.pipe.send(record)


class ptrsparc(Process):
    device = None
    pipe = None
    filename = None

    def __init__(self):
        Process.__init__(self)
        self.pipeEnd,self.pipe = Pipe()
    def getpipe(self):
        return self.pipeEnd
  #  def run(self):
        #hisparcPipe,b = Pipe()
        #hisparcProcess = Process(target=ptrsparc,args=(b,events[0],[events[1],events[2]],events[3],prefix+"_calo.root"))
        #hisparcProcess.start()
   #     print "HiSparc Running"
   # def initialize(self,pipe,event_set,events_wait,event_hisparc,filename):
    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        logger.addHandler(pipeHandler(self.pipe))
        logger.setLevel(logging.INFO)
        logger.info("Searching for HiSPARC III Master...")
        device = self.get_device()
        if not device:
            logger.error("HiSPARC III Master not found")
            return
        logger.info("Master found: %s" % device.serial)
        self.device = device
        self.device_buffer = bytearray()
        self.config = Config(self)

        self.send_message(messages.ResetMessage(True))
        self.send_message(messages.InitializeMessage(False))

        align_adcs = AlignADCs(self)
        align_adcs.set_align_brent()
        self.send_message(messages.TriggerConditionMessage(0x0))
        self.send_message(messages.CoincidenceTimeMessage(1))#*5ns
        #self.send_message(messages.PreCoincidenceTimeMessage(200))#100 voor labtests,200 @ KVI
        #self.send_message(messages.PostCoincidenceTime(500))#900, proton 
        self.send_message(messages.PreCoincidenceTimeMessage(PRECOIN))
        self.send_message(messages.PostCoincidenceTime(POSTCOIN))#900, proton 
        self.send_message(messages.TriggerConditionMessage(0x40))
        self.dw = dataWriter(self.filename,(PRECOIN+POSTCOIN)*2+2)
        self.counter = 0

        self.device.flush_input()
        time.sleep(8)
        logger.info("HiSPARC III Master initialized")
        self.mainLoop()

    def get_device(self):
        devices = FtdiChip.find_all()
        for device in devices:
            serial_str, description = device
            if description == "HiSPARC III Master":
                return FtdiChip(serial_str)
        return None

    def mainLoop(self):
        msgsize = (PRECOIN+POSTCOIN)*6+29
#        self.event_set.set()
#        for event in self.events_wait:
#            event.wait()
        self.starttime = (int)(round(time.time()*1000))
        msg = None

        while True:
            #millis = int(round(time.time() * 1000))
            input = self.device.read(READSIZE)
            #millis = int(round(time.time() * 1000))-millis
            self.device_buffer.extend(input)
            nmsg = len(self.device_buffer)/msgsize
            #if (millis>35):
            #    logger.warn("event "+str(self.counter)+" took " + str(millis) + "ms, got " + str(nmsg) + " msgs")
            if nmsg>2:
                logger.warn("event "+str(self.counter)+": " + str(nmsg) + " in buffer")
            while nmsg>0:
                msg = messages.HisparcMessageFactory(self.device_buffer) #removes message from buffer if found!
                #logger.warn(str(type(msg)))
                if (type(msg) == messages.MeasuredDataMessage ):
                    #if (self.counter<10):
                    #    logger.info(str(self.counter) + " " +  str((int)(round(time.time()*1000)-self.starttime)) )
                    self.counter = self.counter + 1
                    print "HS event"
                    self.dw.addWrite((int)(round(time.time()*1000 - self.starttime)),msg)
                else:
                    break
            if (self.counter%100==0):
                self.pipe.send(self.counter)
                pass
            if (self.pipe.poll()):
                d = self.pipe.recv()
                if (d=="stop"):
                    self.send_message(messages.ResetMessage(True))
                    self.device.flush_input()
                    self.device.close()
                    self.dw.stop()
                    break
            #time.sleep(5)
        #done
        logger.info("done, counted: " + str(self.counter) + " events")
    def send_message(self, msg):
        self.device.write(msg.encode())

    def sendMessage(self,message):
        self.pipe.send(message) 




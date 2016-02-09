import logging
import time
import sys
import signal
from threading import Lock,Thread
import setdetector as sd
import read_parameters as rp
from datawriter import dataWriter
from multiprocessing import Process,Pipe
import numpy

logger = logging.getLogger('')
#log handler to pass log through pipe
class pipeHandler(logging.Handler):
    def __init__(self,pipe):
        logging.Handler.__init__(self)
        self.pipe = pipe
    def write(self,data):
        self.emit(data)
    def emit(self,record):
        self.pipe.send(record)


class ptrrelaxd(Process):
    pipe = None
    filename = None
    id = None
    useConfig = False
    bpc = None
    dacs = None
    hwdacs = None
    def __init__(self):
        Process.__init__(self)
        self.pipeEnd,self.pipe = Pipe()
    def getpipe(self):
        return self.pipeEnd
    def run(self):
  #  def __iffnit__(self,pipe,event_set,events_wait,event_hisparc,filename,id,hw):
        self.hw = [self.useConfig,self.bpc,self.dacs,self.hwdacs]
        signal.signal(signal.SIGINT, signal.SIG_IGN)
#        self.event_set = event_set
#        self.events_wait = events_wait
#        self.event_hisparc = event_hisparc
        self.counter = 0
        logger.addHandler(pipeHandler(self.pipe))
        logger.setLevel(logging.INFO)

        self.mpx=sd.setdet(self.id,self.hw)
        if not self.mpx:
            return
        self.data = numpy.empty([512,256], dtype=numpy.int16)
        sd.exttrigger(self.mpx)
        self.dw = dataWriter(self.filename,self.id,self.display)
        logger.info("Initialized")
        self.mainLoop()

    def mainLoop(self):
#        self.event_set.set()
#        for event in self.events_wait:
#            event.wait()
        lastframe = int(round(time.time() * 1000))
        self.starttime = (int)(round(time.time()*1000))
        if self.mpx.newFrame(True,True):
            self.mpx.readMatrix(self.data) #clear first event
        while True:
            if (self.pipe.poll()):
                d = self.pipe.recv()
                if (d=="stop"):
                    logger.info("Got stop signal")
                    self.mpx.closeShutter()
                    self.dw.stop()
                    break
            if self.mpx.newFrame(True,True):
                lastframe = int(round(time.time() * 1000))
#                self.event_hisparc.wait()
                self.mpx.readMatrix(self.data)
                #if (self.counter<10):
                #    logger.info(str(self.counter) + " " +  str((int)(round(time.time()*1000)-self.starttime)) )
                self.dw.addWrite((int)(round(time.time()*1000)-self.starttime),self.data)
                self.counter = self.counter + 1

            else:
                #logger.info(int(round(time.time()*1000))-lastframe)
                if int(round(time.time()*1000))-lastframe>1000*60:
                    logger.info("setting exttrigger again")
                    lastframe = int(round(time.time() * 1000))
                    sd.exttrigger(self.mpx)
                time.sleep(0.01)
        #done
        sd.originaltrigger(self.mpx)
#        self.mpx.closeShutter()
        logger.info("done, counted: " + str(self.counter) + " events")
    def sendMessage(self,message):
        self.pipe.send(message) 

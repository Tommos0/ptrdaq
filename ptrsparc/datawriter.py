import numpy
import ROOT
from threading import Thread,Lock
import time
import logging
logger = logging.getLogger('')

#dataWriter: buffered root file writer
class dataWriter:
    thread_active = False
    def __init__(self,filename,datasize):
        datasize=1602
        self.data = numpy.zeros(datasize,dtype=numpy.uint16)
        self.time = numpy.zeros(1,dtype=numpy.uint32) #single-value array, so memory address stays the same for ROOT
        
        self.outputfile = ROOT.TFile(filename,'create')
        self.tree = ROOT.TTree("calo","calo")
        self.tree.Branch('calo_data',self.data,'calo_data['+str(datasize)+']/s')
        self.tree.Branch('time',self.time,'time/i')

        self.lock = Lock() #lock because both threads access data
        self.writeList = []
        
        self.counter = 0 
        self.thread = Thread(target=self.threadLoop)
        self.thread_active=True
        logger.info("writing data to: " + filename)
        self.thread.start()
    def addWrite(self,timestamp,msg):
        self.lock.acquire()
        self.writeList.append((timestamp,msg))
        self.lock.release()
    def stop(self):
        self.thread_active = False
        self.thread.join()
    def threadLoop(self):
        while self.thread_active:
            while (len(self.writeList)>0):
                self.counter = self.counter + 1 
                self.lock.acquire()
                p = self.writeList.pop(0) #measureddatamsg
                self.lock.release()
                self.time[0]=p[0] 
                self.data[::] = p[1].trace_ch1 #copies trace1 to address of self.data (needed for ROOT)
                self.tree.Fill()
                if (self.counter>0 and self.counter%100==0):
                    #self.outputfile.Write()
                    logger.info("Writing event " + str(self.counter))
            time.sleep(0.001)
        #thread ended
        self.outputfile.Write()
        self.outputfile.Close()

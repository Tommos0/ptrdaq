import numpy
import ROOT
from threading import Thread,Lock
import time
import logging
import plotter
logger = logging.getLogger('')

class dataWriter:
    thread_active = False
    def __init__(self,filename,id,display=False):
#        if filename[-6:] == "1.root":
        if display:
            self.plotter = plotter.plotter(id)
            self.plotter.start()
            logger.info("Plotter Created")
        self.outputfile = ROOT.TFile(filename,'create')
        self.tree = ROOT.TTree("gridpix","gridpix")

        self.time = numpy.zeros(1,dtype=numpy.uint32)
        self.hits = numpy.zeros(1,dtype=numpy.uint32)
        self.x=numpy.zeros(512*256,dtype=numpy.uint16)
        self.y=numpy.zeros(512*256,dtype=numpy.uint16)
        self.z=numpy.zeros(512*256,dtype=numpy.uint16)

        self.tree.Branch('hits',self.hits,'hits/i')
        self.tree.Branch('x',self.x,'x[hits]/s')
        self.tree.Branch('y',self.y,'y[hits]/s')
        self.tree.Branch('z',self.z,'z[hits]/s')
        self.tree.Branch('time',self.time,'time/i')

        self.lock = Lock()
        self.writeList = []
        
        self.counter = 0 
        self.thread = Thread(target=self.threadLoop)
        self.thread_active=True
        logger.info("writing data to: " + filename)
        self.thread.start()

    def addWrite(self,timestamp,data):
        self.lock.acquire()
        self.writeList.append((timestamp,data.copy()))
        self.lock.release()
    def stop(self):
        self.thread_active = False
        self.thread.join()
    def threadLoop(self):
        self.millis = int(round(time.time() * 1000))
        while self.thread_active:
            while (len(self.writeList)>0):
                self.counter = self.counter + 1 
                self.lock.acquire()
                p = self.writeList.pop(0)
                self.lock.release()
                self.time[0]=p[0]

                data = p[1]
                #millis = (int)(round(time.time()*1000))
                x1list = []
                y1list = []
                z1list = []
                data[256::] = numpy.rot90(numpy.copy(data[256::]),2) #rotate chip2

                xs = numpy.arange(0,512)
                ys = numpy.arange(0,256)
                #ZERO SUPPRESSION ~100x faster than looping, from stackoverflow:
                check = (0<data) #true/false array
                ind = numpy.where( check ) #array of indices where true
                x1list = xs[ ind[0] ] #x values where true
                y1list = ys[ ind[1] ] #y values where true
                z1list = data[ check ] 
                self.hits[0]=len(x1list)
                self.x[:len(x1list):] = numpy.array(x1list,dtype=numpy.uint16)
                self.y[:len(x1list):] = numpy.array(y1list,dtype=numpy.uint16)
                self.z[:len(x1list):] = numpy.array(z1list,dtype=numpy.uint16)
                #print "zero suppression took: " + str((int)(round(time.time()*1000)-millis)) + "ms"
                
                self.tree.Fill()
                if (self.counter>0 and self.counter%100==0):
                    #self.outputfile.Write()
                    logger.info("Writing event " + str(self.counter)+", nhits: " + str(self.hits[0]))
                if (int(round(time.time() * 1000))-self.millis>500):
                    try:
                        self.plotter.plot(x1list,y1list,z1list)
                    except AttributeError:
                        pass
                    self.millis = int(round(time.time() * 1000))
            time.sleep(0.001)
        #thread ended
        try:
            self.plotter.close()
        except AttributeError:
            pass
        logger.info("End of datawriter thread")
        self.outputfile.Write()
        self.outputfile.Close()

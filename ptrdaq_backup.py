from __future__ import division
import logging
from ptrsparc.ptrsparc import ptrsparc
from ptrrelaxd.ptrrelaxd import ptrrelaxd
from multiprocessing import Process, Pipe, Event
import time
logger = logging.getLogger(__name__)

def parsePipeMsg(msg,id):
    if (msg.__class__ == logging.LogRecord):
        logmsg = id + ": " + msg.getMessage()
        if (msg.levelno>20):
            logmsg = "\033[91m" + logmsg + "\033[0m" #red
        print logmsg

if __name__ == "__main__":
    events = [Event() for i in range(0,3)]

    hisparcPipe,b = Pipe()
    hisparcProcess = Process(target=ptrsparc,args=(b,events[0],[events[1],events[2]],"hisparc.root"))
    hisparcProcess.start()

    gp1Pipe,b = Pipe()
    gp1Process = Process(target=ptrrelaxd,args=(b,events[1],[events[0],events[2]],"gp1.root",1,[0,'Jan/chamber1.bpc','Jan/chamber1.bpc.dacs','Jan/chamber1.hw.dacs']))
    gp1Process.start()

    gp2Pipe,b = Pipe()
    gp2Process = Process(target=ptrrelaxd,args=(b,events[2],[events[0],events[1]],"gp2.root",2,[0,'Jan/chamber3.bpc','Jan/chamber3.bpc.dacs','Jan/chamber3.hw.dacs']))
    gp2Process.start()
    while True:
        try:
            while (hisparcPipe.poll()):
                parsePipeMsg(hisparcPipe.recv(),"HiSPARC")
            while (gp1Pipe.poll()):
                parsePipeMsg(gp1Pipe.recv(),"Gridpix 1")
            while (gp2Pipe.poll()):
                parsePipeMsg(gp2Pipe.recv(),"Gridpix 2")
            time.sleep(0.001)
        except KeyboardInterrupt:
            print "keyboard interrupt, flushing buffers to files..."
            events[0].set()
            events[1].set()
            events[2].set()
            hisparcPipe.send("stop")
            gp1Pipe.send("stop")
            gp2Pipe.send("stop")
            break

    print "waiting for hisparc to finish..."
    hisparcProcess.join()
    while (hisparcPipe.poll()):
        parsePipeMsg(hisparcPipe.recv(),"HiSPARC")

    print "waiting for gp1 to finish..."
    gp1Process.join()
    while (gp1Pipe.poll()):
        parsePipeMsg(gp1Pipe.recv(),"Gridpix 1")

    print "waiting for gp2 to finish..."
    gp2Process.join()
    while (gp2Pipe.poll()):
        parsePipeMsg(gp2Pipe.recv(),"Gridpix 2")

    print "done"

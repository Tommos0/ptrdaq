import numpy as np
import matplotlib
matplotlib.use("qt4Agg")
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from multiprocessing import Process, Pipe
from threading import Thread
import time

class plotter:
    def updater(self,pipe):
        while (self.running):
            while (pipe.poll()):
                d = pipe.recv()
                if (d == "stop"):
                    print "plotter got stop"
                    self.running=False
                    break
                xlist = d[0]
                ylist = d[1]
                zlist = d[2]
                plt.cla()
                self.ax1.scatter(xlist,ylist,zlist)           
                self.ax1.set_xlim3d(0,512,30)
                self.ax1.set_ylim3d(0,256,30)
                self.ax1.set_zlim3d(0,12000,5)
                plt.draw()
                self.fig.canvas.draw()
            time.sleep(0.1)
        plt.close()
        print "plotter done"
    def plotProcess(self,pipe,id):
        self.running = True
        self.thread = Thread(target=self.updater,args=(pipe,))
        self.thread.start()
        self.fig = plt.figure()
        self.fig.canvas.set_window_title("Gridpix " + str(id))
        self.ax1 = Axes3D(self.fig)
        self.ax1.scatter([],[],[])           
        self.ax1.set_xlim3d(0,512,30)
        self.ax1.set_ylim3d(0,256,30)
        self.ax1.set_zlim3d(0,12000,5)
        plt.draw()
        plt.show()
        print "Plot shown"
        self.thread.join()
    def __init__(self,id):
        pipe,b = Pipe()
        self.pipe = pipe
        self.proc = Process(target=self.plotProcess,args=(b,id))
        self.proc.start()

    def plot(self,xlist,ylist,zlist):
        self.pipe.send((xlist,ylist,zlist))

    def close(self):
#        self.running=False
        self.pipe.send("stop")
        time.sleep(1)
        print "joining plotter"
        self.proc.join()
        print "plotter joined"


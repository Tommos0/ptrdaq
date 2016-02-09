#!/usr/bin/env python

# embedding_in_qt4.py --- Simple Qt4 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

from __future__ import unicode_literals
import sys, os, random
from PyQt4 import QtGui, QtCore

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from threading import Thread
from multiprocessing import Process,Pipe
import time

class plotter(Process):
    def __init__(self,id):
        Process.__init__(self)
        self.pipe, self.pipeEnd = Pipe()
        self.id = id
    def run(self):
        qApp = QtGui.QApplication(sys.argv)

        self.aw = ApplicationWindow(self.pipeEnd)
        self.aw.setWindowTitle("Track display: GP "+str(self.id))
        self.aw.show()
        #sys.exit(qApp.exec_())
        qApp.exec_()
    def plot(self,xlist,ylist,zlist):
        self.pipe.send((xlist,ylist,zlist))

    def close(self):
        #self.aw.fileQuit()
        self.pipe.send("stop")
        pass
#qApp.exec_()

class Canvas3d(FigureCanvas):
    def __init__(self,aw,parent=None,pipe=None):
        fig = Figure()
        self.axes = Axes3D(fig)
        self.axes.hold(False)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.aw = aw
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.counter = 0
        self.axes.mouse_init()
        self.thread = Thread(target=self.threadloop,args=(pipe,))
        self.thread.start()
    def compute_initial_figure(self):
        self.axes.scatter([],[],[])           
        self.axes.set_xlim3d(0,512,30)
        self.axes.set_ylim3d(0,256,30)
        self.axes.set_zlim3d(0,200,5)
    def threadloop(self,pipe):
        self.running=True
        while (self.running):
            while (pipe.poll()):
                d = pipe.recv()
                if (d == "stop"):
                    self.running=False
                    self.aw.close()
                    break
                xlist = d[0]
                ylist = d[1]
                zlist = d[2]
#                plt.cla()
                self.axes.scatter(xlist,ylist,zlist)           
                self.axes.set_xlim3d(0,512,30)
                self.axes.set_ylim3d(0,256,30)
                self.axes.set_zlim3d(0,200,5)
                self.draw()
            time.sleep(0.1)

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self,pipe):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QVBoxLayout(self.main_widget)
        #sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
      #  sc = Canvas3d(self.main_widget)
        self.dc = Canvas3d(self,self.main_widget,pipe)
        #dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
      #  l.addWidget(sc)
        l.addWidget(self.dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        #self.statusBar().showMessage("All hail matplotlib!", 2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""embedding_in_qt4.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale

This program is a simple example of a Qt4 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
)



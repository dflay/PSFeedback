#! /usr/bin/python 
 
from PyQt5.QtCore import QTime, QTimer
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import *
# import pyqtgraph as pg

from collections import deque

import time 

from util import *
# import vxi11
from instrument import yokogawa 

class YokoGUI(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        super(YokoGUI, self).__init__(*args, **kwargs)
 
        # not sure what these are for... 
        self.t = QTime()
        self.t.start()

        # ----------------------------------------------------------------------        
        # some parameters that we can set 
        # plot variables 
        self.time_delay   =  250                # in milliseconds  
        self.iMin         = -260                # in milliamps  
        self.iMax         =  260                # in milliamps 
        # vectors for plotting data  
        self.max_len         = 200
        self.data_x          = deque(maxlen=self.max_len)
        self.data_y          = deque(maxlen=self.max_len) 

        # directories and filenames 
        self.dataDIR      = "./data" 
        self.dataFN       = "yokogawa"
        self.setpointFN   = "setpoint_history"
        self.fileEXT      = "csv"
        # yokogawa stuff 
        self.yoko_readout_delay = 0.50          # time in seconds 
        self.yoko_status        = "NONE"

        # my variables 
        self.yoko            = yokogawa()       # yokogawa object  
        self.runMgr          = RunManager()
        self.fileMgr         = FileManager()
        self.statusMgr       = StatusManager()  
        self.runMgr.dataDir  = self.dataDIR 
        self.fileMgr.dataDir = self.dataDIR 
        self.fileMgr.fileEXT = self.fileEXT 

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        # set colors 
        # background is the canvas color 
        # foreground is the axes colors 
        pg.setConfigOption('background','w')  # w is white 
        pg.setConfigOption('foreground','k')  # k is black
        
        #QtGui.QApplication.setGraphicsSystem('raster')
        self.win  = QtGui.QMainWindow()
        self.area = DockArea()
        self.win.setCentralWidget(self.area)
        self.win.resize(1000,600)
        
        # make docks  
        self.d1 = Dock("Dock1", size=(500 ,300))
        self.d2 = Dock("Dock2", size=(1000,600))
        self.d3 = Dock("Dock3", size=(500 ,300))
        
        # add the docks 
        self.area.addDock(self.d1,'top')
        self.area.addDock(self.d2,'bottom')
        self.area.addDock(self.d3,'top')

        # dock 1
        # buttons and entry fields 
        # put an entry field for a setpoint 
        self.d1.hideTitleBar()
        self.w1            = pg.LayoutWidget()
        # IP address
        self.ip_label      = QtGui.QLabel("IP Address")
        self.ip_entryField = QtGui.QLineEdit()
        self.connBtn       = QtGui.QPushButton('Connect')
        self.w1.addWidget(self.ip_label     ,row=0, col=0)
        self.w1.addWidget(self.ip_entryField,row=0, col=1)
        self.w1.addWidget(self.connBtn      ,row=0, col=2)
        # manual and auto modes
        self.manual_mode = 1
        self.auto_mode   = 0
        self.mode_label  = QtGui.QLabel("Mode")
        self.manBtn      = QtGui.QPushButton('Manual')
        self.autoBtn     = QtGui.QPushButton('Auto')
        self.w1.addWidget(self.mode_label   ,row=1, col=0)
        self.w1.addWidget(self.manBtn       ,row=1, col=1)
        self.w1.addWidget(self.autoBtn      ,row=1, col=2)
        # set point 
        self.label      = QtGui.QLabel("Setpoint (mA)")
        self.setPtField = QtGui.QLineEdit()
        self.setPtBtn   = QtGui.QPushButton('Apply')
        self.w1.addWidget(self.label        ,row=2, col=0)
        self.w1.addWidget(self.setPtField   ,row=2, col=1)
        self.w1.addWidget(self.setPtBtn     ,row=2, col=2)
        # button functions 
        self.manBtn.clicked.connect(self.setManualMode) 
        self.autoBtn.clicked.connect(self.setAutoMode) 
        self.setPtBtn.clicked.connect(self.applySetPt)
        self.connBtn.clicked.connect(self.connectToDevice)  
        # add the widget to the dock 
        self.d1.addWidget(self.w1)

        # dock 2: the plot  
        self.d2.hideTitleBar()
        # w2 = pg.PlotWidget(title="Yokogawa Current")
        self.w2 = pg.PlotWidget(title="Yokogawa Current",axisItems = {'bottom': TimeAxisItem(orientation='bottom')})
        self.w2.getPlotItem().setLabel('left'  ,'Current'     ,units='mA')  # y axis 
        # w2.getPlotItem().setLabel('bottom','Event Number',units='')    # x axis
        # self.w2.getPlotItem().setLabel('bottom','Time',units='hr:min:sec')    # x axis
        self.w2.getPlotItem().setYRange(self.iMin,self.iMax)
        self.myPlot = self.w2.plot(pen='b')
        self.d2.addWidget(self.w2)

        # dock 3: status bar 
        self.d3.hideTitleBar()
        self.w3       = pg.LayoutWidget()
        # a status bar 
        self.current_status = "System: Idle"
        self.statusBar = QtGui.QStatusBar() 
        self.w3.addWidget(self.statusBar,row=0,col=0)
        self.statusBar.showMessage(self.current_status) 
        # a bunch of buttons
        self.startBtn = QtGui.QPushButton('Start Run')
        self.stopBtn  = QtGui.QPushButton('Stop Run')
        self.quitBtn  = QtGui.QPushButton('Quit')
        self.w3.addWidget(self.startBtn,row=1, col=0)
        self.w3.addWidget(self.stopBtn ,row=1, col=1)
        self.w3.addWidget(self.quitBtn ,row=1, col=2)
        # button functions 
        self.startBtn.clicked.connect(self.startRun)
        self.stopBtn.clicked.connect(self.stopRun)
        self.quitBtn.clicked.connect(self.killDAQ)
        # add the widget to the dock 
        self.d3.addWidget(self.w3)

        self.tmr = QTimer()
        self.tmr.timeout.connect(self.update)

        self.win.show() 

    def connectToDevice(self):
        rc = 1 
        self.statusMgr.ipAddr = self.ip_entryField.text() 
        if self.statusMgr.isConnected==False: 
            self.statusBar.showMessage("System: Connecting to device with IP address %s" %(self.statusMgr.ipAddr) ) 
            rc = self.yoko.open_vxi_connection(self.statusMgr.ipAddr)
            self.yoko_status = self.yoko.status_msg 
            self.statusBar.showMessage("System: %s" %(self.yoko_status) ) 
            if(rc==0):
                # ok, we're connected.  set to current mode, set to max range 
                self.yoko.set_to_current_mode() 
                self.yoko.set_range_max() 
                self.yoko.set_level(0.0)               # set to zero mA
                self.statusMgr.isConnected = True 
        else: 
            self.statusBar.showMessage("System: Already connected at IP address %s" %(self.statusMgr.ipAddr) ) 

    def applySetPt(self):
        text     = self.setPtField.text()
        try: 
            val = float(text)
            self.statusMgr.updateSetPoint(val)
            self.statusBar.showMessage( "System: The setpoint is now %.3f mA" %(self.statusMgr.currentSetPoint) ) 
        except: 
            self.statusBar.showMessage( "System: Invalid setpoint value!  No action taken") 
        # FIXME: program the Yokogawa 

    def setManualMode(self):
        self.statusMgr.manualMode = 1
        self.statusMgr.autoMode   = 0
        self.statusBar.showMessage("System: In manual mode") 
        # FIXME: program the Yokogawa, don't look at file  

    def setAutoMode(self):
        self.statusMgr.manualMode = 0
        self.statusMgr.autoMode   = 1
        self.statusBar.showMessage("System: In auto mode") 
        # FIXME: toggle to look at a file  

    def startRun(self):
        if self.runMgr.isRunning==False: 
            # start readout of yokogawa 
            self.tmr.start(self.time_delay)
            # get the run number, set to active status 
            self.runMgr.updateRunNumber() 
            self.fileMgr.makeDirectory(self.runMgr.runNum)  
            self.runMgr.isRunning = True
            # update the setpoint (get a timestamp on the current setpoint, even if zero)  
            self.statusMgr.updateSetPoint(self.statusMgr.currentSetPoint)
            # update status banner 
            self.statusBar.showMessage("System: Run %d started" %(self.runMgr.runNum) ) 
            # enable the output on the yokogawa 
            self.yoko.enable_output()                   
        else: 
            self.statusBar.showMessage("System: Run %d already started" %(self.runMgr.runNum) ) 

    def stopRun(self):
        if self.runMgr.isRunning==True: 
           # disable the output on the yokogawa 
           self.yoko.disable_output()                   
           # stop readout  
           self.tmr.stop()
           # run is no longer active 
           self.runMgr.isRunning = False
           # print setpoint history 
           self.fileMgr.writeSetPointHistoryFile(self.runMgr.runNum,self.setpointFN,self.statusMgr.tsList,self.statusMgr.spList)
           self.statusMgr.clearSetPointHistory() # clear for next run 
           # update status banner 
           filePath = "%s/run-%05d/%s.%s" %(self.dataDIR,self.runMgr.runNum,self.setpointFN,self.fileEXT)
           self.statusBar.showMessage("System: Run %d stopped.  Set point history written to %s." %(self.runMgr.runNum,filePath) ) 

    def killDAQ(self): 
        # FIXME: set Yokogawa to zero, disable, and disconnect 
        if self.runMgr.isRunning==True:
            self.statusBar.showMessage("System: Cannot quit until run %d is stopped" %(self.runMgr.runNum) )
        else:  
            # set the yokogawa level to zero 
            self.yoko.set_level(0.);
            # close the connection  
            self.yoko.close_vxi_connection() 
            # quit the GUI 
            QtCore.QCoreApplication.instance().quit()
        
    # generate the data 
    def update(self):
        # FIXME: readout value from the yokogawa 
        x = now_timestamp()
        if self.statusMgr.manualMode==1: 
           y = self.statusMgr.currentSetPoint  
        else: 
           y = get_data()
        # program the yokogawa 
        self.yoko.set_level(y) 
        # wait a bit 
        time.sleep(self.yoko_readout_delay)
        lvl = self.yoko.get_level() 
        rc = self.fileMgr.appendToFile(self.runMgr.runNum,self.dataFN,x,lvl) 
        if rc==1: 
            self.statusBar.showMessage("System: Cannot write data to file for run %d" %(self.runMgr.runNum) )
        self.data_x.append(x)
        self.data_y.append(lvl)
        self.myPlot.setData(x=list(self.data_x), y=list(self.data_y))

def main():
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    app = YokoGUI(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


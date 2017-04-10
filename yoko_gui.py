#! /usr/bin/python 
 
from PyQt5.QtCore import QTime, QTimer, Qt
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import *
# import pyqtgraph as pg

from collections import deque

import time

from pid import PID 
from util import *
from instrument import yokogawa 

class ParameterDialog(QtGui.QDialog): 
    def __init__(self,parent=None): 
        super(ParameterDialog,self).__init__(parent)  

        self.myLayout = QtGui.QVBoxLayout(self)

        self.header   = QtGui.QLabel("PID Loop Parameters") 
        self.pLabel   = QtGui.QLabel("P Value") 
        self.iLabel   = QtGui.QLabel("I Value") 
        self.dLabel   = QtGui.QLabel("D Value") 
        self.pField   = QtGui.QLineEdit()
        self.iField   = QtGui.QLineEdit()
        self.dField   = QtGui.QLineEdit()
        # add objects to the layout 
        self.myLayout.addWidget(self.header)
        self.myLayout.addWidget(self.pLabel)
        self.myLayout.addWidget(self.pField)
        self.myLayout.addWidget(self.iLabel)
        self.myLayout.addWidget(self.iField)
        self.myLayout.addWidget(self.dLabel)
        self.myLayout.addWidget(self.dField)
        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
                       QtGui.QDialogButtonBox.Ok | 
                       QtGui.QDialogButtonBox.Cancel, 
                       Qt.Horizontal, 
                       self)
        self.myLayout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def getPars(self):
        pVal = self.pField.text() 
        iVal = self.iField.text() 
        dVal = self.dField.text() 
        return (pVal,iVal,dVal)  

    @staticmethod # make a static method that obtains the values from the dialog 
    def getParameters(parent=None): 
        dialog = ParameterDialog(parent)
        result = dialog.exec_()
        pVal,iVal,dVal = dialog.getPars() 
        return (pVal,iVal,dVal,result==QtGui.QDialog.Accepted)
 
class YokoGUI(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        super(YokoGUI, self).__init__(*args, **kwargs)
 
        # not sure what these are for... 
        self.t = QTime()
        self.t.start()

        # ----------------------------------------------------------------------        
        # some parameters that we can set 
        # plot variables 
        self.time_delay      =  250                # in milliseconds  
        self.iMin            = -260                # in milliamps  
        self.iMax            =  260                # in milliamps 
        self.CONV_mA_TO_AMPS = 1E-3                # conversion mA -> A  
        self.LOWER_LIMIT     = -200                # in mA 
        self.UPPER_LIMIT     =  200                # in mA  
        # vectors for plotting data  
        self.max_len         = 200
        self.data_x          = deque(maxlen=self.max_len)
        self.data_y          = deque(maxlen=self.max_len) 

        # directories and filenames 
        self.dataDIR      = "./data" 
        self.dataFN       = "yokogawa"
        self.setpointFN   = "setpoint_history"
        self.pidFN        = "pid_history"
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
        self.lvl             = 0                # level read back from Yokogawa  
        self.prev_lvl        = 0                # the previous level 
        self.pidLoop         = PID() 
        self.pidLoop.setKp(0.6)  
        self.pidLoop.setKi(0.8)  
        self.pidLoop.setKd(0.) 
        self.pidLoop.setSampleTime(0.01) 

        self.statusMgr.isSimMode = True         # ignore yokogawa, get random data 
        self.statusMgr.manualMode = 1           # default to manual mode 
        self.statusMgr.autoMode   = 0

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
        self.disconnBtn    = QtGui.QPushButton('Disconnect')
        self.w1.addWidget(self.ip_label     ,row=0, col=0)
        self.w1.addWidget(self.ip_entryField,row=0, col=1)
        self.w1.addWidget(self.connBtn      ,row=0, col=2)
        self.w1.addWidget(self.disconnBtn   ,row=0, col=3)
        # manual and auto modes
        self.manual_mode = 1
        self.auto_mode   = 0
        self.paramWidget = QtGui.QWidget() 
        self.mode_label  = QtGui.QLabel("Mode")
        self.manBtn      = QtGui.QPushButton('Manual')
        self.autoBtn     = QtGui.QPushButton('Auto')
        self.paramBtn    = QtGui.QPushButton('Set Parameters...',self.paramWidget)
        self.w1.addWidget(self.mode_label   ,row=1, col=0)
        self.w1.addWidget(self.manBtn       ,row=1, col=1)
        self.w1.addWidget(self.autoBtn      ,row=1, col=2)
        self.w1.addWidget(self.paramBtn     ,row=1, col=3)
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
        self.disconnBtn.clicked.connect(self.disconnectFromDevice) 
        self.paramBtn.clicked.connect(self.ShowParamWindow) 
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
        # main status bar 
        self.mstatusBar = QtGui.QStatusBar() 
        self.mstatusBar.showMessage( "Run: -- | Setpoint: %.3f mA | Mode: Manual" %(self.statusMgr.currentSetPoint) ) 
        # a status bar 
        self.current_status = "System: Idle"
        self.statusBar = QtGui.QStatusBar() 
        self.statusBar.showMessage(self.current_status) 
        # a bunch of buttons
        self.startBtn = QtGui.QPushButton('Start Run')
        self.stopBtn  = QtGui.QPushButton('Stop Run')
        self.quitBtn  = QtGui.QPushButton('Quit')
        # add widgets 
        self.w3.addWidget(self.mstatusBar,row=0,col=0)
        self.w3.addWidget(self.statusBar ,row=1,col=0)
        self.w3.addWidget(self.startBtn  ,row=2,col=0)
        self.w3.addWidget(self.stopBtn   ,row=2,col=1)
        self.w3.addWidget(self.quitBtn   ,row=2,col=2)
        # button functions 
        self.startBtn.clicked.connect(self.startRun)
        self.stopBtn.clicked.connect(self.stopRun)
        self.quitBtn.clicked.connect(self.killDAQ)
        # add the widget to the dock 
        self.d3.addWidget(self.w3)


        self.tmr = QTimer()
        self.tmr.timeout.connect(self.update)

        self.win.show() 

    def ShowParamWindow(self): 
        pVal,iVal,dVal,ok = ParameterDialog.getParameters()
        if ok: 
           PVAL   = float(pVal)
           IVAL   = float(iVal)
           DVAL   = float(dVal)
           self.statusMgr.updatePID(PVAL,IVAL,DVAL) 
           self.pidLoop.setKp(self.statusMgr.currentP)
           self.pidLoop.setKi(self.statusMgr.currentI)
           self.pidLoop.setKd(self.statusMgr.currentD)
           msg    = "System: Updated PID parameters: P = %.3f, I = %.3f, D = %.3f" \
                    %(self.statusMgr.currentP,self.statusMgr.currentI,self.statusMgr.currentD)
           self.statusBar.showMessage(msg)

    def connectToDevice(self):
        rc = 1 
        self.statusMgr.ipAddr = self.ip_entryField.text() 
        if self.statusMgr.ipAddr=="": 
            self.statusBar.showMessage("System: IP address string is empty!") 
        else:  
            if self.statusMgr.isConnected==False: 
                if(self.statusMgr.isSimMode==False): 
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
                        self.mstatusBar.showMessage( self.getSystemStatus() )
                else: 
                    self.statusBar.showMessage("System: Cannot connect to device, in simulation mode") 
            else: 
                self.statusBar.showMessage("System: Already connected at IP address %s" %(self.statusMgr.ipAddr) ) 

    def disconnectFromDevice(self): 
        if self.statusMgr.isSimMode==False: 
            if self.statusMgr.isConnected==True: 
                if self.runMgr.isRunning==False: 
                    self.yoko.disable_output() 
                    self.yoko.close_vxi_connection() 
                    self.yoko_status = self.yoko.status_msg 
                    self.statusBar.showMessage("System: %s" %(self.yoko_status) ) 
                    self.statusMgr.isConnected = False
                    self.mstatusBar.showMessage( self.getSystemStatus() )
                else: 
                    self.statusBar.showMessage("System: Cannot disconnect from the Yokogawa during a run!") 
            else: 
                self.statusBar.showMessage("System: Already disconnected from the Yokogawa.") 
        else: 
            self.statusBar.showMessage("System: In simulation mode, nothing to disconnect from.") 

    def applySetPt(self):
        text     = self.setPtField.text()
        try: 
            val = float(text)
            if val>self.LOWER_LIMIT and val<self.UPPER_LIMIT: 
                self.statusMgr.updateSetPoint(val)
                self.pidLoop.SetPoint = self.statusMgr.currentSetPoint 
                msg = "System: The setpoint is now %.3f mA" %(self.pidLoop.SetPoint)
            else:
                msg = "System: Setpoint out of bounds!  " \
                      "Requested: %.3f mA;  " \
                      "limits: low = %.3f, high = %.3f" %(val,self.LOWER_LIMIT,self.UPPER_LIMIT) 
            self.statusBar.showMessage(msg) 
        except: 
            self.statusBar.showMessage("System: Invalid setpoint value [NaN]!  No action taken") 
        self.mstatusBar.showMessage( self.getSystemStatus() )

    def setManualMode(self):
        self.statusMgr.manualMode = 1
        self.statusMgr.autoMode   = 0
        self.statusBar.showMessage("System: In manual mode") 
        self.mstatusBar.showMessage( self.getSystemStatus() )

    def setAutoMode(self):
        self.statusMgr.manualMode = 0
        self.statusMgr.autoMode   = 1
        self.statusBar.showMessage("System: In auto mode") 
        self.mstatusBar.showMessage( self.getSystemStatus() )

    def getSystemStatus(self):
        # determine a message to display in top banner
        if self.runMgr.isRunning==True: 
            run_state = "Active"
        else:  
            run_state = "Stopped"
        if self.statusMgr.manualMode==1:
            mode = "Manual"
        else: 
            mode = "Auto" 
        msg = "Run: %d (%s) | Setpoint: %.3lf mA | Mode: %s" %(self.runMgr.runNum,run_state,self.statusMgr.currentSetPoint,mode)
        if self.statusMgr.isConnected==True: 
            msg = "%s | Connected to device at IP address: %s" %(msg,self.statusMgr.ipAddr)
        return msg 

    def startRun(self):
        if self.statusMgr.isSimMode==True: 
            if self.runMgr.isRunning==False: 
                # start readout  
                self.tmr.start(self.time_delay)
                # get the run number, set to active status 
                self.runMgr.updateRunNumber() 
                self.fileMgr.makeDirectory(self.runMgr.runNum)  
                self.runMgr.isRunning = True
                # update the setpoint (get a timestamp on the current setpoint, even if zero)  
                self.statusMgr.updateSetPoint(self.statusMgr.currentSetPoint)
                # update status banner 
                self.statusBar.showMessage("System: Run %d started" %(self.runMgr.runNum) ) 
                self.mstatusBar.showMessage( self.getSystemStatus() )
            else: 
                self.statusBar.showMessage("System: Run %d already started" %(self.runMgr.runNum) ) 
        else: 
            if self.runMgr.isRunning==False: 
                # check for connectivity 
                if self.statusMgr.isConnected==True: 
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
                    self.statusBar.showMessage("System: Cannot start the run, not connected to the Yokogawa.") 
            else: 
                self.statusBar.showMessage("System: Run %d already started" %(self.runMgr.runNum) ) 


    def stopRun(self):
        if self.runMgr.isRunning==True: 
           # disable the output on the yokogawa
           if self.statusMgr.isSimMode==False:  
               self.yoko.disable_output()                   
           # stop readout  
           self.tmr.stop()
           # run is no longer active 
           self.runMgr.isRunning = False
           # print setpoint history 
           self.fileMgr.writeSetPointHistoryFile(self.runMgr.runNum,self.setpointFN,self.statusMgr.tsList,self.statusMgr.spList)
           self.statusMgr.clearSetPointHistory() # clear for next run 
           self.fileMgr.writePIDHistoryFile(self.runMgr.runNum,self.pidFN, \
                                            self.statusMgr.tPIDList,self.statusMgr.pList,self.statusMgr.iList,self.statusMgr.dList)
           self.statusMgr.clearPIDHistory() # clear for next run 
           # update status banner 
           filePath = "%s/run-%05d/%s.%s" %(self.dataDIR,self.runMgr.runNum,self.setpointFN,self.fileEXT)
           # msg = "System: Run %d stopped.  Set point history written to: %s." %(self.runMgr.runNum,filePath) 
           msg = "System: Run %d stopped." %(self.runMgr.runNum) 
           self.statusBar.showMessage(msg) 
           self.mstatusBar.showMessage( self.getSystemStatus() )

    def killDAQ(self): 
        if self.runMgr.isRunning==True:
            self.statusBar.showMessage("System: Cannot quit until run %d is stopped" %(self.runMgr.runNum) )
        else: 
            if self.statusMgr.isSimMode==False: 
                if self.statusMgr.isConnected==True:  
                    # set the yokogawa level to zero 
                    self.yoko.set_level(0.) 
                    # disable the output 
                    self.yoko.disable_output() 
                    # close the connection  
                    self.yoko.close_vxi_connection()
                    self.statusMgr.isConnected = False  
            # quit the GUI 
            QtCore.QCoreApplication.instance().quit()
        
    # generate the data 
    def update(self):
        x = now_timestamp()
        if self.statusMgr.manualMode==1: 
           y = self.statusMgr.currentSetPoint     
        else: 
           y = self.get_data()    
        # check the level 
        if y>self.LOWER_LIMIT and y<self.UPPER_LIMIT: 
           # looks good, do nothing 
           y = y 
        else: 
           msg = "System: Invalid level of %.3f attempted!  Setting to 80 percent of maximum." %(y)
           if y>0: y = 0.8*self.UPPER_LIMIT 
           if y<0: y = 0.8*self.LOWER_LIMIT
           self.statusBar.showMessage(msg)
                              
        if self.statusMgr.isSimMode==False: 
            # program the yokogawa 
            if self.prev_lvl!=y:                          # check to see if the yokogawa level changed 
                self.yoko.set_level(y)                    # FIXME: relatively certain that we set the current in mA  
            # wait a bit 
            time.sleep(self.yoko_readout_delay)
            self.lvl = self.yoko.get_level()/self.CONV_mA_TO_AMPS   # the readout is in Amps; convert to mA   
        else:
            # test mode; use the random data  
            self.lvl = y 
        rc = self.fileMgr.appendToFile(self.runMgr.runNum,self.dataFN,x,self.lvl) 
        if rc==1: 
            self.statusBar.showMessage("System: Cannot write data to file for run %d" %(self.runMgr.runNum) )
        self.data_x.append(x)
        self.data_y.append(self.lvl)   
        self.myPlot.setData(x=list(self.data_x), y=list(self.data_y))
        # save the level as the previous one 
        self.prev_lvl = self.lvl 

    def get_data(self):  
        # this is where we would get some value from the fixed probes
        # for now, use a random number generator  
        val = get_random(self.LOWER_LIMIT,self.UPPER_LIMIT)
        self.pidLoop.update(val)       # how does the fixed probe readout compare to the setpoint?    
        return self.pidLoop.output 
        

def main():
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    app = YokoGUI(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


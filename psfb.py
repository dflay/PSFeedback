#! /usr/bin/python 
# Power supply feedback software 
# - Relies on parameters in the ./input/parameters.csv file to do certain actions 
# - Will run indefinitely until a kill signal is sent via the psfb_set_pars program     

# FIXME:
# 1. Automatic run start/stop: make a run a certain length of time, change run numbers automatically 
# 2. Turn readParameters and subsequent setting of various data objects into a function? 
# 3. System should be IDLE unless a run is triggered 
# 4. Finish ROOT file output implementation 

import sys 
import time 
from instrument import yokogawa 
from timeit     import default_timer as timer
from data_structures import * 
from pid import PID 
# start a timer 
t_start = timer()

# global variables 
gLOWER_LIMIT  = -200 # in mA 
gUPPER_LIMIT  =  200 # in mA 
gPrevLvl      = 0    # in mA 
gReadoutDelay = 0.5  # in seconds 


#_______________________________________________________________________________
def startRun(statusMgr,runMgr,yoko):
    if statusMgr.isSimMode==True:
        if runMgr.isRunning==False:
            # get the run number, set to active status 
            runMgr.updateRunNumber()
            runMgr.isRunning = True
            # update the setpoint (get a timestamp on the current setpoint, even if zero)  
            statusMgr.updateSetPoint(statusMgr.currentSetPoint)
    else:
        if runMgr.isRunning==False:
            # check for connectivity 
            if statusMgr.isConnected==True:
                # get the run number, set to active status 
                runMgr.updateRunNumber()
                runMgr.isRunning = True
                # update the setpoint (get a timestamp on the current setpoint, even if zero)  
                statusMgr.updateSetPoint(self.statusMgr.currentSetPoint)
                # enable the output on the yokogawa 
                yoko.enable_output()                 

    def stopRun(statusMgr,runMgr,yoko):
        if runMgr.isRunning==True:
           # disable the output on the yokogawa
           if statusMgr.isSimMode==False:
               yoko.disable_output()
           # run is no longer active 
           runMgr.isRunning = False

    def killDAQ(statusMgr,runMgr,yoko):
        if statusMgr.isSimMode==False:
            if statusMgr.isConnected==True:
                # set the yokogawa level to zero 
                yoko.set_level(0.)
                # disable the output 
                yoko.disable_output()
                # close the connection  
                yoko.close_vxi_connection()
                statusMgr.isConnected = False
    # generate the data 
    def readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko):
        global gPrevLvl,gReadoutDelay,gLOWER_LIMIT,gUPPER_LIMIT 
        dataFN     = "ps-feedback"
        yoko_event = YokogawaEvent() 
        x = now_timestamp()
        if statusMgr.manualMode==1:
           y = statusMgr.currentSetPoint
        else:
           y = get_data()
        # check the level 
        if y>gLOWER_LIMIT and y<gUPPER_LIMIT:
           # looks good, do nothing 
           y = y
        else:
           msg = "System: Invalid level of %.3f attempted!  Setting to 80 percent of maximum." %(y)
           if y>0: y = 0.8*gUPPER_LIMIT
           if y<0: y = 0.8*gLOWER_LIMIT
        # now program the yokogawa 
        if statusMgr.isSimMode==False:
            if gPrevLvl!=y:                          # check to see if the yokogawa level changed 
                yoko.set_level(y)                    # FIXME: relatively certain that we set the current in mA  
            # wait a bit 
            time.sleep(gReadoutDelay)
            my_lvl   = float( self.yoko.get_level() )
            lvl      = my_lvl/self.CONV_mA_TO_AMPS   # the readout is in Amps; convert to mA   
        else:
            # test mode; use the random data  
            lvl = y
        # save the data to the event object 
        yoko_event.ID             = yoko_event.ID + 1
        yoko_event.timestamp      = x
        yoko_event.current        = lvl
        yoko_event.setpoint       = statusMgr.currentSetPoint
        yoko_event.is_manual      = statusMgr.manualMode
        if statusMgr.isSimMode==False:
            yoko_event.output_enabled = int( yoko.get_output_state() )
        else:
            yoko_event.output_enabled = 0
        yoko_event.p_fdbk             = pidLoop.Kp
        yoko_event.i_fdbk             = pidLoop.Ki
        yoko_event.d_fdbk             = pidLoop.Kd
        # now write to file 
        rc = fileMgr.writeYokogawaEvent(runMgr.runNum,dataFN,yoko_event)
        # rc = fileMgr.writeROOTFile(runMgr.runNum,dataFN,yoko_event)
        if rc==1:
            print("System: Cannot write data to file for run %d" %(runMgr.runNum) )
        # save the level as the previous one 
        gPrevLvl = lvl
#_______________________________________________________________________________

fileMgr   = FileManager()
statusMgr = StatusManager()
runMgr    = RunManager()
pidLoop   = PID() 

dataDIR   = './data'
fileEXT   = 'csv'

# initialization
fileMgr.fileEXT = fileEXT  
fileMgr.dataDIR = dataDIR 
runMgr.dataDIR  = dataDIR
pidLoop         = PID()
pidLoop.setKp(0.6)
pidLoop.setKi(0.8)
pidLoop.setKd(0.)
pidLoop.setSampleTime(0.01)

isRunning_prev = False 
parList = [] 

# get instance of yokogawa object  
yoko    = yokogawa()
# open the VXI-connection  
ip_addr = "192.168.5.160"  
rc = yoko.open_vxi_connection(ip_addr)
print(yoko.status_msg)
if rc==1:
    sys.exit()
else: 
    # set up device for reading 
    yoko.set_to_current_mode() 
    yoko.set_range_max() 
    yoko.set_level(0.) 
    yoko.enable_output() 
 
# now start an infinite loop
while(1):
    # read from parameter file 
    parList       = fileMgr.readParameters() 
    runStatus     = int(parList[0])
    simMode       = int(parList[1])
    manMode       = int(parList[2])
    stop          = int(parList[3]) 
    setpoint      = float(parList[4])
    P             = float(parList[5])
    I             = float(parList[6])
    D             = float(parList[7]) 
    # update status manager  
    statusMgr.updateSetPoint(setpoint)
    statusMgr.updatePID(P,I,D)
    pidLoop.setKp(statusMgr.currentP) 
    pidLoop.setKi(statusMgr.currentI) 
    pidLoop.setKd(statusMgr.currentD) 
    if simMode==1: 
        statusMgr.isSimMode = True
    else 
        statusMgr.isSimMode = False
    if manMode==1:
        statusMgr.manualMode = True  
        statusMgr.autoMode   = False 
    else:  
        statusMgr.manualMode = False  
        statusMgr.autoMode   = True
    # update run manager
    if runStatus==1: 
        runMgr.isRunning = True
    else:   
        runMgr.isRunning = False 
    # check run status 
    if runMgr.isRunning==False and isRunning_prev==True: 
       stopRun(statusMgr,runMgr,yoko) 
    elif runMgr.isRunning==True and isRunning_prev==False:
       # start a run 
       startRun(statusMgr,runMgr,yoko)
    elif stop==1:  
       killDAQ(statusMgr,runMgr,yoko)
       break  # leave the infinite loop  
    else: 
       # run is still going, read out the event 
       readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko)
    # setup for next iteration  
    isRunning_prev = runMgr.isRunning 
        
# stop the timer 
t_stop = timer() 
dt     = t_stop - t_start
print("elapsed time: {0:.4f}".format(dt))



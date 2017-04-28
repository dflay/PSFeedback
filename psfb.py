#! /usr/bin/python 
# Power supply feedback software 
# - Relies on parameters in the ./input/parameters.csv file to do certain actions 
# - Will run indefinitely until a kill signal is sent via the psfb_set_pars program     

# FIXME:
# 1. Finish ROOT file output implementation 
# 2. Implement a kill signal to exit this program safely 

import sys 
import time 
from instrument import yokogawa 
from timeit     import default_timer as timer
from data_structures import * 
from pid import PID 

# global variables 
gLOWER_LIMIT  = -200 # in mA 
gUPPER_LIMIT  =  200 # in mA 
gPrevLvl      = 0    # in mA 
gReadoutDelay = 0.5  # in seconds 
ip_addr       = "192.168.5.160" 
gRunTime      = 100  # in seconds   

#_______________________________________________________________________________
def getParameters(statusMgr,runMgr,fileMgr,pidLoop): 
    # read from parameter file 
    parList   = fileMgr.readParameters() 
    daqStatus = int(parList[0])  # 0 = inactive, 1 = active  
    simMode   = int(parList[1])
    manMode   = int(parList[2])
    setpoint  = float(parList[3])
    P         = float(parList[4])
    I         = float(parList[5])
    D         = float(parList[6]) 
    # update status manager  
    statusMgr.updateSetPoint(setpoint)
    statusMgr.updatePID(P,I,D)
    if daqStatus==1: 
        statusMgr.isActive  = True
    else: 
        statusMgr.isActive  = False 
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
    # update PID loop  
    pidLoop.setKp(statusMgr.currentP) 
    pidLoop.setKi(statusMgr.currentI) 
    pidLoop.setKd(statusMgr.currentD) 
    pidLoop.SetPoint = statusMgr.currentSetPoint 

    def enableDAQ(statusMgr,yoko):
        if statusMgr.isSimMode==False:
            yoko.open_vxi_connection(statusMgr.ipAddr)
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
                statusMgr.isConnected = True

    def disableDAQ(statusMgr,yoko):
        if statusMgr.isSimMode==False:
            if statusMgr.isConnected==True:
                # set the yokogawa level to zero 
                yoko.set_level(0.)
                # disable the output 
                yoko.disable_output()
                # close the connection  
                yoko.close_vxi_connection()
                statusMgr.isConnected = False

    def get_data(pidLoop):
        # this is where we would get some value from the fixed probes
        # for now, use a random number generator  
        val = get_random(gLOWER_LIMIT,gUPPER_LIMIT)
        pidLoop.update(val)       # how does the fixed probe readout compare to the setpoint?    
        return pidLoop.output

    # generate the data 
    def readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko):
        global gPrevLvl,gReadoutDelay,gLOWER_LIMIT,gUPPER_LIMIT 
        dataFN     = "ps-feedback"
        yoko_event = YokogawaEvent() 
        x = now_timestamp()
        if statusMgr.manualMode==1:
           y = statusMgr.currentSetPoint
        else:
           y = get_data(pidLoop)
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
yoko      = yokogawa()

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

# get all the parameters 
getParameters(statusMgr,runMgr,fileMgr,pidLoop) 

if statusMgr.isSimMode==False:
    enableDAQ(statusMgr,yoko)  

# start a timer 
t_start = timer()
t_prev  = t_start 
 
# now start an infinite loop
while(1):
    # update the parameters 
    getParameters(statusMgr,runMgr,fileMgr,pidLoop) 
    # check DAQ status 
    # Did we get a kill signal? 
    if statusMgr.killDAQ==True: 
        disableDAQ(statusMgr,yoko)
        break  
    if statusMgr.isActive==True:
        # DAQ is active; are we connected?  
        if statusMgr.isConnected==False: 
            enableDAQ(statusMgr,yoko)     
        if statusMgr.isConnected==True: 
            # we're connected, check elapsed time 
            t_current = timer()
            dt = t_current - t_prev 
            if dt>=gRunTime: 
               # run is finished, change run numbers
               runMgr.updateRunNumber() 
            # read out the event 
            readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko)
    else:
        # disable the DAQ 
        disableDAQ(statusMgr,yoko)
    # setup for next iteration  
    t_prev = t_current  
        
# stop the timer 
t_stop = timer() 
dt     = t_stop - t_start
print("[PSFeedback]: Elapsed time: {0:.4f}".format(dt))
print("[PSFeedback]: System disabled and no longer taking data.")


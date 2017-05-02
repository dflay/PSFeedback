#! /usr/bin/python 
# Power supply feedback software 
# - Relies on parameters in the ./input/parameters.csv file to do certain actions 
# - Will run indefinitely until a kill signal is sent via the psfb_set_pars program     

# FIXME:
# 1. Finish ROOT file output implementation 
# 2. How to integrate the fixed probe input? 
# 3. Get code to start a new data file when re-starting data taking (when toggling status switch) 
#    - Do we really care about this? 

import time 
from instrument      import yokogawa 
from timeit          import default_timer as timer
from data_structures import * 
from util            import *
from pid             import PID 

# global variables 
gLOWER_LIMIT     = -200           # in mA 
gUPPER_LIMIT     =  200           # in mA 
gPrevLvl         = 0              # in mA 
gPrevTime        = 0              # in seconds  
gReadoutDelay    = 0.5            # in seconds 
gRunTime         = 60.*1          # in seconds 
gCONV_mA_TO_AMPS = 1E-3           # 1 mA = 10^-3 A  
gEventNumber     = 0 
gDataFN          = "ps-feedback"  # output file name
ip_addr          = "192.168.5.160" 
gDataDIR         = './data'
gFileEXT         = 'csv'
gIsDebug         = True
gWriteROOT       = True           # write ROOT file   

#_______________________________________________________________________________
def getParameters(statusMgr,runMgr,fileMgr,pidLoop):
    global gIsDebug 
    # read from parameter file 
    parList   = fileMgr.readParameters()
    if gIsDebug==True: print("[getParameters]: Obtained %d parameters" %( len(parList) ) ) 
    killDAQ   = int(parList[0])  # 0 = alive,    1 = kill 
    daqStatus = int(parList[1])  # 0 = inactive, 1 = active  
    simMode   = int(parList[2])
    manMode   = int(parList[3])  # 0 = manual,   1 = auto  
    setpoint  = float(parList[4])
    P         = float(parList[5])
    I         = float(parList[6])
    D         = float(parList[7]) 
    # update status manager  
    statusMgr.updateSetPoint(setpoint)
    statusMgr.updatePID(P,I,D)
    if daqStatus==1: 
        statusMgr.isActive  = True
    else: 
        statusMgr.isActive  = False 
    if simMode==1: 
        statusMgr.isSimMode = True
    else:  
        statusMgr.isSimMode = False
    if manMode==0:
        statusMgr.manualMode = True  
        statusMgr.autoMode   = False 
    else:  
        statusMgr.manualMode = False  
        statusMgr.autoMode   = True
    if killDAQ==1: 
        statusMgr.killDAQ    = True 
    else: 
        statusMgr.killDAQ    = False 
    # update PID loop  
    pidLoop.setKp(statusMgr.currentP) 
    pidLoop.setKi(statusMgr.currentI) 
    pidLoop.setKd(statusMgr.currentD) 
    pidLoop.SetPoint = statusMgr.currentSetPoint 
    if gIsDebug==True: print("[getParameters]: Parameters read from file")

def checkRunTime(runMgr):
    global gRunTime,gPrevTime,gEventNumber 
    rc = 0 # 0 = not ready, 1 = ready 
    current_time = timer()  
    dt = current_time - gPrevTime 
    if dt>=gRunTime: 
        if gIsDebug==True: print("[checkRunTime]: RUN %d FINISHED!  t_current = %.4E, t_prev = %.4E, diff = %.4E, run_max = %.4E" \
                           %(runMgr.runNum,current_time,gPrevTime,dt,gRunTime) )
        # clear event number 
        gEventNumber = 0 
        if gIsDebug==True: print("[checkRunTime]: Starting run %d" %(runMgr.runNum+1) )
        gPrevTime = current_time  
        rc = 1
    return rc  

def enableDAQ(statusMgr,runMgr,yoko):
    if statusMgr.isSimMode==False:
        rc = yoko.open_vxi_connection(statusMgr.ipAddr)
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
    runMgr.updateRunNumber()  # update the run number 
    if gIsDebug==True: print("[enableDAQ]: DAQ enabled")

def disableDAQ(statusMgr,yoko):
    global gIsDebug
    if statusMgr.isSimMode==False:
        if statusMgr.isConnected==True:
            # set the yokogawa level to zero, disable, and disconnect 
            yoko.set_level(0.)
            yoko.disable_output()
            yoko.close_vxi_connection()
            statusMgr.isConnected = False
    if gIsDebug==True: print("[disableDAQ]: DAQ disabled")

def get_data(pidLoop):
    global gIsDebug,gLOWER_LIMIT,gUPPER_LIMIT 
    if gIsDebug==True: print("[get_data]: getting data...")
    # this is where we would get some value from the fixed probes
    # for now, use a random number generator  
    val = get_random(gLOWER_LIMIT,gUPPER_LIMIT)
    pidLoop.update(val)       # how does the fixed probe readout compare to the setpoint?    
    if gIsDebug==True: print("[enableDAQ]: done!")
    return pidLoop.output

# generate the data 
def readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko):
    global gIsDebug,gEventNumber,gPrevLvl,gReadoutDelay,gLOWER_LIMIT,gUPPER_LIMIT,gWriteROOT,gDataFN,gCONV_mA_TO_AMPS 
    if gIsDebug==True: print("[readEvent]: Reading event...")
    gEventNumber = gEventNumber + 1
    yoko_event = YokogawaEvent() 
    x = now_timestamp_2()
    if statusMgr.manualMode==1:
       y = statusMgr.currentSetPoint
    else:
       y = get_data(pidLoop)
    # check the level 
    if y>gLOWER_LIMIT and y<gUPPER_LIMIT:
       # looks good, do nothing 
       y = y
    else:
       if y>0: y = 0.8*gUPPER_LIMIT
       if y<0: y = 0.8*gLOWER_LIMIT
    # now program the yokogawa 
    if statusMgr.isSimMode==False:
        if gPrevLvl!=y:                          # check to see if the yokogawa level changed 
            yoko.set_level(y)                    # FIXME: relatively certain that we set the current in mA  
        # wait a bit 
        time.sleep(gReadoutDelay)
        my_lvl   = float( yoko.get_level() )
        lvl      = my_lvl/gCONV_mA_TO_AMPS   # the readout is in Amps; convert to mA   
    else:
        # test mode; use the random data  
        time.sleep(gReadoutDelay)
        lvl = y
    # save the data to the event object
    yoko_event.ID             = gEventNumber 
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
    if gIsDebug==True: print("[readEvent]: Event number = %d, current = %.4f" %(yoko_event.ID,yoko_event.current) ) 
    rc = fileMgr.writeYokogawaEvent(gWriteROOT,runMgr.runNum,gDataFN,yoko_event)
    if rc==1:
        print("System: Cannot write data to file for run %d" %(runMgr.runNum) )
    # save the level as the previous one 
    gPrevLvl = lvl
    if gIsDebug==True: print("[readEvent]: Done!")
#_______________________________________________________________________________

fileMgr   = FileManager()
statusMgr = StatusManager()
runMgr    = RunManager()
pidLoop   = PID() 
yoko      = yokogawa()

# initialization
fileMgr.fileEXT = gFileEXT  
fileMgr.dataDir = gDataDIR 
runMgr.dataDir  = gDataDIR
runMgr.tag      = "%s_run-" %(gDataFN)
pidLoop         = PID()
pidLoop.setKp(0.6)
pidLoop.setKi(0.8)
pidLoop.setKd(0.)
pidLoop.setSampleTime(0.01)

# get all the parameters 
getParameters(statusMgr,runMgr,fileMgr,pidLoop) 
statusMgr.ipAddr = ip_addr

enableDAQ(statusMgr,runMgr,yoko)  

# start a timer 
t_start = timer()
 
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
        if statusMgr.isConnected==False and statusMgr.isSimMode==False: 
            enableDAQ(statusMgr,runMgr,yoko)     
        if statusMgr.isConnected==True: 
            # we're connected, check elapsed time 
            rc = checkRunTime(runMgr) 
            if rc==1: runMgr.updateRunNumber() 
            # read out the event 
            readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko)
        # if in simulation mode, readout an event anyway 
        if statusMgr.isSimMode==True: 
            # we're connected, check elapsed time 
            rc = checkRunTime(runMgr) 
            if rc==1: runMgr.updateRunNumber() 
            # read out the event 
            readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko)
    else:
        # disable the DAQ 
        disableDAQ(statusMgr,yoko)
    time.sleep(0.002)  # need a buffer time so the code can catch up (when reading in the pars at the top of the loop) 
        
# stop the timer 
t_stop = timer() 
dt     = t_stop - t_start
print("[PSFeedback]: Elapsed time: {0:.4f} sec".format(dt))
print("[PSFeedback]: System disabled and no longer taking data.")


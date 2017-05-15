#! /usr/bin/python 
# Power supply feedback software 
# - Relies on parameters in the ./input/parameters.csv file to do certain actions 
# - Will run indefinitely until a kill signal is sent via the psfb_set_pars program     

# FIXME:
# 1. How to integrate the fixed probe input? 

import time
import global_var
from util            import *
from instrument      import yokogawa 
from timeit          import default_timer as timer
from data_structures import * 
from pid             import PID 

#_______________________________________________________________________________
def getParameters(statusMgr,runMgr,fileMgr,pidLoop,fpEvent):
    # read from parameter file 
    parList      = fileMgr.readParameters()
    if global_var.IS_DEBUG==True: print("[getParameters]: Obtained %d parameters" %( len(parList) ) ) 
    killDAQ      = int(parList[0])  # 0 = alive,    1 = kill 
    daqStatus    = int(parList[1])  # 0 = inactive, 1 = active  
    simMode      = int(parList[2])
    manMode      = int(parList[3])  # 0 = manual,   1 = auto  
    setpoint     = float(parList[4])
    P            = float(parList[5])
    I            = float(parList[6])
    D            = float(parList[7]) 
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
    pidLoop.updatePID(statusMgr.currentP,statusMgr.currentI,statusMgr.currentD)
    pidLoop.updateSetPoint(statusMgr.currentSetPoint)
    # read in fixed probe data 
    fpList       = fileMgr.readFPData()
    fieldAvg_Hz  = float(fpList[0])   
    fieldAvg_ppm = float(fpList[1])  
    fieldSig_Hz  = float(fpList[2])   
    fieldSig_ppm = float(fpList[3])  
    # update the fixed probe event 
    fpEvent.updateAverage(fieldAvg_Hz,fieldAvg_ppm)  
    fpEvent.updateSigma(fieldSig_Hz,fieldSig_ppm)  
    if global_var.IS_DEBUG==True: print("[getParameters]: Parameters read from file")

def checkRunTime(runMgr):
    # global global_var.PREV_TIME,global_var.EVENT_NUMBER # only need the variables we want to change 
    rc = 0 # 0 = not ready, 1 = ready 
    current_time = timer()  
    dt = current_time - global_var.PREV_TIME 
    if dt>=global_var.RUN_TIME: 
        if global_var.IS_DEBUG==True: 
            print("[checkRunTime]: RUN %d FINISHED!  t_current = %.4E, t_prev = %.4E, diff = %.4E, run_max = %.4E" \
                           %(runMgr.runNum,current_time,global_var.PREV_TIME,dt,global_var.RUN_TIME) )
        # clear event number 
        global_var.EVENT_NUMBER = 0 
        if global_var.IS_DEBUG==True: print("[checkRunTime]: Starting run %d" %(runMgr.runNum+1) )
        global_var.PREV_TIME = current_time  
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
    if global_var.IS_DEBUG==True: print("[enableDAQ]: DAQ enabled")

def disableDAQ(statusMgr,yoko):
    if statusMgr.isSimMode==False:
        if statusMgr.isConnected==True:
            # set the yokogawa level to zero, disable, and disconnect 
            yoko.set_level(0.)
            yoko.disable_output()
            yoko.close_vxi_connection()
            statusMgr.isConnected = False
    if global_var.IS_DEBUG==True: print("[disableDAQ]: DAQ disabled")

def get_data(pidLoop,statusMgr,fpEvent):
    if global_var.IS_DEBUG==True: print("[get_data]: getting data...")
    # tMIN, tMAX for simulation mode 
    tMIN = 40E+3 # in Hz 
    tMAX = 60E+3 # in Hz 
    if statusMgr.isSimMode==True: 
       val = get_random(tMIN,tMAX)
    else: 
       val = fpEvent.field_avg_Hz 
    # how does the fixed probe readout compare to the setpoint?
    output = pidLoop.update(val)           
    if global_var.IS_DEBUG==True: print("[enableDAQ]: done!")
    return output

# generate the data 
def readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko,fpEvent):
    # global global_var.EVENT_NUMBER,global_var.PREV_LVL
    if global_var.IS_DEBUG==True: print("[readEvent]: Reading event...")
    global_var.EVENT_NUMBER = global_var.EVENT_NUMBER + 1
    yoko_event = YokogawaEvent() 
    x = now_timestamp()
    if statusMgr.manualMode==1:
       y = statusMgr.currentSetPoint
       y = y*global_var.CONV_Hz_TO_AMPS/1E-3 # need to convert to mA  
    else:
       y = get_data(pidLoop,statusMgr,fpEvent)/1E-3    # comes out in Amps, convert to mA 
    # check the level 
    if y>global_var.LOWER_LIMIT and y<global_var.UPPER_LIMIT:
       # looks good, do nothing 
       y = y
    else:
       if y>0: y = 0.8*global_var.UPPER_LIMIT
       if y<0: y = 0.8*global_var.LOWER_LIMIT
    # now program the yokogawa 
    if statusMgr.isSimMode==False:
        if global_var.PREV_LVL!=y:               # check to see if the yokogawa level changed 
            yoko.set_level(y)                    # FIXME: relatively certain that we set the current in mA  
        # wait a bit 
        time.sleep(global_var.READOUT_DELAY)
        my_lvl   = float( yoko.get_level() )
        lvl      = my_lvl/1E-3                    # the readout is in Amps; convert to mA   
    else:
        # test mode; use the random data  
        time.sleep(global_var.READOUT_DELAY)
        lvl = y
    # save the data to the event object
    yoko_event.ID             = global_var.EVENT_NUMBER 
    yoko_event.timestamp      = x
    yoko_event.current        = lvl
    yoko_event.setpoint       = statusMgr.currentSetPoint
    yoko_event.is_manual      = statusMgr.manualMode
    if statusMgr.isSimMode==False:
        yoko_event.output_enabled = int( yoko.get_output_state() )
    else:
        yoko_event.output_enabled = 0
    yoko_event.p_fdbk = pidLoop.Kp
    yoko_event.i_fdbk = pidLoop.Ki
    yoko_event.d_fdbk = pidLoop.Kd
    # now write to file 
    if global_var.IS_DEBUG==True: print("[readEvent]: Event number = %d, current = %.4f mA" %(yoko_event.ID,yoko_event.current) ) 
    rc = fileMgr.writeYokogawaEvent(global_var.WRITE_ROOT,runMgr.runNum,global_var.DATA_FN,yoko_event)
    if rc==1:
        print("System: Cannot write data to file for run %d" %(runMgr.runNum) )
    # save the level as the previous one 
    global_var.PREV_LVL = lvl
    if global_var.IS_DEBUG==True: print("[readEvent]: Done!")
#_______________________________________________________________________________

fileMgr    = FileManager()
statusMgr  = StatusManager()
runMgr     = RunManager()
pidLoop    = PID() 
fpEvent    = FixedProbeEvent() 
yoko       = yokogawa()

# initialization
fileMgr.fileEXT = global_var.FILE_EXT  
fileMgr.dataDir = global_var.DATA_DIR 
runMgr.dataDir  = global_var.DATA_DIR
runMgr.tag      = "%s_run-" %(global_var.DATA_FN)
pidLoop         = PID()
pidLoop.updatePID(1.0,0.0,0.0) 
pidLoop.setSampleTime(0.01)
pidLoop.setScaleFactor(global_var.CONV_Hz_TO_AMPS) 

# get all the parameters 
getParameters(statusMgr,runMgr,fileMgr,pidLoop,fpEvent) 
statusMgr.ipAddr = global_var.IP_ADDR

enableDAQ(statusMgr,runMgr,yoko)  

# start a timer 
t_start = timer()
 
# now start an infinite loop
while(1):
    # update the parameters 
    getParameters(statusMgr,runMgr,fileMgr,pidLoop,fpEvent) 
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
            readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko,fpEvent)
        # if in simulation mode, readout an event anyway 
        if statusMgr.isSimMode==True: 
            # we're connected, check elapsed time 
            rc = checkRunTime(runMgr) 
            if rc==1: runMgr.updateRunNumber() 
            # read out the event 
            readEvent(statusMgr,runMgr,fileMgr,pidLoop,yoko,fpEvent)
    else:
        # disable the DAQ 
        disableDAQ(statusMgr,yoko)
    time.sleep(0.002)  # need a buffer time so the code can catch up (when reading in the pars at the top of the loop) 
        
# stop the timer 
t_stop = timer() 
dt     = t_stop - t_start
print("[PSFeedback]: Elapsed time: {0:.4f} sec".format(dt))
print("[PSFeedback]: System disabled and no longer taking data.")


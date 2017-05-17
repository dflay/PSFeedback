#! /usr/bin/python 
# use command-line flags to 
# set the PID and setpoint variables to be applied to the Yokogawa

import os
import argparse
from data_structures import FileManager 

IsDebug         = False
writeFPFile     = False  
CONV_Hz_TO_ppm  = 61.79 # Hz/ppm 

# file manager object 
fileMgr         = FileManager()
fileMgr.fileEXT = "csv" 

# first get existing parameters 
parList  = [] 
parList  = fileMgr.readParameters() 

killStatus = int(parList[0])  # 0 = alive,    1 = kill 
daqStatus  = int(parList[1])  # 0 = inactive, 1 = active  
simMode    = int(parList[2])
mode       = int(parList[3])
setpoint   = float(parList[4])
P          = float(parList[5])
I          = float(parList[6])
D          = float(parList[7])

print("OLD VALUES:") 
print("P = %.3f, I = %.3f, D = %.3f, setpoint = %.3f, simMode = %d, mode = %d, daqStatus = %d, killStatus = %d" \
          %(P,I,D,setpoint,simMode,mode,daqStatus,killStatus) )

fpList    = [] 
fpList    = fileMgr.readFPData()
fpAvg     = float(fpList[0]) 
fpAvgPPM  = float(fpList[1]) 
fpSig     = float(fpList[2]) 
fpSigPPM  = float(fpList[3]) 

parser = argparse.ArgumentParser(description='PS Feedback Parameters') 
# declare arguments 
parser.add_argument('--p'          ,action='store',dest='p'         ,default=P)
parser.add_argument('--i'          ,action='store',dest='i'         ,default=I)
parser.add_argument('--d'          ,action='store',dest='d'         ,default=D)
parser.add_argument('--setpoint'   ,action='store',dest='setpoint'  ,default=setpoint)
parser.add_argument('--status'     ,action='store',dest='status'    ,default=daqStatus) # active (1), disabled (0)  
parser.add_argument('--kill'       ,action='store_true')                                # kill program 
parser.add_argument('--start'      ,action='store_true')                                # enable starting the system    
parser.add_argument('--debug'      ,action='store_true')                                # debug mode
parser.add_argument('--sim'        ,action='store',dest='sim'       ,default=simMode)        # simulation mode; 0 = false, 1 = true 
parser.add_argument('--manual_mode',action='store_true')                                # manual mode 
parser.add_argument('--auto_mode'  ,action='store_true')                                # auto mode (used fixed probe data) 
parser.add_argument('--fp_avg'     ,action='store',dest='fp_avg'    ,default=fpAvg)     # fixed probe average field value (Hz)  
parser.add_argument('--fp_avg_ppm' ,action='store',dest='fp_avg_ppm',default=fpAvgPPM)  # fixed probe average field value (ppm)  
# parse command-line arguments
args = parser.parse_args()

# now let's see if any of the parameters were changed via the command line 

# update values if necessary
if args.kill is None: 
    killStatus = 0 
else: 
    killStatus = int(args.kill) 
    iStart     = 0 

startDAQ = bool(args.start) 

if args.status is not None: 
    daqStatus = int(args.status)  

if args.sim is not None: 
    simMode = int(args.sim)  

isManualModeTouched = bool(args.manual_mode) 
isAutoModeTouched   = bool(args.auto_mode) 

if isManualModeTouched: 
    mode = 0 

if isAutoModeTouched: 
    mode = 1

if args.p is not None: 
    P = float(args.p)
 
if args.i is not None: 
    I = float(args.i)

if args.d is not None: 
    D = float(args.d)  

if args.setpoint is not None: 
    setpoint = float(args.setpoint)  

# use only one flag, not both (that won't make sense!) 
if args.fp_avg is not None: 
    fpAvg    = float(args.fp_avg) 
    fpAvgPPM = (fpAvg-setpoint)/CONV_Hz_TO_ppm 
    writeFPFile = True  

if args.fp_avg_ppm is not None:
    fpAvgPPM = float(args.fp_avg_ppm) 
    fpAvg    = fpAvgPPM*CONV_Hz_TO_ppm + setpoint
    writeFPFile = True  

IsDebug = bool(args.debug)   
if IsDebug==True: 
    print("NEW VALUES:") 
    print("P = %.3f, I = %.3f, D = %.3f, setpoint = %.3f, simMode = %d, mode = %d, daqStatus = %d, killStatus = %d, start = %d" \
          %(P,I,D,setpoint,simMode,mode,daqStatus,killStatus,startDAQ) )

fileMgr.writeParameters(killStatus,daqStatus,simMode,mode,setpoint,P,I,D) 
 
if writeFPFile==True: 
    fileMgr.writeFPData(fpAvg,fpAvgPPM,fpSig,fpSigPPM)

# if the start flag was used, start the program 
task = "python psfb.py"
cmd  = "screen -S ps-fdbk -d -m %s" %(task) 
if startDAQ: 
   os.system(cmd) 


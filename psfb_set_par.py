#! /usr/bin/python 
# use command-line flags to 
# set the PID and setpoint variables to be applied to the Yokogawa

import os
import argparse
from data_structures import YokogawaEvent, FileManager 

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

fpList    = [] 
fpList    = fileMgr.readFPData()
fpTgt     = float(fpList[0])     # should be in Hz  
fpAvg     = float(fpList[1]) 
fpAvgPPM  = float(fpList[2]) 

parser = argparse.ArgumentParser(description='PS Feedback Parameters') 
# declare arguments 
parser.add_argument('--p'         ,action='store',dest='p'         ,default=-1)
parser.add_argument('--i'         ,action='store',dest='i'         ,default=-1)
parser.add_argument('--d'         ,action='store',dest='d'         ,default=-1)
parser.add_argument('--setpoint'  ,action='store',dest='setpoint'  ,default=-300)
parser.add_argument('--status'    ,action='store',dest='status'    ,default=-1)  # active (1), disabled (0)  
parser.add_argument('--kill'      ,action='store',dest='kill'      ,default=-1)  # kill (1)  , do nothing (0)   
parser.add_argument('--debug'     ,action='store',dest='debug'     ,default=-1)  # debug mode
parser.add_argument('--sim'       ,action='store',dest='sim'       ,default=-1)  # simulation mode; 0 = false, 1 = true 
parser.add_argument('--mode'      ,action='store',dest='mode'      ,default=-1)  # mode: 0 = manual, 1 = auto 
parser.add_argument('--fp_avg'    ,action='store',dest='fp_avg'    ,default=-1)  # fixed probe average field value (Hz)  
parser.add_argument('--fp_avg_ppm',action='store',dest='fp_avg_ppm',default=-1)  # fixed probe average field value (ppm)  
# parse command-line arguments
args = parser.parse_args()

# now let's see if any of the parameters were changed via the command line 
iP         = float(args.p)
iI         = float(args.i)
iD         = float(args.d)
iSetpoint  = float(args.setpoint)
iFPAvg     = float(args.fp_avg) 
iFPAvgPPM  = float(args.fp_avg_ppm) 
iSimMode   = int(args.sim) 
iMode      = int(args.mode) 
iDAQStatus = int(args.status)
iKill      = int(args.kill)
# update values if necessary
if iKill>=0:     killStatus  = iKill      
if iDAQStatus>0: daqStatus   = iDAQStatus
if iSimMode>0:   simMode     = iSimMode
if iMode>=0:     mode        = iMode
if iP>=0:        P           = iP 
if iI>=0:        I           = iI 
if iD>=0:        D           = iD 
if iSetpoint!=-300: setpoint = iSetpoint
# use only one flag, not both (that won't make sense!) 
if iFPAvg>=0 and iFPAvgPPM<0: 
    fpAvg    = iFPAvg 
    fpAvgPPM = (iFPAvg-iFPTgt)/CONV_Hz_TO_ppm  # convert to ppm   
    writeFPFile = True  
if iFPAvg<0 and iFPAvgPPM>=0:
    fpAvgPPM = iFPAvgPPM 
    fpAvg    = iFPAvgPPM*CONV_Hz_TO_ppm + iFPTgt 
    writeFPFile = True  
 
if IsDebug==True: 
    print("P = %.3f, I = %.3f, D = %.3f, setpoint = %.3f, simMode = %d, daqStatus = %d " \
          %(P,I,D,setpoint,simMode,mode,daqStatus) )

fileMgr.writeParameters(killStatus,daqStatus,simMode,mode,setpoint,P,I,D) 

if writeFPFile==True: 
    fileMgr.writeFPData(fpAvg,fpAvgPPM)



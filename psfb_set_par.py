#! /usr/bin/python 
# use command-line flags to 
# set the PID and setpoint variables to be applied to the Yokogawa

import os
import argparse
from data_structures import YokogawaEvent, FileManager 

IsDebug = False

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

parser = argparse.ArgumentParser(description='PS Feedback Parameters') 
# declare arguments 
parser.add_argument('--p'         ,action='store',dest='p'       ,default=-1)
parser.add_argument('--i'         ,action='store',dest='i'       ,default=-1)
parser.add_argument('--d'         ,action='store',dest='d'       ,default=-1)
parser.add_argument('--setpoint'  ,action='store',dest='setpoint',default=-300)
parser.add_argument('--status'    ,action='store',dest='status'  ,default=-1)  # active (1), disabled (0)  
parser.add_argument('--kill'      ,action='store',dest='kill'    ,default=-1)  # kill (1)  , do nothing (0)   
parser.add_argument('--debug'     ,action='store',dest='debug'   ,default=-1)  # debug mode
parser.add_argument('--sim'       ,action='store',dest='sim'     ,default=-1)  # simulation mode
parser.add_argument('--mode'      ,action='store',dest='mode'    ,default=-1)  # mode: 0 = manual, 1 = auto 
# parse command-line arguments
args = parser.parse_args()

# now let's see if any of the parameters were changed via the command line 
iP         = float(args.p)
iI         = float(args.i)
iD         = float(args.d)
iSetpoint  = float(args.setpoint)
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
 
if IsDebug==True: 
    print("P = %.3f, I = %.3f, D = %.3f, setpoint = %.3f, simMode = %d, daqStatus = %d " \
          %(P,I,D,setpoint,simMode,mode,daqStatus) )

fileMgr.writeParameters(killStatus,daqStatus,simMode,manMode,setpoint,P,I,D) 


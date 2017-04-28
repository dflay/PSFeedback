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
parList = fileMgr.readParameters() 

runStatus = int(parList[0])
simMode   = int(parList[1]) 
setpoint  = float(parList[2])
P         = float(parList[3]) 
I         = float(parList[4]) 
D         = float(parList[5]) 

parser = argparse.ArgumentParser(description='PS Feedback Parameters') 
# declare arguments 
parser.add_argument('--p'         ,action='store',dest='p'         ,default=-1)
parser.add_argument('--i'         ,action='store',dest='i'         ,default=-1)
parser.add_argument('--d'         ,action='store',dest='d'         ,default=-1)
parser.add_argument('--setpoint'  ,action='store',dest='setpoint'  ,default=-1)
parser.add_argument('--run_status',action='store',dest='run_status',default=-1)  # active (1), disabled (0)  
parser.add_argument('--debug'     ,action='store',dest='debug'     ,default=-1)  # debug mode
parser.add_argument('--sim'       ,action='store',dest='sim'       ,default=-1)  # simulation mode
# parse command-line arguments
args = parser.parse_args()

# now let's see if any of the parameters were changed via the command line 
iP         = float(args.p)
iI         = float(args.i)
iD         = float(args.d)
iSetpoint  = float(args.setpoint)
iSimMode   = int(args.sim) 
iRunStatus = int(args.run_status)
# update values if necessary
if iRunStatus>0: runStatus = iRunStatus
if iSimMode>0:   simMode   = iSimMode
if iP>0:         P         = iP 
if iI>0:         I         = iI 
if iD>0:         I         = iD 
if iSetpoint>0:  setpoint  = iSetpoint 
 
if IsDebug==True: 
    print("P = %.3f, I = %.3f, D = %.3f, setpoint = %.3f, simMode = %d, runStatus = %d " \
          %(P,I,D,setpoint,simMode,runStatus) )

fileMgr.writeParameters(runStatus,simMode,setpoint,P,I,D) 


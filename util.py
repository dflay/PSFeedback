#! /usr/bin/python 
# miscellaneous functions for the Yokogawa operation 

import os.path 
import sys
import numpy as np
import datetime
import random
import pytz
import pyqtgraph as pg

UNIX_EPOCH_naive        = datetime.datetime(1970, 1, 1, 0, 0) # offset-naive datetime
UNIX_EPOCH_offset_aware = datetime.datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc) # offset-aware datetime
UNIX_EPOCH              = UNIX_EPOCH_naive
TS_MULT_us              = 1e6

#_______________________________________________________________________________
# Miscellaneous functions and classes 

def get_random(minVal,maxVal): 
    return random.randrange(minVal,maxVal)

def now_timestamp(ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    return(int((datetime.datetime.utcnow() - epoch).total_seconds()*ts_mult))

def int2dt(ts, ts_mult=TS_MULT_us):
    return(datetime.datetime.utcfromtimestamp(float(ts)/ts_mult))

def dt2int(dt, ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    delta = dt - epoch
    return(int(delta.total_seconds()*ts_mult))

def td2int(td, ts_mult=TS_MULT_us):
    return(int(td.total_seconds()*ts_mult))

def int2td(ts, ts_mult=TS_MULT_us):
    return(datetime.timedelta(seconds=float(ts)/ts_mult))

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        # return [QTime().addMSecs(value).toString('mm:ss') for value in values]
        # return [int2dt(value).strftime("%H:%M:%S.%f") for value in values]
        return [int2dt(value).strftime("%H:%M:%S") for value in values]
#_______________________________________________________________________________
# a class to keep track of the yokogawa data for a given readout event 
class YokogawaEvent: 
    def __init__(self): 
        self.clear()  

    def clear(self): 
        self.timestamp      = 0 
        self.is_manual      = 0 
        self.output_enabled = 0 
        self.current        = 0 
        self.p_fdbk         = 0 
        self.i_fdbk         = 0 
        self.d_fdbk         = 0 
        self.setpoint       = 0 

#_______________________________________________________________________________
# a class to keep track of the run number, and its start and stop times 
class RunManager: 
    def __init__(self):
        self.runNum    = 0  
        self.startTime = 0 # UTC  
        self.endTime   = 0 # UTC 
        self.dataDir   = ""
        self.isRunning = False 
        self.isDebug   = False

    def updateRunNumber(self): 
        self.runNum = self.getRunNumber()

    def getRunNumber(self):
        dirs = [d for d in os.listdir(self.dataDir) if os.path.isdir( os.path.join(self.dataDir,d) ) ] 
        N = len(dirs) 
        runList = []
        lastRun = -300 
        if N>0:  
            for entry in dirs: 
                arg = int(entry.strip('run-') )
                if arg>=lastRun: lastRun = arg
        else: 
            lastRun = 0 
        nextRun = lastRun + 1
        if self.isDebug==True: print("Number of runs: %d, next run: %d" %(N,nextRun) )  
        return nextRun
#_______________________________________________________________________________
# a class that keeps track of miscellaneous important quantities 
# that are not necessarily related to a run  
class StatusManager: 
    def __init__(self): 
        self.isConnected      = False 
        self.isDebug          = False 
        self.manualMode       = 0 
        self.autoMode         = 0
        self.ipAddr           = "" 
        self.currentSetPoint  = 0 
        self.isSimMode        = False 
        # for a history of setpoint changes 
        self.tsList           = [] 
        self.spList           = []
        # PID values 
        self.currentP         = 0 
        self.currentI         = 0 
        self.currentD         = 0 
        # history of changes 
        self.tPIDList         = []
        self.pList            = [] 
        self.iList            = [] 
        self.dList            = [] 

    def updateSetPoint(self,val): 
        self.tsList.append( now_timestamp() )
        self.spList.append(val) 
        self.currentSetPoint = val  

    def updatePID(self,P,I,D): 
        self.tPIDList.append( now_timestamp() ) 
        self.pList.append(P) 
        self.iList.append(I) 
        self.dList.append(D)
        self.currentP = P  
        self.currentI = I  
        self.currentD = D  

    def clearSetPointHistory(self):
         # clear the array 
         del self.tsList[:] 
         del self.spList[:]

    def clearPIDHistory(self):
         # clear arrays
         del self.tPIDList[:] 
         del self.pList[:]
         del self.iList[:]
         del self.dList[:]

#_______________________________________________________________________________
# a class that handles all file I/O 
class FileManager: 
    def __init__(self): 
        self.dataDir = ""
        self.isDebug = False
        self.fileEXT = "dat"
      
    def appendToFile(self,runNum,fn,utc_time,val):
        rc = 0 
        theDir = self.getRunPath(runNum) 
        outpath = '%s/%s.%s' %(theDir,fn,self.fileEXT)
        # check if the directory exists before writing to file 
        if (os.path.isdir(theDir)==True ): 
           myFile = open(outpath,'a')
           myFile.write("%d,%.6f\n" %(utc_time,val) )
           myFile.close()
        else:
           if self.isDebug==True: print("[FileManager]: Cannot access the directory %s. " %(theDir) ) 
           rc = 1 
        return rc 

    def writeSummaryFile(self,runNum,fn,msg):
        rc = 0 
        theDir = self.getRunPath(runNum) 
        outpath = '%s/%s.%s' %(theDir,fn,self.fileEXT)
        # check if the directory exists before writing to file 
        if (os.path.isdir(theDir)==True ): 
           myFile = open(outpath,'w')
           for entry in msg: 
               myFile.write("%s\n" %(entry) )
           myFile.close()
        else:
           if self.isDebug==True: print("[FileManager]: Cannot access the directory %s. " %(theDir) ) 
           rc = 1 
        return rc 

    def writeSetPointHistoryFile(self,runNum,fn,ts,sp):
        rc = 0 
        theDir = self.getRunPath(runNum) 
        outpath = '%s/%s.%s' %(theDir,fn,self.fileEXT)
        # check if the directory exists before writing to file 
        if (os.path.isdir(theDir)==True ): 
           myFile = open(outpath,'w')
           N = len(ts)
           if N==0: 
               # if no setpoints, write one line of zeros 
               myFile.write("%d,%.6lf\n" %(0,0) ) 
           else: 
               for i in range(0,N): 
                   myFile.write("%d,%.6lf\n" %(ts[i],sp[i]) )
           myFile.close()
        else:
           if self.isDebug==True: print("[FileManager]: Cannot access the directory %s. " %(theDir) ) 
           rc = 1 
        return rc 

    def writePIDHistoryFile(self,runNum,fn,tList,pList,iList,dList):
        rc = 0 
        theDir = self.getRunPath(runNum) 
        outpath = '%s/%s.%s' %(theDir,fn,self.fileEXT)
        # check if the directory exists before writing to file 
        if (os.path.isdir(theDir)==True ): 
           myFile = open(outpath,'w')
           N = len(tList)
           if N==0: 
               # if no setpoints, write one line of zeros 
               myFile.write("%d,%.6lf,%.6lf,%.6lf\n" %(0,0,0,0) ) 
           else: 
               for i in range(0,N): 
                   myFile.write("%d,%.6lf,%.6lf,%.6lf\n" %(tList[i],pList[i],iList[i],dList[i]) )
           myFile.close()
        else:
           if self.isDebug==True: print("[FileManager]: Cannot access the directory %s. " %(theDir) ) 
           rc = 1 
        return rc 

    def getRunPath(self,runNum): 
        thePath  = "%s/run-%05d" %(self.dataDir,runNum)
        return thePath 

    def makeDirectory(self,runNum): 
        theDir  = "%s/run-%05d" %(self.dataDir,runNum) 
        if not os.path.exists(theDir):
            os.makedirs(theDir)
#_______________________________________________________________________________



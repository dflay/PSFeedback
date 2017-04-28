import os.path
import sys
import csv
import ROOT 

#_______________________________________________________________________________
# a class to keep track of the yokogawa data for a given readout event 
class YokogawaEvent:
    def __init__(self):
        self.clear()

    def clear(self):
        self.ID             = 0
        self.timestamp      = 0
        self.is_manual      = 0
        self.output_enabled = 0
        self.current        = 0
        self.setpoint       = 0
        self.p_fdbk         = 0
        self.i_fdbk         = 0
        self.d_fdbk         = 0
#_______________________________________________________________________________
# a class to keep track of the run number, and its start and stop times 
class RunManager:
    def __init__(self):
        self.runNum    = 0
        self.startTime = 0 # UTC  
        self.endTime   = 0 # UTC 
        self.dataDir   = ""
        self.tag       = ""
        self.isRunning = False
        self.isDebug   = False

    def updateRunNumber(self):
        self.runNum = self.getRunNumber()

    def getRunNumber(self):
        # dirs  = [d for d in os.listdir(self.dataDir) if os.path.isdir( os.path.join(self.dataDir,d) ) ] 
        files = [f for f in os.listdir(self.dataDir) if os.path.isfile(os.path.join(self.dataDir,f) ) ]
        N = len(files)
        runList = []
        lastRun = -300
        if N>0:
            for entry in files:
                # path = '%s/%s' %(self.dataDir,entry) 
                fn   = os.path.splitext( os.path.basename(entry) )[0] # take the zeroth entry of the split function  
                # print(fn) 
                # arg = int(entry.strip('run-') )
                arg = int( fn.strip(self.tag) )
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
        self.isActive         = False 
        # PID values 
        self.currentP         = 0 
        self.currentI         = 0 
        self.currentD         = 0 

    def updateSetPoint(self,val):
        self.currentSetPoint = val

    def updatePID(self,P,I,D):
        self.currentP = P
        self.currentI = I
        self.currentD = D
#_______________________________________________________________________________
# a class that handles all file I/O 
class FileManager:
    def __init__(self):
        self.dataDir = ""
        self.isDebug = False
        self.fileEXT = "dat"

    def readFPData(self):
        theDir  = './input'
        inpath = '%s/fixed-probe-data.%s' %(theDir,self.fileEXT)
        myList  = [] 
        if (os.path.isdir(theDir)==True ):
            with open(inpath,'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    myList = row 
                f.close()
        else:
            print("[FileManager]: Cannot access the directory %s. " %(theDir) )
        return myList 

    def readParameters(self):
        theDir  = './input'
        inpath = '%s/parameters.%s' %(theDir,self.fileEXT)
        myList  = [] 
        if (os.path.isdir(theDir)==True ):
            with open(inpath,'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    myList = row 
                f.close()
        else:
            print("[FileManager]: Cannot access the directory %s. " %(theDir) )
        return myList 

    def writeFPData(self,field_avg,field_avg_ppm):
        theDir  = './input'
        outpath = '%s/fixed-probe-data.%s' %(theDir,self.fileEXT)
        if (os.path.isdir(theDir)==True ):
            myFile = open(outpath,'w')
            myFile.write( "%.3f,%.3f" %(field_avg,field_avg_ppm) )
            myFile.close()
            rc = 0
        else:
            print("[FileManager]: Cannot access the directory %s. " %(theDir) )
            rc = 1
        return rc

    def writeParameters(self,killStatus,daqStatus,simMode,manMode,setpoint,P,I,D):
        theDir  = './input'
        outpath = '%s/parameters.%s' %(theDir,self.fileEXT)
        if (os.path.isdir(theDir)==True ):
            myFile = open(outpath,'w')
            myFile.write( "%d,%d,%d,%d,%.3f,%.3f,%.3f,%.3f" %(killStatus,daqStatus,simMode,manMode,setpoint,P,I,D) )
            myFile.close()
            rc = 0
        else:
            print("[FileManager]: Cannot access the directory %s. " %(theDir) )
            rc = 1
        return rc

    def writeYokogawaEvent(self,writeROOT,runNum,tag,event):
        rc = self.writeCSV(runNum,tag,event)
        if writeROOT==True: 
            rc = self.writeROOTFile(runNum,tag,event) 
        return rc 

    def writeCSV(self,runNum,tag,event):
        rc = 0
        theDir  = './data'
        fn      = '%s_run-%05d.%s' %(tag,runNum,self.fileEXT)
        outpath = '%s/%s'      %(theDir,fn)
        # check if the directory exists before writing to file 
        if (os.path.isdir(theDir)==True ):
           myFile = open(outpath,'a')
           myFile.write("%d,%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f\n" %(event.timestamp,event.is_manual,event.output_enabled,\
                                                                event.current,event.setpoint,\
                                                                event.p_fdbk,event.i_fdbk,event.d_fdbk) )
           myFile.close()
        else:
           if self.isDebug==True: print("[FileManager]: Cannot access the directory %s. " %(theDir) )
           rc = 1
        return rc

    def writeROOTFile(self,runNum,tag,event):
        print("Writing ROOT file")


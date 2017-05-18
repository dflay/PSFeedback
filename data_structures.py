import os.path
import sys
import csv
from ROOT import gROOT, TTree, TFile, AddressOf 

# data structure for ROOT
# NOTE: We have to make all data members the same type for some odd reason... 
gROOT.ProcessLine(
"struct YokogawaEvent_t{\
   Double_t fID;\
   Double_t ftimestamp;\
   Double_t fis_manual;\
   Double_t foutput_enabled;\
   Double_t fcurrent;\
   Double_t fsetpoint;\
   Double_t fP;\
   Double_t fI;\
   Double_t fD;\
  };")

from ROOT import YokogawaEvent_t

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
# a class to keep track of the fixed probe info 
class FixedProbeEvent: 
    def __init__(self): 
        self.clear() 

    def updateAverage(self,avg_hz,avg_ppm): 
        self.field_avg_Hz  = avg_hz  
        self.field_avg_ppm = avg_ppm  

    def updateSigma(self,sig_hz,sig_ppm): 
        self.field_sig_Hz  = sig_hz  
        self.field_sig_ppm = sig_ppm  

    def clear(self):
        self.field_avg_Hz  = 0
        self.field_sig_Hz  = 0
        self.field_avg_ppm = 0
        self.field_sig_ppm = 0

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
        theDir = "%s/csv" %(self.dataDir)  # look at the CSV directory 
        files = [f for f in os.listdir(theDir) if os.path.isfile(os.path.join(theDir,f) ) ]
        N = len(files)
        runList = []
        lastRun = -300
        if N>0:
            for entry in files:
                fn   = os.path.splitext( os.path.basename(entry) )[0] # take the zeroth entry of the split function  
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
        isUpdated = False
        theDir    = './input'
        inpath    = '%s/fixed-probe-data.%s' %(theDir,self.fileEXT)
        lockfile  = '%s/fixed-probe-data.lock' %(theDir)
        myList    = [0,0,0,0] 
        if not os.path.isfile(lockfile):
            if (os.path.isdir(theDir)==True ):
                if os.path.isfile(inpath): 
                    isUpdated = True  
                    with open(inpath,'rb') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            myList = row 
                        f.close()
                else:  
                    print( "[FileManager]: File %s does not exist.  Returning zeroes." %(inpath) )
            else:
                print("[FileManager]: Cannot access the directory %s. " %(theDir) )
        return isUpdated,myList 

    def readParameters(self):
        theDir  = './input'
        inpath = '%s/parameters.%s' %(theDir,self.fileEXT)
        myList  = [] 
        if (os.path.isdir(theDir)==True ):
            if os.path.isfile(inpath): 
                with open(inpath,'rb') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        myList = row 
                    f.close()
            else: 
                print( "[FileManager]: File %s does not exist.  Returning default parameters." %(inpath) ) 
                myList = self.getDefaultParameters() 
        else:
            print("[FileManager]: Cannot access the directory %s. " %(theDir) )
        return myList 

    def getDefaultParameters(self):
        myList = [1,0,1,1,0,0,0,0] # kill program, DAQ disabled, simulation mode, manual mode, setpoint, P, I, D = 0  
        return myList

    def writeFPData(self,field_avg,field_avg_ppm,field_sig,field_sig_ppm):
        theDir  = './input'
        outpath = '%s/fixed-probe-data.%s' %(theDir,self.fileEXT)
        if (os.path.isdir(theDir)==True ):
            myFile = open(outpath,'w')
            myFile.write( "%.3f,%.3f,%.3f,%.3f" %(field_avg,field_avg_ppm,field_sig,field_sig_ppm) )
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
        theDir  = self.dataDir  
        fn      = '%s_run-%05d.%s' %(tag,runNum,self.fileEXT)
        outpath = '%s/csv/%s'      %(theDir,fn)
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
        myEvent                 = YokogawaEvent_t()
        myEvent.fID             = event.ID
        myEvent.ftimestamp      = event.timestamp     
        myEvent.fis_manual      = event.is_manual     
        myEvent.foutput_enabled = event.output_enabled
        myEvent.fcurrent        = event.current       
        myEvent.fsetpoint       = event.setpoint      
        myEvent.fP              = event.p_fdbk             
        myEvent.fI              = event.i_fdbk             
        myEvent.fD              = event.d_fdbk             

        fn            = '%s_run-%05d.root' %(tag,runNum)
        fileName      = "%s/ROOTfiles/%s"  %(self.dataDir,fn)
        treeName      = "T"
        branchName    = 'PSFB'
        leafStructure = 'ID/D:timestamp/D:is_manual/D:output_enabled/D:current/D:setpoint/D:P/D:I/D:D/D'

        if event.ID==1:
            # make a new file  
            myFile = TFile(fileName,"recreate")
            myTree = TTree(treeName,treeName)
            myTree.Branch(branchName,myEvent,leafStructure)
        elif event.ID>1:
            # appending to file   
            myFile = TFile(fileName,"update")
            myTree = gROOT.FindObject(treeName)
            myTree.SetBranchAddress(branchName,AddressOf(myEvent,"fID") )
        myTree.Fill()
        myFile.WriteTObject(myTree)  # this apparently removes the multiple basket issue 
        myFile.Close()


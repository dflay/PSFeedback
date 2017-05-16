// a script that shows plots of all relevant variables 

#include <iostream> 

#include "TDatime.h"
#include "TCanvas.h"
#include "TTree.h"
#include "TString.h"
#include "TH2F.h"

#include "./include/YokogawaEvent.h"
#include "./src/Graph.C"

bool gIsDebug      = false; 
bool gUseTimeStamp = true; 

void FillVector(TString axis,vector<YokogawaEvent_t> Event,vector<double> &v); 
TGraph *GetTGraph(TString xaxis,TString yaxis,vector<YokogawaEvent_t> Event);  
char *GetTimeStamp(int unix_time); 

void Plot(){

   int run=0;
   std::cout << "Enter run number: "; 
   std::cin  >> run; 
 
   TString TreeName   = Form("T"); 
   TString BranchName = Form("PSFB");
   TString prefix     = Form("./data/ROOTfiles/");
   TString path       = prefix + Form("ps-feedback_run-%05d.root",run);

   TFile *f          = new TFile(path);
   TTree *myTree     = (TTree *)f->Get(TreeName);  
   TBranch *myBranch = myTree->GetBranch(BranchName);

   TLeaf *timeLeaf     = myBranch->GetLeaf("timestamp");   
   TLeaf *modeLeaf     = myBranch->GetLeaf("is_manual");   
   TLeaf *outputLeaf   = myBranch->GetLeaf("output_enabled");   
   TLeaf *currentLeaf  = myBranch->GetLeaf("current");   
   TLeaf *setpointLeaf = myBranch->GetLeaf("setpoint");   
   TLeaf *pLeaf        = myBranch->GetLeaf("P");   
   TLeaf *iLeaf        = myBranch->GetLeaf("I");   
   TLeaf *dLeaf        = myBranch->GetLeaf("D");   

   YokogawaEvent_t myData; 
   vector<YokogawaEvent_t> Event;  

   char *time_stamp = new char[100];
   TDatime da(2000,0,0,0,0,0);

   int utc_time = 0;
   int myYear=0; 

   const int NEvents = myTree->GetEntries(); 
   for(int i=0;i<NEvents;i++){
      myTree->GetEntry(i);
      // some effort to get a timestamp... 
      utc_time              = timeLeaf->GetValue()/1E+6; // NOTE: This is in usec!  Divide by 10^6.  
      time_stamp            = GetTimeStamp(utc_time); 
      if(gIsDebug) std::cout << i << "\t" << utc_time << "\t" << time_stamp << "\t" << currentLeaf->GetValue() << std::endl; 
      da.Set(time_stamp);
      myYear = da.GetYear();
      if(myYear<2000) continue;  
      myData.timestamp      = (Int_t)( da.Convert() );  
      myData.ID             = i+1; 
      myData.is_manual      = (Int_t)( modeLeaf->GetValue()   );  
      myData.output_enabled = (Int_t)( outputLeaf->GetValue() );  
      myData.current        = currentLeaf->GetValue();  
      myData.setpoint       = setpointLeaf->GetValue();  
      myData.P              = pLeaf->GetValue();  
      myData.I              = iLeaf->GetValue();  
      myData.D              = dLeaf->GetValue(); 
      Event.push_back(myData);  
   } 

   TString xAxis = Form("ID"); 
   if(gUseTimeStamp) xAxis = Form("timestamp");  

   TGraph *gCurrent  = GetTGraph(xAxis,"current"  ,Event);
   TGraph *gSetpoint = GetTGraph(xAxis,"setpoint" ,Event);
   TGraph *gMode     = GetTGraph(xAxis,"is_manual",Event);
   TGraph *gP        = GetTGraph(xAxis,"P"        ,Event);
   TGraph *gI        = GetTGraph(xAxis,"I"        ,Event);
   TGraph *gD        = GetTGraph(xAxis,"D"        ,Event);

   SetGraphParameters(gCurrent ,20,kBlack);
   SetGraphParameters(gSetpoint,20,kBlack);
   SetGraphParameters(gMode    ,20,kBlack);
   SetGraphParameters(gP       ,20,kBlack);
   SetGraphParameters(gI       ,20,kBlack);
   SetGraphParameters(gD       ,20,kBlack);

   TString xAxisTitle = Form("Event ID");
   if(gUseTimeStamp) xAxisTitle = Form("Time");

   TCanvas *c1 = new TCanvas("c1","Power Supply Feedback",1200,800); 
   c1->Divide(1,2); 

   c1->cd(1);
   gCurrent->Draw("alp");
   gCurrent->SetTitle("Current"); 
   gCurrent->GetXaxis()->SetTitle(xAxisTitle); 
   gCurrent->GetXaxis()->CenterTitle(); 
   if(gUseTimeStamp){
      gCurrent->GetXaxis()->SetTimeDisplay(1);
      gCurrent->GetXaxis()->SetTimeFormat("#splitline{%m-%d-%y}{%H:%M:%S}");
      gCurrent->GetXaxis()->SetLabelOffset(0.03);
      gCurrent->GetXaxis()->SetTimeOffset(0);
   }
   gCurrent->GetYaxis()->SetTitle("Current (mA)"); 
   gCurrent->GetYaxis()->CenterTitle(); 
   gCurrent->Draw("alp");
   c1->Update(); 
 
   c1->cd(2);
   gSetpoint->Draw("ap");
   gSetpoint->SetTitle("Setpoint"); 
   gSetpoint->GetXaxis()->SetTitle(xAxisTitle); 
   gSetpoint->GetXaxis()->CenterTitle(); 
   if(gUseTimeStamp){
      gSetpoint->GetXaxis()->SetTimeDisplay(1);
      gSetpoint->GetXaxis()->SetTimeFormat("#splitline{%m-%d-%y}{%H:%M:%S}");
      gSetpoint->GetXaxis()->SetLabelOffset(0.03);
      gSetpoint->GetXaxis()->SetTimeOffset(0);
   }
   gSetpoint->GetYaxis()->SetTitle("Setpoint (Hz)"); 
   gSetpoint->GetYaxis()->CenterTitle(); 
   gSetpoint->Draw("ap");
   c1->Update(); 

   TCanvas *c2 = new TCanvas("c2","Power Supply Feedback (Parameters)",1200,800); 
   c2->Divide(2,2); 

   c2->cd(1);
   gMode->Draw("ap");
   gMode->SetTitle("Mode (0 = manual, 1 = auto)"); 
   gMode->GetXaxis()->SetTitle(xAxisTitle); 
   gMode->GetXaxis()->CenterTitle(); 
   if(gUseTimeStamp){
      gMode->GetXaxis()->SetTimeDisplay(1);
      gMode->GetXaxis()->SetTimeFormat("#splitline{%m-%d-%y}{%H:%M:%S}");
      gMode->GetXaxis()->SetLabelOffset(0.03);
      gMode->GetXaxis()->SetTimeOffset(0);
   }
   gMode->GetYaxis()->SetTitle("Mode"); 
   gMode->GetYaxis()->CenterTitle(); 
   gMode->Draw("ap");
   c2->Update(); 
  
   c2->cd(2);
   gP->Draw("ap");
   gP->SetTitle("Feedback Coefficient P"); 
   gP->GetXaxis()->SetTitle(xAxisTitle); 
   gP->GetXaxis()->CenterTitle(); 
   if(gUseTimeStamp){
      gP->GetXaxis()->SetTimeDisplay(1);
      gP->GetXaxis()->SetTimeFormat("#splitline{%m-%d-%y}{%H:%M:%S}");
      gP->GetXaxis()->SetLabelOffset(0.03);
      gP->GetXaxis()->SetTimeOffset(0);
   }
   gP->GetYaxis()->SetTitle("P"); 
   gP->GetYaxis()->CenterTitle(); 
   gP->Draw("ap");
   c2->Update(); 
   
   c2->cd(3);
   gI->Draw("ap");
   gI->SetTitle("Feedback Coefficient I"); 
   gI->GetXaxis()->SetTitle(xAxisTitle); 
   gI->GetXaxis()->CenterTitle(); 
   if(gUseTimeStamp){
      gI->GetXaxis()->SetTimeDisplay(1);
      gI->GetXaxis()->SetTimeFormat("#splitline{%m-%d-%y}{%H:%M:%S}");
      gI->GetXaxis()->SetLabelOffset(0.03);
      gI->GetXaxis()->SetTimeOffset(0);
   }
   gI->GetYaxis()->SetTitle("I"); 
   gI->GetYaxis()->CenterTitle(); 
   gI->Draw("ap");
   c2->Update(); 

   c2->cd(4);
   gD->Draw("ap");
   gD->SetTitle("Feedback Coefficient D"); 
   gD->GetXaxis()->SetTitle(xAxisTitle); 
   gD->GetXaxis()->CenterTitle(); 
   if(gUseTimeStamp){
      gD->GetXaxis()->SetTimeDisplay(1);
      gD->GetXaxis()->SetTimeFormat("#splitline{%m-%d-%y}{%H:%M:%S}");
      gD->GetXaxis()->SetLabelOffset(0.03);
      gD->GetXaxis()->SetTimeOffset(0);
   }
   gD->GetYaxis()->SetTitle("I"); 
   gD->GetYaxis()->CenterTitle(); 
   gD->Draw("ap");
   c2->Update(); 

}
//______________________________________________________________________________
TGraph *GetTGraph(TString xaxis,TString yaxis,vector<YokogawaEvent_t> Event){
   vector<double> x,y; 
   FillVector(xaxis,Event,x); 
   FillVector(yaxis,Event,y);
   TGraph *g = GetTGraph(x,y);
   return g;  
}
//______________________________________________________________________________
void FillVector(TString axis,vector<YokogawaEvent_t> Event,vector<double> &v){
   const int N = Event.size(); 
   if(axis=="ID")             for(int i=0;i<N;i++) v.push_back( Event[i].ID );  
   if(axis=="timestamp")      for(int i=0;i<N;i++) v.push_back( Event[i].timestamp );  
   if(axis=="is_manual")      for(int i=0;i<N;i++) v.push_back( Event[i].is_manual );  
   if(axis=="output_enabled") for(int i=0;i<N;i++) v.push_back( Event[i].output_enabled );  
   if(axis=="current")        for(int i=0;i<N;i++) v.push_back( Event[i].current );  
   if(axis=="setpoint")       for(int i=0;i<N;i++) v.push_back( Event[i].setpoint );  
   if(axis=="P")              for(int i=0;i<N;i++) v.push_back( Event[i].P );  
   if(axis=="I")              for(int i=0;i<N;i++) v.push_back( Event[i].I );  
   if(axis=="D")              for(int i=0;i<N;i++) v.push_back( Event[i].D );  
}
//______________________________________________________________________________
char *GetTimeStamp(int unix_time){
    time_t     utime = unix_time;
    struct tm  ts;
    char       buf[100];
    // Format time, "ddd yyyy-mm-dd hh:mm:ss zzz"
    ts = *localtime(&utime);
    strftime(buf, sizeof(buf), "%a %Y-%m-%d %H:%M:%S %Z", &ts);
    // format time stamp: remove timezone at the end 
    int length = strlen(buf);
    for(int i=length-1;i>=length-3;i--) buf[i] = '\0';
    // format time stamp: remove day label at the front  
    char *time_stamp = new char[100];
    strcpy(time_stamp,buf);
    for(int i=0;i<3;i++) time_stamp++;
    return time_stamp;
}


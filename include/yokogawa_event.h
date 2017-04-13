#ifndef YOKOGAWAEVENT_H
#define YOKOGAWAEVENT_H

// a data structure for a Yokogawa event  
// to be used when generating a ROOT file for a run  

typedef struct yokogawa_event{
   long int timestamp;    // UTC timestamp 
   int is_manual;         // manual mode (1) or auto [fixed probe input] (0) 
   int output_enabled;    // is output enabled (1) or disabled (0)  
   double current;        // current read back from device in mA  
   double p_fdbk;         // coefficient for feedback    
   double i_fdbk;         // coefficient for feedback
   double d_fdbk;         // coefficient for feedback
   double setpoint;       // user-defined setpoint in mA  
} yokogawa_event_t; 

#endif 

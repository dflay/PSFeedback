#ifndef YOKOGAWA_H
#define YOKOGAWA_H

// a data structure for the Yokogawa data 

typedef struct yokogawa{
   long int timestamp;    // UTC timestamp 
   double current;        // in mA  
   double p_fdbk;         // coefficient for feedback    
   double i_fdbk;         // coefficient for feedback
   double d_fdbk;         // coefficient for feedback
   double setpoint;       // user-defined setpoint  
} yokogawa_t; 

#endif 

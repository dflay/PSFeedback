#ifndef YOKOGAWA_EVENT_H
#define YOKOGAWA_EVENT_H

typedef struct YokogawaEvent{
   Int_t ID;
   Int_t timestamp;
   Int_t is_manual;
   Int_t output_enabled;
   Double_t current;
   Double_t setpoint;
   Double_t P;
   Double_t I;
   Double_t D;
} YokogawaEvent_t;

#endif 

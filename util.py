#! /usr/bin/python 
# miscellaneous functions  

import global_var
from datetime  import datetime
import random

def get_random(minVal,maxVal): 
    return random.randrange(minVal,maxVal)

def now_timestamp(ts_mult=global_var.TS_MULT_us, epoch=global_var.UNIX_EPOCH):
    dt       = datetime.utcnow() - epoch 
    tot_usec = int( dt.total_seconds()*ts_mult )
    return tot_usec

def now_timestamp_2(ts_mult=global_var.TS_MULT_us,epoch=global_var.UNIX_EPOCH): 
    # NOTE: this method works in python 2.6; differs from the above function 
    #       by 2E-14. (6E-6 ppb)   
    dt          = datetime.utcnow() - epoch # timedelta object 
    dt_tot_usec = int( dt.microseconds + 0.0 + (dt.seconds + dt.days*24*3600)*1E+6 )
    return dt_tot_usec


#! /usr/bin/python 
# miscellaneous functions  

import os.path 
import sys
from datetime import datetime
import random
import pytz

SECONDS = 1
MINUTES = 60*SECONDS 
HOURS   = 60*MINUTES

UNIX_EPOCH_naive        = datetime(1970, 1, 1, 0, 0) # offset-naive datetime
UNIX_EPOCH_offset_aware = datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc) # offset-aware datetime
UNIX_EPOCH              = UNIX_EPOCH_naive
TS_MULT_us              = 1E6

def get_random(minVal,maxVal): 
    return random.randrange(minVal,maxVal)

def now_timestamp(ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    dt       = datetime.utcnow() - epoch 
    tot_usec = int( dt.total_seconds()*ts_mult )
    return tot_usec

def now_timestamp_2(ts_mult=TS_MULT_us,epoch=UNIX_EPOCH): 
    # NOTE: this method works in python 2.6; differs from the above function 
    #       by 2E-14. (6E-6 ppb)   
    dt          = datetime.utcnow() - epoch # timedelta object 
    dt_tot_usec = int( dt.microseconds + 0.0 + (dt.seconds + dt.days*24*3600)*1E+6 )
    return dt_tot_usec 

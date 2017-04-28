#! /usr/bin/python 
# miscellaneous functions  

import os.path 
import sys
import numpy as np
import datetime
import random
import pytz

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



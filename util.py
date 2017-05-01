#! /usr/bin/python 
# miscellaneous functions  

import os.path 
import sys
from datetime import datetime
import random
import pytz

UNIX_EPOCH_naive        = datetime(1970, 1, 1, 0, 0) # offset-naive datetime
UNIX_EPOCH_offset_aware = datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc) # offset-aware datetime
UNIX_EPOCH              = UNIX_EPOCH_naive
TS_MULT_us              = 1e6

def get_random(minVal,maxVal): 
    return random.randrange(minVal,maxVal)

def now_timestamp(ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    return( int( (datetime.utcnow() - epoch).total_seconds()*ts_mult ) )

# def now_timestamp(): 
#     utcTime   = datetime.utcnow()
#     timeStamp = int( utcTime.timestamp() ) 
#     return timeStamp  

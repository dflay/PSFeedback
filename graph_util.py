#! /usr/bin/python 
# functions used when plotting yokogawa data  

import datetime
import pytz
import pyqtgraph as pg

UNIX_EPOCH_naive        = datetime.datetime(1970, 1, 1, 0, 0)                    # offset-naive datetime
UNIX_EPOCH_offset_aware = datetime.datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc) # offset-aware datetime
UNIX_EPOCH              = UNIX_EPOCH_naive
TS_MULT_us              = 1e6

def int2dt(ts, ts_mult=TS_MULT_us):
    return(datetime.datetime.utcfromtimestamp(float(ts)/ts_mult))

def dt2int(dt, ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    delta = dt - epoch
    return(int(delta.total_seconds()*ts_mult))

def td2int(td, ts_mult=TS_MULT_us):
    return(int(td.total_seconds()*ts_mult))

def int2td(ts, ts_mult=TS_MULT_us):
    return(datetime.timedelta(seconds=float(ts)/ts_mult))

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        # return [QTime().addMSecs(value).toString('mm:ss') for value in values]
        # return [int2dt(value).strftime("%H:%M:%S.%f") for value in values]
        return [int2dt(value).strftime("%H:%M:%S") for value in values]


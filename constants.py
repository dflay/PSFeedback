# constants 
from datetime import datetime
import pytz

SECONDS                 = 1
MINUTES                 = 60*SECONDS
HOURS                   = 60*MINUTES
UNIX_EPOCH_naive        = datetime(1970, 1, 1, 0, 0) # offset-naive datetime
UNIX_EPOCH_offset_aware = datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc) # offset-aware datetime
UNIX_EPOCH              = UNIX_EPOCH_naive
TS_MULT_us              = 1E6

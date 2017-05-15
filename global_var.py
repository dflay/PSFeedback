from datetime import datetime
import pytz

# constants
SECONDS                 = 1
MINUTES                 = 60*SECONDS
HOURS                   = 60*MINUTES
UNIX_EPOCH_naive        = datetime(1970, 1, 1, 0, 0) # offset-naive datetime
UNIX_EPOCH_offset_aware = datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc) # offset-aware datetime
UNIX_EPOCH              = UNIX_EPOCH_naive
TS_MULT_us              = 1E6

# global variables 
LOWER_LIMIT             = -200                      # in mA 
UPPER_LIMIT             =  200                      # in mA 
PREV_LVL                = 0                         # in mA 
PREV_TIME               = 0                         # in seconds  
READOUT_DELAY           = 0.5*SECONDS               # in seconds 
RUN_TIME                = 2*HOURS                   # in seconds  
CONV_mA_TO_AMPS         = 1E-3                      # 1 mA = 10^-3 A  
CONV_Hz_TO_AMPS         = (1./32.)*(5200./61.79E+6) # A/Hz 
EVENT_NUMBER            = 0
DATA_FN                 = "ps-feedback"             # output file name
IP_ADDR                 = "192.168.5.160"
DATA_DIR                = './data'
FILE_EXT                = 'csv'
IS_DEBUG                = True
WRITE_ROOT              = True                      # write ROOT file  

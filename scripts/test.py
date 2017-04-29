#! /usr/bin/python 
# test out talking to yokogawa using the yokogawa class  

import sys 
import time 
from instrument import yokogawa 
from timeit     import default_timer as timer
# start a timer 
t_start = timer()

# get list of arguments to the program 
# arglist = sys.argv
# 
# print "Command line args:"
# for entry in arglist:
#     print "{0}".format(entry)

print("----------- Testing Yokogawa Communication -----------")

# get instance of yokogawa object  
yoko    = yokogawa()
# open the VXI-connection  
ip_addr = "192.168.5.160"  
rc = yoko.open_vxi_connection(ip_addr)
print(yoko.status_msg)
if rc==1:
    sys.exit()
# get device ID 
dev_id = yoko.get_device_id()
yoko.Print() 
# get the mode  
mode = yoko.get_mode() 
print("mode = {0}".format(mode)) 
# get the current/voltage level 
current = yoko.get_level() 
print("level = {0:.4f} mA".format( float(current)/1E-3 )) 
# close the connection 
yoko.close_vxi_connection()
# stop the timer 
t_stop = timer() 
dt     = t_stop - t_start
print("elapsed time: {0:.4f}".format(dt))


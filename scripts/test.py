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
# get the output state
output_state = yoko.get_output_state() 
print("output state = {0}".format(output_state))
# get the mode  
mode = yoko.get_mode() 
print("mode = {0}".format(mode)) 
# set to current mode 
print("setting to current mode...")
rc   = yoko.clear_errors() 
rc   = yoko.set_to_current_mode() 
mode = yoko.get_mode() 
print("mode = {0}".format(mode)) 
rc = yoko.set_range_max() 
rc = yoko.set_level(0.00) 
# get the current/voltage level 
current = yoko.get_level() 
print("level = {0:.4f} mA".format( float(current)/1E-3 )) 
# close the connection 
yoko.close_vxi_connection()
# stop the timer 
t_stop = timer() 
dt     = t_stop - t_start
print("elapsed time: {0:.4f}".format(dt))


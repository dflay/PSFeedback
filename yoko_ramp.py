#! /usr/bin/python 
# test out talking to yokogawa using the yokogawa class  
# ramp from -5 mA to + 5 mA 

import sys 
import time 
import matplotlib.pyplot as plt 
import numpy as np
from instrument import yokogawa 
from timeit     import default_timer as timer

IsTestMode = 2   # 0 = scan currents; 1 = run self test, print device info and quit; 2 = plot random ints in a plot  

NARGS = len(sys.argv) 
if(NARGS!=2): 
    print "Invalid input!"
    print "Usage: python {0} [IP address]".format(sys.argv[0])
    sys.exit(0) 

# get arguments from command line  
ip_addr = sys.argv[1]

# ip_addr = "192.168.5.160"
yoko    = yokogawa(ip_addr)

# try connecting to the device
# will return 1 if it fails  
rc      = yoko.open_vxi_connection()

if(rc==1 and IsTestMode!=2): 
   print "Exiting..."
   sys.exit(0) 

# show device info  
yoko.Print()  

if(IsTestMode==1):  
    response = yoko.run_self_test() 
    print response
    
    response = yoko.run_error_check() 
    print response
    
    mode = yoko.get_mode()
    print mode 
    
    output_state = yoko.get_output_state() 
    print output_state 
    
    time = yoko.get_clock_time() 
    print time 
    
    date = yoko.get_clock_date() 
    print date 
    yoko.close_vxi_connection()
    sys.exit(0) 

# get ready for current scan
# turn on output, close connection  
if(rc==0): 
    yoko.set_output_state(1) 
    yoko.close_vxi_connection()

# set up a plot
plt.ion() # Note: enables interactive plotting 
plt.xlabel('Event')
plt.ylabel('Current (mA)')
plt.title('Yokogawa Current')

i = 0
current = 0

#  bring in the currents
setPt = [] 
inpath = "./input/current-list.txt" 
infile = open(inpath,"r") 
for line in infile:
    line.strip('\n')
    setPt.append( float(line) ) 

print "Currents to scan: "
print setPt 

NPTS = 300 # len(setPt)  
for i in range(0,NPTS): 
    t_start = timer() 
    if(IsTestMode==0): 
         rc = yoko.open_vxi_connection()
         if(rc==0): 
             mode = yoko.get_mode() 
             print "mode = {0}".format(mode)  
             yoko.set_level(setPt[i]) 
             current = yoko.get_level() 
             print "level = {0:.4f} mA".format( float(current)/1E-3 ) 
             yoko.close_vxi_connection()  
             t_stop = timer() 
             dt     = t_stop - t_start
             print "elapsed time: {0:.4f}".format(dt)
             print "-------------------------------------"
    elif(IsTestMode==2):
         x_val = float(i)
         y_val = np.random.random()  
         # print "event {0}: \t {1} " .format(x_val,y_val)
         # plt.scatter(x_val,y_val)
         plt.plot(x_val,y_val,marker='o',color='b',linestyle='-') 
         plt.pause(0.100) #Note this correction 
         time.sleep(1)  # 1-second delay 
         

# disable and reset to zero  
rc = yoko.open_vxi_connection()
if(rc==0): 
    yoko.set_output_state(0)
    yoko.set_level(0)  
    yoko.close_vxi_connection()
 

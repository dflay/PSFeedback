# python class to talk to Yokogawa 
# - contains predefined functions and other convenient wrappers 
#   so we don't have to remember the Yokogawa commands 

import vxi11

class yokogawa(object): 
        #_____________________________________________________________________________
        def __init__(self,ip_addr): 
            self.ip_addr   = ip_addr 
            self.mfg       = "NONE"
            self.model_no  = "NONE"
            self.serial_no = "NONE"
            self.fw_ver    = "NONE"   # firmware version 
        #_____________________________________________________________________________
        def open_vxi_connection(self): 
            VISA_str = self.get_VISA_string("TCPIP",self.ip_addr)
            print "Opening VXI-11 connection...".format(self.mfg)
            response = "UNKNOWN"
            rc = 0 
            try:
                self.dev = vxi11.Instrument(VISA_str)
                self.dev.open() 
                response = "open"
            except: 
                response = "FAILED"
                rc = 1 
            else: 
                id_data = self.get_device_id() 
            print "[{0}]: VXI-11 connection {1}.".format(self.mfg,response)
            return rc
        #_____________________________________________________________________________
        def close_vxi_connection(self): 
            self.dev.close()
            print "[{0}]: VXI-11 connection closed.".format(self.mfg)
        #_____________________________________________________________________________
        def get_VISA_string(self,aType,id_tag):
            a_str = "UNKNOWN"
            if (aType=="GPIB"):
                a_str = ""
            elif (aType=="USB"):
                a_str = ""
            elif (aType=="TCPIP"):
                a_str = "TCPIP::%s::INSTR" %(id_tag)
            return a_str
        #_____________________________________________________________________________
        def get_device_id(self):
            cmd = "*IDN?"
            response       = self.ask(cmd) 
            myList         = response.split(',') 
            self.mfg       = myList[0]
            self.model_no  = myList[1]
            self.serial_no = myList[2]
            self.fw_ver    = myList[3]
            return response  
        #_____________________________________________________________________________
        def get_mode(self):
            cmd = ":SOUR:FUNC?"
            response = self.ask(cmd) 
            return response 
        #_____________________________________________________________________________
        def get_level(self): 
            cmd = ":SOUR:LEV?"
            response = self.ask(cmd) 
            return response 
        #_____________________________________________________________________________
        def get_range(self): 
            cmd = ":SOUR:RANG?"
            response = self.ask(cmd) 
            return response 
        #_____________________________________________________________________________
        def run_self_test(self):
            cmd = "*TST?" 
            response = self.ask(cmd) 
            return response 
        #_____________________________________________________________________________
        def run_error_check(self):
            cmd = ":SYSTem:ERRor?" 
            response = self.ask(cmd) 
            return response 
        #_____________________________________________________________________________
        def get_output_state(self): 
            cmd = "OUTP?" 
            response = self.ask(cmd) 
            return response  
        #_____________________________________________________________________________
        def get_clock_time(self): 
            cmd = ":SYST:CLOC:TIME?"
            response = self.ask(cmd) 
            return response  
        #_____________________________________________________________________________
        def get_clock_date(self): 
            cmd = ":SYST:CLOC:DATE?"
            response = self.ask(cmd) 
            return response 
        #_____________________________________________________________________________
        def set_to_voltage_mode(self): 
            cmd = ":SOUR:FUNC VOLT"
            rc  = self.write(cmd)
            return rc 
        #_____________________________________________________________________________
        def set_to_current_mode(self): 
            cmd = ":SOUR:FUNC CURR"
            rc  = self.write(cmd)
            return rc 
        #_____________________________________________________________________________
        def set_range(self,value): 
            cmd = ":SOUR:RANG {0:.0E}".format( float(value) ) 
            rc  = self.write(cmd)
            return rc 
        #_____________________________________________________________________________
        def set_range_min(self): 
            cmd = ":SOUR:RANG MIN" 
            rc  = self.write(cmd)
            return rc 
        #_____________________________________________________________________________
        def set_range_max(self): 
            cmd = ":SOUR:RANG MAX" 
            rc  = self.write(cmd)
            return rc 
        #_____________________________________________________________________________
        def set_level(self,value): 
            cmd = ":SOUR:LEV {0:.5f}".format( float(value) ) 
            rc  = self.write(cmd)
            return rc
        #_____________________________________________________________________________
        def set_output_state(self,value): 
            cmd = "OUTP:STAT {0:d}".format( float(value) ) 
            rc  = self.write(cmd) 
            return rc 
        #_____________________________________________________________________________
        def set_clock_time(self,hour,minute,second): 
            fhr  = float(hour) 
            fmin = float(minute) 
            fsec = float(second)  
            cmd  = ':SYST:CLOC:TIME "{0:02d}:{1:02d}:{2:02d}"'.format(fhr,fmin,fsec)
            rc   = self.write(cmd) 
            return rc 
        #_____________________________________________________________________________
        def set_clock_date(self,month,day,year):
            fmon = float(month) 
            fday = float(day) 
            fyr  = float(year)  
            cmd  = ':SYST:CLOC:DATE "{0:04d}/{1:02d}/{2:02d}"'.format(fyr,fmon,fday)
            rc   = self.write(cmd) 
            return rc 
        #_____________________________________________________________________________
        def write(self,cmd):
            rc = 0 
            try: 
                self.dev.write(cmd)
            except: 
                print "[{0}]: write {1} FAILED.".format(self.mfg,cmd) 
                rc = 1 
            return rc  
        #_____________________________________________________________________________
        def ask(self,cmd):
            response = "NO RESPONSE" 
            try:  
                response = self.dev.ask(cmd)
            except: 
                print "[{0}]: ask {1} FAILED.".format(self.mfg,cmd) 
            return response 
        #_____________________________________________________________________________
        def Print(self):
            print "--------------------------------------------"
            print "MFG:           {0}".format(self.mfg      )
            print "Model No.:     {0}".format(self.model_no ) 
            print "Serial No.:    {0}".format(self.serial_no)
            print "Firmware Ver.: {0}".format(self.fw_ver   ) 
            print "IP Address:    {0}".format(self.ip_addr  )
            print "--------------------------------------------"
            # print "subnet:      %s" %(self.subnet)
            # print "gateway:     %s" %(self.gateway)
            # print "MAC address: %s" %(self.mac_addr)
        #_____________________________________________________________________________


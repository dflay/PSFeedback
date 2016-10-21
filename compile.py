#! /usr/bin/python 

import os
import subprocess

executable = "yoko_simple"; 
cmd        = "gcc -Wall -I/usr/include/python2.6 -lpython2.6 {0}.c -o {0}".format(executable); 
print cmd   
os.system(cmd) 

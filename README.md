# PSFeedback
Software to regulate the magnet power supply for the muon g-2 magnet.

# Running the GUI/DAQ

To run the GUI, run `python yoko_gui.py`.  This will start up the GUI.  Before starting a run, 
enter the IP address of the Yokogawa device, and click *Connect*.  If successful, 
a status message will display saying that you are connected.  Otherwise, an error will be displayed. 
From here, enter a setpoint in the setpoint field, and click *Apply*.  To start a run, 
click *Start Run*.  To stop a run, click *Stop Run*.    

# Installation Directions

## Prerequisites 

Some libraries are needed to run the GUI: 
1. python-vxi11 (https://github.com/python-ivi/python-vxi11) 
2. SIP (to install PyQt) 
3. PyQt (4 or 5) and/or PySide 
4. pyqtgraph

### VXI-11

1. Run `sudo python setup.py install` from the python-vxi11 directory
2. Modify `PYTHONPATH` in your bashrc to `export PYTHONPATH = /usr/lib/python2.6/site-packages/python_vxi11-0.9-py2.6.egg:$PYTHONPATH` 

### SIP 

1. Go to /lib/ directory and unpack the SIP library
2. Run the configure script `python configure.py`; this will create the Makefile and associated tools
3. Run `make`, then `sudo make install`.   

### PyQt 

### pyqtgraph

1. Go to /lib/pyqtgraph-0.10.0
2. Run the installation script `sudo python setup.py install` 


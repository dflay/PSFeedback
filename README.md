# PSFeedback
Software to regulate the magnet power supply for the muon g-2 magnet.

# Running the GUI/DAQ

To run the GUI, run `python yoko_gui.py`.  This will start up the GUI.  Before starting a run, 
enter the IP address of the Yokogawa device, and click **Connect**.  If successful, 
a status message will display saying that you are connected.  Otherwise, an error will be displayed. 
From here, enter a setpoint in the setpoint field, and click **Apply**.  To start a run, 
click **Start Run**.  To stop a run, click **Stop Run**.    

# Installation Directions

## Prerequisites 

Some libraries are needed to run the GUI: 
1. python-vxi11 (https://github.com/python-ivi/python-vxi11) 
2. numpy
3. SIP (to install PyQt) 
4. qmake
5. PyQt (4 or 5)  
6. pyqtgraph

### VXI-11

1. Run `sudo python setup.py install` from the python-vxi11 directory
2. Modify `PYTHONPATH` in your bashrc to `export PYTHONPATH = /usr/lib/python2.6/site-packages/python_vxi11-0.9-py2.6.egg:$PYTHONPATH` 

### numpy

1. Enter into the python environment by running `pyenv` 
2. Run `sudo yum install numpy.x86_64` 

### SIP 

To install SIP, first activate the python environment (pyenv) 

1. Go to /lib/ directory and unpack the SIP library
2. Run the configure script `python configure.py`; this will create the Makefile and associated tools
3. Run `make`, then `sudo make install`.   

### qmake 

Tool for generating configure script for qmake-based projects (needed for PyQt) 

1. Enter into the python environment by running `pyenv` 
2. Run `sudo yum install qconf.x86_64` 

### PyQt4 or PyQt5  

1. Go into the python environment
2. Should grab PySide: `sudo yum install python-pyside.x86_64`

### pyqtgraph

1. Go to /lib/pyqtgraph-0.10.0
2. Run the installation script `sudo python setup.py install` 
3. Modify `PYTHONPATH` in your bashrc to `export PYTHONPATH = /usr/lib/python2.6/site-packages/:$PYTHONPATH` 


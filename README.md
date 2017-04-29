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
4. qmake (for PyQt) 
5. PyQt (4 or 5)  
6. pyqtgraph

Note: For the directions below, we may need to enter into the python environment.  Do this by running `pyenv27`.  

### VXI-11

1. Run `python setup.py install` from the python-vxi11 directory

### numpy

1. Enter into the python environment  
2. Run `sudo yum install numpy.x86_64` 

### SIP 

1. Go to /lib/ directory and unpack the SIP library
2. Deactivate the UPS environment (comment out .upsrc in the .bashrc file)
3. Logout, log back in to refresh the paths
4. Run `scl enable python27 /bin/bash`
2. Activate the python environment 
3. Run the configure script `python configure.py`; this will create the Makefile and associated tools
4. Run `make`, then `sudo make install`.   

### qmake 

Tool for generating configure script for qmake-based projects (needed for PyQt) 

1. Activate the python environment 
2. Run `sudo yum install qconf.x86_64` 

### PyQt4 or PyQt5  

1. Should grab PySide: `sudo yum install python-pyside.x86_64`
2. Deactivate the UPS environment (comment out .upsrc in the .bashrc file)
3. Logout, log back in to refresh the paths
4. Run `scl enable python27 /bin/bash`
5. Activate the python environment
6. Configure: `python configure-ng.py  --qmake /home/newg2/pyenv27/bin/qmake-qt4 --static`
7. `make`
   - it will fail when it gets to the line about
     QtGuiQAbstractPrintDialog.  Edit the file
     ~/QtGui/sipQtGuiQAbstractPrintDialog.cpp, and comment
     out that line mentioning the PrintCurrentPage thing.
     Try make again.
8. `sudo make install` 

### pyqtgraph

1. Run `scl enable python27 /bin/bash`
2. Activate the python environment
3. Go to /lib/pyqtgraph-0.10.0
4. Run the installation script `sudo python setup.py install` 


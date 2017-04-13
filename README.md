# PSFeedback
Software to regulate the magnet power supply for the muon g-2 magnet.

## Prerequisites 

Some libraries are needed to run the GUI: 
1. pyqtgraph
2. python-vxi11 (https://github.com/python-ivi/python-vxi11) 
3. PyQt (4 or 5) and/or PySide 
4. SIP (to install PyQt) 

## Installation Directions

### VXI-11

1. Run `sudo python setup.py install` from the python-vxi11 directory
2. Modify `PYTHONPATH` in your bashrc to `export PYTHONPATH = /usr/lib/python2.6/site-packages/python_vxi11-0.9-py2.6.egg:$PYTHONPATH` 

### SIP 

1. Go to /lib/ directory and unpack the SIP library
2. Run the configure script `python configure.py`; this will create the Makefile and associated tools
3. Run `make`, then `sudo make install`.   

### PyQt 

### pyqtgraph



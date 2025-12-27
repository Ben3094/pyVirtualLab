# pyVirtualLab

**An abstraction library to laboratory instruments**

This library is used as Python drivers to turn various physical instruments into Python objects. It uses pyVISA as a base but it is more object-oriented. To not rely on platform-specific implementation of VISA, this library uses pyVISA pure Python back-end.

> **Use pure Python back-end**
>
> 1. Install "pyVISA" and "pyVISA-py" package on your environment
> ```sh
> # In terminal
> pip install -U pyvisa
> pip install -U pyvisa-py
> ```
> 2. In your Python code, use the following command to get a universal VISA resource manager.
> ```python
> resourceManager = pyvisa.ResourceManager('@py')
> ```
> 3. You good to go !

## Instrument object

This object is a common base for child objects to define common methods, fields, and properties. They simplify development of dedicated intrument Python objects.

An ```Instrument``` is initiated using a VISA formatted address (see "VPP-4.3: The VISA Library" at 4.3.1.1 section). It can also define the timeout used for the communication through the ```visaTimeout``` argument. Both argument can also be changed after with the corresponding ```Instrument``` properties (i.e., ```Address``` and ```VISATimeout```).

A couple of methods (i.e., ```Connect``` and ```Disconnect```) and a property (i.e., ```IsConnected```) manage connection/disconnection procedures.

Methods to sent raw string commands (see IVI fundation SCPI Volume 1: Syntax and Style) to the VISA device (i.e., ```Read```, ```Write```, and ```Query```) are public. But their use is up to pyVirtualLab user.

Common standard commands are defined as methods in this first implementation:
- ```Wait```: To wait for operations to finish on the physical VISA device
- ```SelfTest```: To test the physical VISA device
- ```Reset```: To reset the physical VISA device

Once connected, few read-only properties are updated:
- ```Id```: Raw ID returned by the physical VISA device
- ```Vendor```: Device vendor (extracted from ID)
- ```Model```: Device model (extracted from ID)

## Source object

This object derives from ```Instrument```. As a source could be switched off in case of an emergency, the ```Source``` object defines an ```Abort``` method. The base implementation is to execute the ```Reset``` method on targeted physical VISA device.

We invite developers that create a ```Source```-based driver to customize the ```__abort__``` hiden method. This way, they can implement a tailored switch-off procedure.

## Provided Python drivers

All provided drivers are located in ```pyVirtualLab.Instruments```.

As of now, this library provides few instrument drivers:
- ```Keysight.E3642A```: Agilent E3642A power source
- ```Keysight.N5183B```: Agilent N5183B synthesizer
- ```Keysight.N191X```: Keysight N191X power meter series
- ```Keysight.N6705C```: Keysight N6705C multiple power supply
- ```Keysight.MSOS804A```: Keysight MSOS804A oscilloscope
- ```Keysight.E363XXX```: Keysight E363XXX multiple power supply series
- ```Keysight.G_33210A```: Agilent 33210A function generator
- ```Keysight.N9040B```: Keysight N9040B signal analyser
- ```LeCroy.2610N```: LeCroy 2610N oscilloscope series
- ```RohdeAndSchwarz.RTB2XXX```: Rohde & Schwarz RTB2XXX oscilloscope series

Except ```Keysight.N191X```, all other drivers have not been tested for close, and maybe compatible, instruments.
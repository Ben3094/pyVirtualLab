from pyVirtualLab.VISAInstrument import Source, GetProperty
from pyVirtualLab.Instruments.KeysightN6705C.Outputs import *
from pyvisa import VisaIOError

class KeysightN6705C(Source):
	def __init__(self, address):
		super(KeysightN6705C, self).__init__(address)
		self.__outputs__:dict[int, Output] = None

	MAX_OUTPUTS = 4

	@property
	def Outputs(self) -> dict[int, Output]:
		if self.__outputs__ == None:
			self.__outputs__ = dict()
			address = 0
			connectedOutputs = int(self.Query('SYST:CHAN:COUN'))
			while address <= KeysightN6705C.MAX_OUTPUTS and len(self.__outputs__) < connectedOutputs:
				address += 1
				try:
					output = globals()[str(self.Query('SYST:CHAN:MOD', f"(@{address})")).replace('\n','')]
					self.__outputs__[address] = output(self, address)
				except KeyError:
					output = Output
					self.__outputs__[address] = output(self, address)
				except VisaIOError:
					pass
		return self.__outputs__

	LOW_INTERVAL_PARAMETER = 'RES20'
	HIGH_INTERVAL_PARAMETER = 'RES40'
	@property
	def LowIntervalEnabled(self) -> bool:
		return self.__parent__.Query('SENS:SWE:TINT:RES') == KeysightN6705C.LOW_INTERVAL_PARAMETER
	@LowIntervalEnabled.setter
	def LowIntervalEnabled(self, value: bool):
		value = KeysightN6705C.LOW_INTERVAL_PARAMETER if value else KeysightN6705C.HIGH_INTERVAL_PARAMETER
		self.__parent__.Write('SENS:SWE:TINT:RES', value)
		if self.LowIntervalEnabled != value:
			raise Exception(f"Error while {'en' if value else 'dis'}abling high time resolution")
		
	@property
	@GetProperty(float, 'SENS:SWE:TINT')
	def Interval(self, getMethodReturn) -> float:
		return getMethodReturn
	@Interval.setter
	def Interval(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write('SENS:SWE:TINT', value)

	ASCII_DATA_FORMAT = 'ASC'
	REAL_DATA_FORMAT = 'REAL'
	@property
	def __isDataASCII__(self) -> bool:
		return self.Query('FORM:DATA') == KeysightN6705C.ASCII_DATA_FORMAT
	@__isDataASCII__.setter
	def __isDataASCII__(self, value: bool) -> bool:
		value = bool(value)
		self.Write('FORM:DATA', KeysightN6705C.ASCII_DATA_FORMAT if value else KeysightN6705C.REAL_DATA_FORMAT)
		if self.__isDataASCII__ != value:
			raise Exception("Error while setting data format")
		return value
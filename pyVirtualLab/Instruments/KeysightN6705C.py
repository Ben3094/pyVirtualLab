from enum import Flag, unique
from aenum import Enum
from pyVirtualLab.VISAInstrument import Source, GetProperty, SetProperty

@unique
class Condition(Flag):
	OK = 0
	OverVoltage = 1
	OverCurrent = 2
	PowerFailure = 4
	PositivePowerLimitExceeded = 8
	OverTemperature = 16
	NegativePowerLimitExceeded = 32
	PositiveVoltageLimitExceeded = 64
	PositiveVoltageOrCurrentLimit = 128
	NegativeVoltageOrCurrentLimit = 256
	ExternalInhibit = 512
	Unregulated = 1024
	CoupledProtection = 2048
	DetectedOscillation = 4096

@unique
class MeasureType(Enum):
	Average = 'DC'
	RMS = 'ACDC'
	HighLevel = 'HIGH'
	LowLevel = 'LOW'
	Maximum = 'MAX'
	Minimum = 'MIN'

class Output():
	def __init__(self, parentKeysightN6705C, address):
		self.__parent__ = parentKeysightN6705C
		self.__address__ = address
		self.__model__ = str(self.__parent__.Query("SYST:CHAN:MOD", f"(@{self.Address})"))
		self.__options__ = str(self.__parent__.Query("SYST:CHAN:OPT", f"(@{self.Address})"))
		self.__serialNumber__ = str(self.__parent__.Query("SYST:CHAN:SER", f"(@{self.Address})"))

	@property
	def Address(self) -> int:
		return self.__address__

	@property
	def Model(self) -> str:
		return self.__model__

	@property
	def Options(self) -> str:
		return self.__options__

	@property
	def SerialNumber(self) -> str:
		return self.__serialNumber__

	@property
	def Conditions(self) -> Condition:
		return Condition(int(self.__parent__.Query("STAT:QUES:COND", f"(@{self.Address})")))

	DEFAULT_FORMAT = "{:2.6f}"
	@property
	def MaxVoltage(self) -> float:
		return float(self.__parent__.Query("SOUR:VOLT:PROT:LEV", f"(@{self.Address})"))
	@MaxVoltage.setter
	def MaxVoltage(self, value: float):
		value = float(value)
		self.__parent__.Write(f"SOUR:VOLT:PROT:LEV {str(value)},(@{self.Address})")
		self.__parent__.Write(f"SOUR:VOLT:PROT:STAT ON,(@{self.Address})")
		if self.MaxVoltage != float(self.DEFAULT_FORMAT.format(value)):
			raise Exception("Error while setting the voltage protection value")

	@property
	def Voltage(self) -> float:
		return float(self.__parent__.Query("SOUR:VOLT:LEV:IMM:AMPL", f"(@{self.Address})"))
	@Voltage.setter
	def Voltage(self, value: float):
		value = float(value)
		self.__parent__.Write(f"SOUR:VOLT:LEV:IMM:AMPL {str(value)},(@{self.Address})")
		if self.Voltage != float(self.DEFAULT_FORMAT.format(value)):
			raise Exception("Error while setting the voltage")
		self.__parent__.Write(f"OUTP:PROT:CLE (@{self.Address})")
		if self.Conditions == Condition.OverVoltage:
			raise Exception("Voltage set is superior or equal to maximum voltage")

	@property
	def MeasuredVoltage(self, measureType: MeasureType=MeasureType.Average) -> float:
		return float(self.__parent__.Query(f"MEAS:SCAL:VOLT:{measureType.value}", f"(@{self.Address})").lstrip('[').rstrip(']'))
	@property
	def MeasuredCurrent(self, measureType: MeasureType=MeasureType.Average) -> float:
		return float(self.__parent__.Query(f"MEAS:SCAL:CURR:{measureType.value}", f"(@{self.Address})").lstrip('[').rstrip(']'))
	POWER_NOT_AVAILABLE_MEASURE_TYPE = [MeasureType.RMS, MeasureType.LowLevel, MeasureType.HighLevel]
	@property
	def MeasuredPower(self, measureType: MeasureType=MeasureType.Average) -> float:
		if measureType in Output.POWER_NOT_AVAILABLE_MEASURE_TYPE:
			raise Exception("This type of measure is not available")
		return float(self.__parent__.Query(f"MEAS:SCAL:POW:{measureType.value}", f"(@{self.Address})").lstrip('[').rstrip(']'))

	@property
	def MaxCurrent(self) -> float:
		if self.__parent__.Query("SOUR:CURR:PROT:STAT", f"(@{self.Address})") == 'OFF':
			return None
		else:
			return float(self.__parent__.Query("SOUR:CURR:LEV:IMM:AMPL", f"(@{self.Address})"))
	@MaxCurrent.setter
	def MaxCurrent(self, value):
		if value == None:
			maxCurrent = self.__parent__.Query("SOUR:CURR:RANG", f"(@{self.Address})")
			self.__parent__.Write(f"SOUR:CURR:LEV:IMM:AMPL {maxCurrent},(@{self.Address})")
			self.__parent__.Write(f"SOUR:CURR:PROT:STAT OFF,(@{self.Address})")
		else:
			value = float(value)
			self.__parent__.Write(f"SOUR:CURR:LEV:IMM:AMPL {str(value)},(@{self.Address})")
			if self.MaxCurrent != float(self.DEFAULT_FORMAT.format(value)):
				raise Exception("Error while setting the maximum current")
			self.__parent__.Write(f"SOUR:CURR:PROT:STAT ON,(@{self.Address})")
		
		self.__parent__.Write(f"OUTP:PROT:CLE (@{self.Address})")
		if self.Conditions == Condition.OverCurrent:
			raise Exception("Current set is superior or equal to maximum current")

	@property
	def IsEnabled(self) -> bool:
		return bool(int(self.__parent__.Query("OUTP:STAT", f"(@{self.Address})")))
	@IsEnabled.setter
	def IsEnabled(self, value) -> bool:
		value = bool(value)
		self.__parent__.Write(f"OUTP:STAT {str(int(value))}", f",(@{self.Address})")
		newValue = self.IsEnabled
		if newValue != value:
			raise Exception("Error while en/dis-abling source")
		return newValue
		
	@property
	def MaxMeasuredCurrentSet(self) -> float:
		if bool(int(self.__parent__.Query('SENS:DLOG:CURR:RANG:AUTO', f"(@{self.Address})"))):
			return float('inf')
		else:
			return float(self.__parent__.Query('SENS:DLOG:CURR:RANG', f"(@{self.Address})"))
	@MaxMeasuredCurrentSet.setter
	def MaxMeasuredCurrentSet(self, value: float) -> float:
		value = float(value)
		if str(value) == 'inf':
			self.__parent__.Write(f"SENS:DLOG:CURR:RANG:AUTO 1,(@{self.Address})")
		else:
			self.__parent__.Write(f"SENS:DLOG:CURR:RANG {value},(@{self.Address})")
			self.__parent__.Write(f"SENS:DLOG:CURR:RANG:AUTO 0,(@{self.Address})")
		
	@property
	def MaxMeasuredVoltageSet(self) -> float:
		if bool(int(self.__parent__.Query('SENS:DLOG:VOLT:RANG:AUTO', f"(@{self.Address})"))):
			return float('inf')
		else:
			return float(self.__parent__.Query('SENS:DLOG:VOLT:RANG', f"(@{self.Address})"))
	@MaxMeasuredVoltageSet.setter
	def MaxMeasuredVoltageSet(self, value: float) -> float:
		value = float(value)
		if str(value) == 'inf':
			self.__parent__.Write(f"SENS:DLOG:VOLT:RANG:AUTO 1,(@{self.Address})")
		else:
			self.__parent__.Write(f"SENS:DLOG:VOLT:RANG {value},(@{self.Address})")
			self.__parent__.Write(f"SENS:DLOG:VOLT:RANG:AUTO 0,(@{self.Address})")

	VOLTAGE_HEADER = 'VOLT'
	CURRENT_HEADER = 'CURR'
	POWER_HEADER = 'POW'
	def GetMeasuredVoltage(self) -> list[float]:
		return self.__getMesuredValues__(Output.VOLTAGE_HEADER)
	def GetMeasuredCurrent(self) -> list[float]:
		return self.__getMesuredValues__(Output.CURRENT_HEADER)
	def GetMeasuredPower(self) -> list[float]:
		return self.__getMesuredValues__(Output.POWER_HEADER)
	def __getMesuredValues__(self, header):
		savedASCIIFormat = self.__parent__.__isDataASCII__
		self.__parent__.__isDataASCII__ = True
		values = [float(value) for value in self.__parent__.Query(f"FETC:ARR:{header} (@{self.Address})").lstrip('[').rstrip(']').split(',')]
		if not savedASCIIFormat:
			self.__parent__.__isDataASCII__ = False
		return values
		
	@property
	def TriggeringVoltage(self) -> float:
		return float(self.__parent__.Query(f"TRIG:ACQ:VOLT, (@{self.Address})"))
	@TriggeringVoltage.setter
	def TriggeringVoltage(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"TRIG:ACQ:VOLT {value}, (@{self.Address})")
		if self.TriggeringVoltage != value:
			raise Exception("Error while setting the triggering voltage")
		return value
	TRIGGERING_POSITIVE_SLOPE_HEADER = 'POS'
	TRIGGERING_NEGATIVE_SLOPE_HEADER = 'NEG'
	@property
	def IsTriggeringVoltageSlopePositive(self) -> bool:
		return self.__parent__.Query(f"TRIG:ACQ:VOLT:SLOP, (@{self.Address})") == Output.TRIGGERING_POSITIVE_SLOPE_HEADER
	@IsTriggeringVoltageSlopePositive.setter
	def IsTriggeringVoltageSlopePositive(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"TRIG:ACQ:VOLT:SLOP {Output.TRIGGERING_POSITIVE_SLOPE_HEADER if value else Output.TRIGGERING_NEGATIVE_SLOPE_HEADER}, (@{self.Address})")
		if self.IsTriggeringVoltageSlopePositive != value:
			raise Exception("Error while setting voltage trigger slope direction")
		return value
		
	@property
	def TriggeringCurrent(self) -> float:
		return float(self.__parent__.Query(f"TRIG:ACQ:CURR, (@{self.Address})"))
	@TriggeringCurrent.setter
	def TriggeringCurrent(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"TRIG:ACQ:CURR {value}, (@{self.Address})")
		if self.TriggeringCurrent != value:
			raise Exception("Error while setting the triggering current")
		return value
	@property
	def IsTriggeringCurrentSlopePositive(self) -> bool:
		return self.__parent__.Query(f"TRIG:ACQ:CURR:SLOP, (@{self.Address})") == Output.TRIGGERING_POSITIVE_SLOPE_HEADER
	@IsTriggeringCurrentSlopePositive.setter
	def IsTriggeringCurrentSlopePositive(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"TRIG:ACQ:CURR:SLOP {Output.TRIGGERING_POSITIVE_SLOPE_HEADER if value else Output.TRIGGERING_NEGATIVE_SLOPE_HEADER}, (@{self.Address})")
		if self.IsTriggeringCurrentSlopePositive != value:
			raise Exception("Error while setting current trigger slope direction")
		return value

class N6734B(Output):
	def __init__(self, parentKeysightN6705C, address):
		super(N6734B, self).__init__(parentKeysightN6705C, address)

class KeysightN6705C(Source):
	def __init__(self, address):
		super(KeysightN6705C, self).__init__(address)
		self.__outputs__ = None

	MAX_OUTPUTS = 4

	@property
	def Outputs(self) -> dict[int, Output]:
		if self.__outputs__ == None:
			self.__outputs__ = dict()
			address = 0
			connectedOutputs = int(self.Query('SYST:CHAN:COUN'))
			while address <= KeysightN6705C.MAX_OUTPUTS and len(self.Outputs) < connectedOutputs:
				address += 1
				output = None
				try:
					output = globals()[str(self.Query('SYST:CHAN:MOD', f"(@{address})")).replace('\n','')]
				except: pass
				if output == None:
					output = Output
				self.Outputs[address] = output(self, address)
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
			raise Exception("Error while en/dis-abling high time resolution")
		
	@property
	@GetProperty(float, 'SENS:SWE:TINT')
	def Interval(self, getMethodReturn) -> float:
		return getMethodReturn
	@Interval.setter
	def Interval(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write('SENS:SWE:TINT', value)

	

	ASCII_DATA_FORMAT = 'ASCII'
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
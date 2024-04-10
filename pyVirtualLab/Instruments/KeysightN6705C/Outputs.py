from aenum import Flag, unique, Enum
from pyVirtualLab.Instruments.KeysightN6705C.Triggers import Trigger, NAMES, SOURCE_PATTERN
from re import match, Match

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
class EmulatedSource(Enum):
	BipolarWithLoad = 'PS4Q'
	UnipolarWithLoad = 'PS2Q'
	Unipolar = 'PS1Q'
	Battery = 'BATT'
	BatteryCharger = 'CHAR'
	ConstantCurrentLoad = 'CCL'
	ConstantVoltageLoad = 'CVL'
	Voltmeter = 'VMET'
	Ammeter = 'AMET'

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
	def __clearPreviousConditionAndCheck__(self):
		self.__parent__.Write(f"OUTP:PROT:CLE (@{self.Address})")
		if self.Conditions != Condition.OK:
			raise Exception(f"Bad condition encountered: \"{self.Conditions.value}\"")

	DEFAULT_DECIMAL_FORMAT = "{:2.6f}"
	def CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value:float) -> float:
		if value == None:
			return None
		else:
			return float(Output.DEFAULT_DECIMAL_FORMAT.format(value))
		
	@property
	def MaxVoltage(self) -> float:
		if self.__parent__.Query('SOUR:VOLT:PROT:STAT', f"(@{self.Address})") == 'OFF':
			return None
		else:
			return float(self.__parent__.Query("SOUR:VOLT:PROT:LEV", f"(@{self.Address})"))
	@MaxVoltage.setter
	def MaxVoltage(self, value: float):
		if value != None:
			self.__parent__.Write(f"SOUR:VOLT:PROT:STAT OFF,(@{self.Address})")
		else:
			value = float(value)
			self.__parent__.Write(f"SOUR:VOLT:PROT:LEV {str(value)},(@{self.Address})")
			self.__parent__.Write(f"SOUR:VOLT:PROT:STAT ON,(@{self.Address})")

		if self.MaxVoltage != Output.CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value):
			raise Exception("Error while setting the voltage protection value")

	def __getVoltage__(self) -> float:
		return float(self.__parent__.Query("SOUR:VOLT:LEV:IMM:AMPL", f"(@{self.Address})"))
	def __setVoltage__(self, value:float) -> float:
		value = float(value)
		self.__parent__.Write(f"SOUR:VOLT:LEV:IMM:AMPL {str(value)},(@{self.Address})")
		currentSetVoltage = self.Voltage
		if currentSetVoltage != float(Output.DEFAULT_DECIMAL_FORMAT.format(value)):
			raise Exception("Error while setting the voltage")
		else:
			return currentSetVoltage
	@property
	def Voltage(self) -> float:
		return self.__getVoltage__()
	@Voltage.setter
	def Voltage(self, value: float):
		self.__setVoltage__(value)
		self.__clearPreviousConditionAndCheck__()

	def __getCurrentHighLimit__(self) -> float:
		if self.__parent__.Query("SOUR:CURR:PROT:STAT", f"(@{self.Address})") == 'OFF':
			return None
		else:
			return float(self.__parent__.Query("SOUR:CURR:LEV:IMM:AMPL", f"(@{self.Address})"))
	def __setCurrentHighLimit__(self, value:float) -> float:
		if value == None:
			maxCurrent = self.__parent__.Query("SOUR:CURR:RANG", f"(@{self.Address})")
			self.__parent__.Write(f"SOUR:CURR:LEV:IMM:AMPL {maxCurrent},(@{self.Address})")
			self.__parent__.Write(f"SOUR:CURR:PROT:STAT OFF,(@{self.Address})")
		else:
			value = float(value)
			self.__parent__.Write(f"SOUR:CURR:LEV:IMM:AMPL {str(value)},(@{self.Address})")
			if self.Current != float(self.DEFAULT_DECIMAL_FORMAT.format(value)):
				raise Exception("Error while setting the maximum current")
			self.__parent__.Write(f"SOUR:CURR:PROT:STAT ON,(@{self.Address})")
		currentSetCurrent = self.Current
		if currentSetCurrent != Output.CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value):
			raise Exception("Error while setting the voltage protection value")
		else:
			return currentSetCurrent
	@property
	def Current(self) -> float:
		return self.__getCurrentHighLimit__()
	@Current.setter
	def Current(self, value:float):
		self.__setCurrentHighLimit__(value)
		self.__clearPreviousConditionAndCheck__()
			
	@property
	def LowLimit(self) -> float:
		pass
	@LowLimit.setter
	def LowLimit(self, value:float) -> float:
		return value

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

	__trigger__ = None
	@property
	def Trigger(self) -> Trigger:
		reply:Match = match(SOURCE_PATTERN, self.__parent__.Query('TRIG:ACQ:SOUR', f"(@{self.Address})"))
		if type(self.__trigger__) != NAMES[reply[1]]:
			if self.__trigger__:
				self.__trigger__.__parent__ = None # Unlink old trigger object
			self.__trigger__ = NAMES[reply[1]](self)
		return self.__trigger__
	@Trigger.setter
	def Trigger(self, value:Trigger) -> Trigger:
		self.__parent__.Write('TRIG:ACQ:SOUR', f"{value.__name__}, (@{self.Address})")
		self.__trigger__ = value
		currentTrigger = self.Trigger
		if currentTrigger != value:
			raise Exception("Error while setting trigger mode")
		return currentTrigger

	def __getMeasuredValues__(self, header, measureType:MeasureType, whenTriggered:bool, onlyLast:bool) -> list[float]:
		savedASCIIFormat = self.__parent__.__isDataASCII__
		self.__parent__.__isDataASCII__ = True
		query = f"{'FETC' if whenTriggered else 'MEAS'}:{'SCAL' if onlyLast else 'ARR'}:{header}:{measureType} (@{self.Address})"
		values = [float(value) for value in self.__parent__.Query(query).lstrip('[').rstrip(']').split(',')]
		if not savedASCIIFormat:
			self.__parent__.__isDataASCII__ = False
		return values[0] if onlyLast else values
	VOLTAGE_HEADER = 'VOLT'
	CURRENT_HEADER = 'CURR'
	POWER_HEADER = 'POW'
	def GetMeasuredVoltage(self, measureType:MeasureType=MeasureType.Average, whenTriggered:bool=True) -> float:
		return self.__getMeasuredValues__(Output.VOLTAGE_HEADER, measureType, whenTriggered, onlyLast=True)
	def GetMeasuredCurrent(self, measureType:MeasureType=MeasureType.Average, whenTriggered:bool=True) -> float:
		return self.__getMeasuredValues__(Output.CURRENT_HEADER, measureType, whenTriggered, onlyLast=True)
	def GetMeasuredPower(self, whenTriggered:bool=True) -> float:
		measureType=MeasureType.Average
		return self.__getMeasuredValues__(Output.POWER_HEADER, measureType, whenTriggered, onlyLast=True)
	def GetVoltagesWaveform(self, whenTriggered:bool=True) -> list[float]:
		measureType=MeasureType.Average
		return self.__getMeasuredValues__(Output.VOLTAGE_HEADER, measureType, whenTriggered, onlyLast=False)
	def GetCurrentsWaveform(self, whenTriggered:bool=True) -> list[float]:
		measureType=MeasureType.Average
		return self.__getMeasuredValues__(Output.CURRENT_HEADER, measureType, whenTriggered, onlyLast=False)
	def GetPowersWaveform(self, whenTriggered:bool=True) -> list[float]:
		measureType=MeasureType.Average
		return self.__getMeasuredValues__(Output.POWER_HEADER, measureType, whenTriggered, onlyLast=False)

class N6734B(Output):
	def __init__(self, parentKeysightN6705C, address):
		super(N6734B, self).__init__(parentKeysightN6705C, address)

class N678XA(Output):
	def __init__(self, parentKeysightN6705C, address):
		super(N678XA, self).__init__(parentKeysightN6705C, address)

	AVAILABLED_EMULATED_SOURCES:list[EmulatedSource] = list()
	ALLOWED_EMULATION_IN_PRIORITY_MODE:list[EmulatedSource] = [EmulatedSource.Unipolar, EmulatedSource.UnipolarWithLoad, EmulatedSource.BipolarWithLoad]
	@property
	def EmulatedSource(self):
		return EmulatedSource(self.__parent__.Query('SOUR:EMUL', f"(@{self.Address})"))
	@EmulatedSource.setter
	def EmulatedSource(self, value):
		value = EmulatedSource(value)
		if value in self.AVAILABLED_EMULATED_SOURCES:
			self.__parent__.Write('SOUR:EMUL', f"{value.value}, (@{self.Address})")
			if self.EmulatedSource != value:
				raise Exception("Error while setting emulated source")
			return value
		else:
			raise Exception(f"{value} not available for {self.__name__}")
	
	@property
	def IsLimitsCoupled(self) -> bool:
		return bool(int(self.__parent__.Query(f"SOUR:{N678XA.CURRENT_HEADER if self.IsVoltagePrimary else N678XA.VOLTAGE_HEADER}:LIM:COUP", f"(@{self.Address})")))
	@IsLimitsCoupled.setter
	def IsLimitsCoupled(self, value:bool) -> bool:
		match self.EmulatedSource:
			case EmulatedSource.UnipolarWithLoad: pass
			case EmulatedSource.BipolarWithLoad: pass
			case _: raise Exception(f"Negative limit cannot be set in {self.EmulatedSource}")
		value = bool(value)
		self.__parent__.Write(f"SOUR:{N678XA.CURRENT_HEADER if self.IsVoltagePrimary else N678XA.VOLTAGE_HEADER}:LIM:COUP", f"{int(value)}, (@{self.Address})")
		if value != self.IsLimitsCoupled:
			raise Exception(f"Error while {'' if value else 'de'}coupling limits")
		
	VOLTAGE_PRIMARY = 'VOLT'
	CURRENT_PRIMARY = 'CURR'
	@property
	def IsVoltagePrimary(self) -> bool:
		return bool(True if self.__parent__.Query('SOUR:FUNC', f"(@{self.Address})") == N678XA.VOLTAGE_PRIMARY else False)
	@IsVoltagePrimary.setter
	def IsVoltagePrimary(self, value:bool) -> bool:
		def retainCoupledLimitsState(func):
			def wrapper(*args):
				wasLimitsCoupled = self.IsLimitsCoupled
				result = func()
				self.IsLimitsCoupled = wasLimitsCoupled
				return result
			return wrapper
		
		def setVoltagePrimary():
			self.__parent__.Write('SOUR:FUNC', f"{N678XA.VOLTAGE_PRIMARY if value else N678XA.CURRENT_PRIMARY}, (@{self.Address})")

		value = bool(value)
		if not self.EmulatedSource in N678XA.ALLOWED_EMULATION_IN_PRIORITY_MODE:
			raise Exception(f"Setting voltage/current priority is not allowed in {self.EmulatedSource.value} emulation")
		else:
			value =  bool(value)
			coupledLimitsStateRetaining = self.EmulatedSource == EmulatedSource.UnipolarWithLoad|EmulatedSource.BipolarWithLoad
			(retainCoupledLimitsState(setVoltagePrimary) if coupledLimitsStateRetaining else setVoltagePrimary)()
			if self.IsVoltagePrimary != value:
				raise Exception("Error while setting the voltage/current priority")
			return value

	def __getVoltageLowLimit__(self):
		return float(self.__parent__.Query('SOUR:VOLT:LIM:NEG:IMM:AMPL', f"(@{self.Address})"))
	def __setVoltageLowLimit__(self, value:float) -> float:
		value = 'MIN' if value == None else float(value)
		self.__parent__.Write('SOUR:VOLT:LIM:NEG:IMM:AMPL', f"{value}, (@{self.Address})")
		currentSetVoltageLowLimit = self.__getVoltageLowLimit__()
		if currentSetVoltageLowLimit != Output.CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value):
			raise Exception("Error while setting voltage low limit")
		else:
			return currentSetVoltageLowLimit
	def __getVoltageHighLimit__(self):
		return float(self.__parent__.Query('SOUR:VOLT:LIM:POS:IMM:AMPL', f"(@{self.Address})"))
	def __setVoltageHighLimit__(self, value:float) -> float:
		value = 'MAX' if value == None else float(value)
		self.__parent__.Write('SOUR:VOLT:LIM:POS:IMM:AMPL', f"{value}, (@{self.Address})")
		currentSetVoltageHighLimit = self.__getVoltageHighLimit__()
		if currentSetVoltageHighLimit != Output.CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value):
			raise Exception("Error while setting voltage high limit")
		else:
			return currentSetVoltageHighLimit
	@property
	def Voltage(self) -> float:
		if self.IsVoltagePrimary:
			return self.__getVoltage__()
		else:
			return self.__getVoltageHighLimit__()
	@Voltage.setter
	def Voltage(self, value:float) -> float:
		if self.IsVoltagePrimary:
			currentSetVoltage = self.__setVoltage__(value)
		else:
			currentSetVoltage = self.__setVoltageHighLimit__(value)
		self.__clearPreviousConditionAndCheck__()
		return currentSetVoltage
	
	def __getCurrent__(self):
		return float(self.__parent__.Query('SOUR:CURR:LEV:IMM:AMPL', f"(@{self.Address})"))
	def __setCurrent__(self, value:float) -> float:
		value = float(value)
		self.__parent__.Write(f"SOUR:CURR:LEV:IMM:AMPL {str(value)},(@{self.Address})")
		currentSetCurrent = self.Current
		if currentSetCurrent != float(Output.DEFAULT_DECIMAL_FORMAT.format(value)):
			raise Exception("Error while setting the current")
		else:
			return currentSetCurrent
	def __getCurrentHighLimit__(self) -> float:
		return float(self.__parent__.Query('SOUR:CURR:LIM:POS:IMM:AMPL', f"(@{self.Address})"))
	def __setCurrentHighLimit__(self, value:float) -> float:
		value = 'MAX' if value == None else float(value)
		self.__parent__.Write('SOUR:CURR:LIM:POS:IMM:AMPL', f"{value}, (@{self.Address})")
		currentSetCurrentLowLimit = self.__getCurrentHighLimit__()
		if currentSetCurrentLowLimit != Output.CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value):
			raise Exception("Error while setting current high limit")
		else:
			return currentSetCurrentLowLimit
	def __getCurrentLowLimit__(self):
		return float(self.__parent__.Query('SOUR:CURR:LIM:NEG:IMM:AMPL', f"(@{self.Address})"))
	def __setCurrentLowLimit__(self, value:float) -> float:
		value = 'MIN' if value == None else float(value)
		self.__parent__.Write('SOUR:CURR:LIM:NEG:IMM:AMPL', f"{value}, (@{self.Address})")
		currentSetCurrentLowLimit = self.__getCurrentLowLimit__()
		if currentSetCurrentLowLimit != Output.CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value):
			raise Exception("Error while setting current low limit")
		else:
			return currentSetCurrentLowLimit
	@property
	def Current(self) -> float:
		if self.IsVoltagePrimary:
			return self.__getCurrentHighLimit__()
		else:
			return self.__getCurrent__()
	@Current.setter
	def Current(self, value:float) -> float:
		if self.IsVoltagePrimary:
			currentSetVoltage = self.__setCurrentHighLimit__(value)
		else:
			currentSetVoltage = self.__setCurrent__(value)
		self.__clearPreviousConditionAndCheck__()
		return currentSetVoltage
	
	@property
	def NegativeLimit(self) -> float:
		if self.IsVoltagePrimary:
			return self.__getCurrentLowLimit__()
		else:
			return self.__getVoltageLowLimit__()
	@NegativeLimit.setter
	def NegativeLimit(self, value:float) -> float:
		self.IsLimitsCoupled = False
		if self.IsVoltagePrimary:
			currentNegativeLimit = self.__setCurrentLowLimit__(value)
		elif self.EmulatedSource == EmulatedSource.BipolarWithLoad:
			currentNegativeLimit = self.__setVoltageLowLimit__(value)
		else:
			raise Exception("Only 4 quadrant emulating power source (bipolar with load) supports negative voltage limit")
		self.__clearPreviousConditionAndCheck__()
		return currentNegativeLimit

class N6781A(N678XA):
	def __init__(self, parentKeysightN6705C, address):
		super(N6781A, self).__init__(parentKeysightN6705C, address)
		self.AVAILABLED_EMULATED_SOURCES = [EmulatedSource.Unipolar, EmulatedSource.UnipolarWithLoad, EmulatedSource.ConstantCurrentLoad, EmulatedSource.ConstantVoltageLoad, EmulatedSource.Ammeter, EmulatedSource.Voltmeter, EmulatedSource.Battery, EmulatedSource.BatteryCharger]
class N6782A(N678XA):
	def __init__(self, parentKeysightN6705C, address):
		super(N6782A, self).__init__(parentKeysightN6705C, address)
		self.AVAILABLED_EMULATED_SOURCES = [EmulatedSource.Unipolar, EmulatedSource.UnipolarWithLoad, EmulatedSource.ConstantCurrentLoad, EmulatedSource.ConstantVoltageLoad, EmulatedSource.Ammeter, EmulatedSource.Voltmeter]
class N6784A(N678XA):
	def __init__(self, parentKeysightN6705C, address):
		super(N6784A, self).__init__(parentKeysightN6705C, address)
		self.AVAILABLED_EMULATED_SOURCES = [EmulatedSource.Unipolar, EmulatedSource.UnipolarWithLoad, EmulatedSource.ConstantCurrentLoad, EmulatedSource.ConstantVoltageLoad, EmulatedSource.Ammeter, EmulatedSource.Voltmeter, EmulatedSource.BipolarWithLoad]
class N6785A(N678XA):
	def __init__(self, parentKeysightN6705C, address):
		super(N6785A, self).__init__(parentKeysightN6705C, address)
		self.AVAILABLED_EMULATED_SOURCES = [EmulatedSource.Unipolar, EmulatedSource.UnipolarWithLoad, EmulatedSource.ConstantCurrentLoad, EmulatedSource.ConstantVoltageLoad, EmulatedSource.Ammeter, EmulatedSource.Voltmeter, EmulatedSource.Battery, EmulatedSource.BatteryCharger]
class N6786A(N678XA):
	def __init__(self, parentKeysightN6705C, address):
		super(N6786A, self).__init__(parentKeysightN6705C, address)
		self.AVAILABLED_EMULATED_SOURCES = [EmulatedSource.Unipolar, EmulatedSource.UnipolarWithLoad, EmulatedSource.ConstantCurrentLoad, EmulatedSource.ConstantVoltageLoad, EmulatedSource.Ammeter, EmulatedSource.Voltmeter]
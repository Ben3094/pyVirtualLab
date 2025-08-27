from aenum import Enum
from .Measurements import *
					
class Source():
	TYPE_COMMAND_HEADER = None
	
	__commandAddress__:str = None

	def __init__(self):
		self.__commandAddress__ = self.TYPE_COMMAND_HEADER

class DummySource(Source):
	def __eq__(self, value):
		if hasattr(value, 'TYPE_COMMAND_HEADER'):
			return self.TYPE_COMMAND_HEADER == value.TYPE_COMMAND_HEADER
		else: return False

class AuxSource(Source):
	TYPE_COMMAND_HEADER = 'EXT'

class EtmSource(Source):
	TYPE_COMMAND_HEADER = 'ETM'
	
class LineSource(Source):
	TYPE_COMMAND_HEADER = 'LINE'

class ChannelUnit(Enum):
	Volt = 0
	Ampere = 1
	Watt = 2
	Unknown = 3
class Channel(Source):
	TYPE_COMMAND_HEADER = 'C'
	
	__parent__ = None
	__address__:str = None

	def __init__(self, parentOscilloscope, address):
		super().__init__()
		self.__parent__ = parentOscilloscope
		self.__address__ = address
		self.__commandAddress__ = f"{self.__commandAddress__}{self.__address__}"

	def Read(self) -> str:
		return self.__parent__.Read()
	def Write(self, command:str, arguments:str='') -> str:
		return self.__parent__.Write(f"{self.__commandAddress__}:{command}", arguments)
	def Query(self, command:str, arguments:str='') -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:{command}", arguments)
	
	@property
	def Address(self) -> int:
		return self.__address__

	ENABLE_COMMAND:str = 'TRA'
	@property
	def IsEnabled(self) -> bool:
		return bool(self.__parent__.Query(f"{self.__commandAddress__}:{self.ENABLE_COMMAND}"))
	@IsEnabled.setter
	def IsEnabled(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:{self.ENABLE_COMMAND}", value)
		if self.Scale != value:
			raise Exception("Error while dis-/en-abling channel")
		return value

	def GetWaveform(self) -> dict[float, float]:
		self.__parent__.Write("WAV:SOUR", self.__commandAddress__)
		self.__parent__.Write("WAV:BYT LSBF")
		self.__parent__.Write("WAV:FORM WORD")
		yIncrement = float(self.__parent__.Query("WAV:YINC"))
		yOrigin = float(self.__parent__.Query("WAV:YOR"))
		xIncrement = float(self.__parent__.Query("WAV:XINC"))
		xOrigin = float(self.__parent__.Query("WAV:XOR"))
		savedTimeout = self.__parent__.Timeout
		self.__parent__.Timeout = 200000
		data = self.__parent__.__resource__.query_binary_values("WAV:DATA?", datatype='h', is_big_endian=False)
		data = [yIncrement * float(result) + yOrigin for result in data]
		abscissae = range(0, len(data))
		abscissae = [xIncrement * float(abscissa) + xOrigin for abscissa in abscissae]
		data = dict(zip(abscissae, data))
		self.__parent__.Timeout = savedTimeout
		return data
	
	SCALE_COMMAND:str = 'VDIV'
	@property
	def Scale(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:{self.SCALE_COMMAND}"))
	@Scale.setter
	def Scale(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:{self.SCALE_COMMAND}", value)
		if self.Scale != value:
			raise Exception("Error while setting scale")
		return value
	
	OFFSET_COMMAND:str = 'OFST'	
	@property
	def Offset(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:{self.OFFSET_COMMAND}"))
	@Offset.setter
	def Offset(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:{self.OFFSET_COMMAND}", value)
		if self.Offset != value:
			raise Exception("Error while setting offset")
	
	SET_MEASUREMENT_COMMAND:str = 'PACU'
	CUSTOM_MEASUREMENT_PREFIX:str = 'CUST'
	# Measurements	
	def __queryMeasurement__(self, measurementType:MeasurementType, index:int=-1, args:str='', forceDuplication:bool=False) -> Measurement:
		self.__parent__.Write(self.SET_MEASUREMENT_COMMAND, f"1,{measurementType.value},{args}")
		if index == -1:
			index = next(measurement[0] for measurement in self.__parent__.Measurements if measurement[1] == (measurementType, self))
		return self.__parent__.GetMeasurement(index) #TODO: Support adding statistic
	
	def GetFrequency(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.Frequency, args=f"{self.__commandAddress__}")
	def GetPeriod(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.Period, args=f"{self.__commandAddress__}")
	def GetPositiveWidth(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.Width50PercentPositiveSlope, args=f"{self.__commandAddress__}")
	def GetNegativeWidth(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.Width50PercentNegativeSlope, args=f"{self.__commandAddress__}")
	RISING_DUTY_CYCLE_MEASUREMENT_ARGUMENT = 'RIS'
	FALLING_DUTY_CYCLE_MEASUREMENT_ARGUMENT = 'FALL'
	def GetDutyCycle(self, onDownState:bool=False) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.DutyCycle, f"{self.__commandAddress__},{Channel.FALLING_DUTY_CYCLE_MEASUREMENT_ARGUMENT if onDownState else Channel.RISING_DUTY_CYCLE_MEASUREMENT_ARGUMENT}")
	
class VerticalMeasurePossibleChannel(Channel):
	def GetAmplitude(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.Amplitude, args=f"{self.__commandAddress__}")
	def GetMaximum(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.MaximumValue, args=f"{self.__commandAddress__}")
	def GetMinimum(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.MinimumValue, args=f"{self.__commandAddress__}")
	def GetRiseTime(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.RiseTime10To90, args=f"{self.__commandAddress__}")
	def GetFallTime(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.FallTime90To10, args=f"{self.__commandAddress__}")
	def GetPeakToPeakAmplitude(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.PeakToPeak, args=f"{self.__commandAddress__}")
	def GetBase(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.Base, args=f"{self.__commandAddress__}")
	def GetTop(self) -> Measurement:
		return self.__queryMeasurement__(MeasurementType.Top, args=f"{self.__commandAddress__}")
	
	# AC measurements
	OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT = 'DISP'
	OVER_1_CYCLE_MEASUREMENT_ARGUMENT = 'CYCL'
	def GetAverage(self, overOnly1Cycle:bool=False) -> Measurement:
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT, self.__commandAddress__]
		value = self.__queryMeasurement__(MeasurementType.MeanValue, ','.join(args))
		return value
	
	def GetArea(self, overOnly1Cycle:bool=False) -> Measurement:
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT, self.__commandAddress__]
		value = self.__queryMeasurement__(MeasurementType.Area, ','.join(args))
		return value

	WITH_DC_COMPONENT_ARGUMENT = 'DC'
	WITHOUT_DC_COMPONENT_ARGUMENT = 'AC'
	def GetRMS(self, overOnly1Cycle:bool=False, removeDCComponent:bool=True) -> Measurement:
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT, AnalogChannel.WITHOUT_DC_COMPONENT_ARGUMENT if removeDCComponent else AnalogChannel.WITH_DC_COMPONENT_ARGUMENT, self.__commandAddress__]
		value = self.__queryMeasurement__(MeasurementType.RootMeanSquare, ','.join(args))
		return value

class Coupling(Enum):
	AC = 'A1M'
	OneMegaOhmImpedance = 'D1M'
	FiftyOhmImpedance = 'DC50'
	Disconnected = 'GND'
class AnalogChannel(VerticalMeasurePossibleChannel):
	@property
	def Configuration(self) -> Coupling:
		return Coupling(self.__parent__.Query(f"{self.__commandAddress__}:INP"))
	@Configuration.setter
	def Configuration(self, value:Coupling) -> Coupling:
		value = Coupling(value)
		self.__parent__.Write(f"{self.__commandAddress__}:INP {value.value}")
		if self.Configuration != value:
			raise Exception(f"Error while setting channel {self.Address} configuration")
		return value

	@property
	def Label(self) -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:LAB")
	@Label.setter
	def Label(self, value: str) -> str:
		value = str(value)
		if value.isascii() & len(value) <= 16:
			self.__parent__.Write(f"{self.__commandAddress__}:LAB {value}")
		else:
			raise Exception("Label must be ASCII and less or equal 16 characters long")
		if self.Label != value:
			raise Exception("Error while setting label")
		return value

	@property
	def IsInverted(self) -> bool:
		return bool(self.__parent__.Query(f"{self.__commandAddress__}:INV"))
	@IsInverted.setter
	def IsInverted(self, value: bool):
		return self.__parent__.Write(f"{self.__commandAddress__}:INV {int(bool(value))}")
	
	@property
	def Unit(self) -> ChannelUnit:
		match self.__parent__.Query(f"{self.__commandAddress__}:UNIT"):
			case "VOLT":
				return ChannelUnit.Volt
			case "AMP":
				return ChannelUnit.Ampere
			case "WATT":
				return ChannelUnit.Watt
			case "UNKN":
				return ChannelUnit.Unknown
	@Unit.setter
	def Unit(self, value: ChannelUnit):
		match value:
			case ChannelUnit.Volt:
				self.__parent__.Write(f"{self.__commandAddress__}:UNIT VOLT")
			case ChannelUnit.Ampere:
				self.__parent__.Write(f"{self.__commandAddress__}:UNIT AMP")
			case ChannelUnit.Watt:
				self.__parent__.Write(f"{self.__commandAddress__}:UNIT WATT")
			case ChannelUnit.Unknown:
				self.__parent__.Write(f"{self.__commandAddress__}:UNIT UNKN")

	def AutoScale(self):
		self.Write('ASET')
		self.__parent__.Wait()

class WaveformMemoryChannel(VerticalMeasurePossibleChannel):
	TYPE_COMMAND_HEADER = 'M'

	STORE_COMMAND:str = 'STO'
	def Save(self, channel:Channel):
		self.__parent__.Write(self.STORE_COMMAND, f"{channel.__commandAddress__},{self.__commandAddress__}")
	CLEAR_COMMAND:str = 'CLM'
	def Clear(self):
		self.__parent__.Write(self.CLEAR_COMMAND, self.__commandAddress__)
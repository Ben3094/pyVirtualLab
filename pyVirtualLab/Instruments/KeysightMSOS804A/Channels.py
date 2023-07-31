from aenum import Enum

class ResultState(Enum):
	Correct = 0
	Questionable = 1
	Less = 2
	Greater = 3
	Invalid = 4
	EdgeNotFound = 5
	MaxNotFound = 6
	MinNotFound = 7
	TimeNotFound = 8
	VoltageNotFound = 9
	TopEqualsBase = 10
	TooSmall = 11
	LowerNotFoung = 12
	UpperNotFound = 13
	UpperCloseToLower = 14
	TopNotFound = 15
	BaseNotFound = 16
	CompletionCriteriaNotReached = 17
	Impossible = 18
	WaveformNotDisplayed = 19
	HighWaveformClipped = 20
	LowWaveformClipped = 21
	HighAndLowClippedWaveform = 22
	DataContainsHoles = 23
	DataNotFound = 24
	FFTPeakNotFound = 29
	EyePatternNotFound = 30
	NRZEyeNotFound = 31
	ExtinctionRatioInvalid = 32
	MoreThanOneSource = 33
	SignalTooSmall = 35
	AverageWaitToComplete = 36
	WaitingForClock = 38
	NeedJitterMode = 39
	MeasurementNotOnScreen = 40
	ClockRecoveryImpossible = 41
	PLLLoopBandwidthTooHigh = 42
	RJDJNotFound = 43
	ClockRecoveryProhibited = 45
	JitterPreventRJDJSeparation = 46
	SampleRatesDifferent = 52
	SignalsDoNotCross = 53
	SignalTooPeriodic = 54
	OutOfComputingMemory = 55
	LowerThresholdNotFound = 56
	UpperThresholdNotFound = 57
	TooMuchNoise = 59
	NotSuitedMeasurement = 60
	NoOpenEyeFound = 61
	NotSuitedConfiguration = 62
	NotSuitedResponsivity = 63
	CrossCorrelationTimeTooBig = 64
	InvalidEdgePolarity = 65
	CarrierFrequencyNotFound = 66

class Source():
	TYPE_COMMAND_HEADER = None
	
	__commandAddress__:str = None

	def __init__(self):
		self.__commandAddress__ = self.TYPE_COMMAND_HEADER
class AuxSource(Source):
	TYPE_COMMAND_HEADER = 'AUX'
class LineSource(Source):
	TYPE_COMMAND_HEADER = 'LINE'
class ChannelUnit(Enum):
	Volt = 0
	Ampere = 1
	Watt = 2
	Unknown = 3
class Channel(Source):
	TYPE_COMMAND_HEADER = 'CHAN'
	
	__parent__ = None
	__address__:str = None

	def __init__(self, parentKeysightMSOS804A, address):
		super().__init__()
		self.__parent__ = parentKeysightMSOS804A
		self.__address__ = address
		self.__commandAddress__ = f"{self.__commandAddress__}{self.__address__}"

	@property
	def Address(self) -> float:
		return self.__address__

	@property
	def IsEnabled(self) -> bool:
		return bool(int(self.__parent__.Query(f"{self.__commandAddress__}:DISP")))
	@IsEnabled.setter
	def IsEnabled(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:DISP {int(value)}")
		if self.IsEnabled != value:
			raise Exception(f"Error when en/dis-able {self.__commandAddress__}")
		return value

	def GetWaveform(self) -> dict[float, float]:
		self.__parent__.Write("WAV:SOUR", self.__commandAddress__)
		self.__parent__.Write("WAV:BYT LSBF")
		self.__parent__.Write("WAV:FORM WORD")
		yIncrement = float(self.__parent__.Query("WAV:YINC"))
		yOrigin = float(self.__parent__.Query("WAV:YOR"))
		xIncrement = float(self.__parent__.Query("WAV:XINC"))
		xOrigin = float(self.__parent__.Query("WAV:XOR"))
		savedTimeout = self.__parent__.VISATimeout
		self.__parent__.VISATimeout = 200000
		data = self.__parent__.__instr__.query_binary_values("WAV:DATA?", datatype='h', is_big_endian=False)
		data = [yIncrement * float(result) + yOrigin for result in data]
		abscissae = range(0, len(data))
		abscissae = [xIncrement * float(abscissa) + xOrigin for abscissa in abscissae]
		data = dict(zip(abscissae, data))
		self.__parent__.VISATimeout = savedTimeout
		return data
	
	@property
	def Scale(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:SCAL"))
	@Scale.setter
	def Scale(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:SCAL {value}")
		if self.Scale != value:
			raise Exception("Error while setting scale")
		return value
	
	@property
	def Offset(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:OFFS"))
	@Offset.setter
	def Offset(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:OFFS {value}")
		if self.Offset != value:
			raise Exception("Error while setting offset")
		return value
	
	# Measurements
	def __queryMeasurement__(self, command, args) -> (float, ResultState):
		currentSendValidMeasurements = self.__parent__.SendValidMeasurements
		self.__parent__.SendValidMeasurements = True
		values = self.__parent__.Query(command, args).split(',')
		self.__parent__.SendValidMeasurements = currentSendValidMeasurements
		return float(values[0]), ResultState(int(values[1]))
	def GetFrequency(self) -> float:
		return self.__queryMeasurement__("MEAS:FREQ", f"{self.__commandAddress__}")[0]
	def GetPeriod(self) -> float:
		return self.__queryMeasurement__("MEAS:PER", f"{self.__commandAddress__}")[0]
	def GetPositiveWidth(self) -> float:
		return self.__queryMeasurement__("MEAS:PWID", f"{self.__commandAddress__}")[0]
	def GetNegativeWidth(self) -> float:
		return self.__queryMeasurement__("MEAS:NWID", f"{self.__commandAddress__}")[0]
	RISING_DUTY_CYCLE_MEASUREMENT_ARGUMENT = 'RIS'
	FALLING_DUTY_CYCLE_MEASUREMENT_ARGUMENT = 'FALL'
	def GetDutyCycle(self, onDownState:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:DUTY", f"{self.__commandAddress__},{Channel.FALLING_DUTY_CYCLE_MEASUREMENT_ARGUMENT if onDownState else Channel.RISING_DUTY_CYCLE_MEASUREMENT_ARGUMENT}")[0]
	
class VerticalMeasurePossibleChannel(Channel):
	def GetMaximum(self) -> float:
		return float(self.__parent__.Query("MEAS:VMAX", f"{self.__commandAddress__}"))
	def GetMinimum(self) -> float:
		return float(self.__parent__.Query("MEAS:VMIN", f"{self.__commandAddress__}"))
	def GetRange(self) -> float:
		return float(self.__parent__.Query("MEAS:VPP", f"{self.__commandAddress__}"))
	def GetRiseTime(self) -> float:
		return float(self.__parent__.Query("MEAS:RIS", f"{self.__commandAddress__}"))
	def GetFallTime(self) -> float:
		return float(self.__parent__.Query("MEAS:FALL", f"{self.__commandAddress__}"))
	def GetPeakToPeakAmplitude(self) -> float:
		return float(self.__parent__.Query("MEAS:VPP", f"{self.__commandAddress__}"))
	
	# AC measurements
	OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT = 'DISP'
	OVER_1_CYCLE_MEASUREMENT_ARGUMENT = 'CYCL'
	def GetAverage(self, overOnly1Cycle = False) -> float:
		savedSendValidMeas = self.__parent__.SendValidMeasurements
		self.__parent__.SendValidMeasurements = True
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT,
	    		self.__commandAddress__]
		value = float(self.__parent__.Query('MEAS:VAV', ','.join(args)).split(',')[0])
		if not savedSendValidMeas:
			self.__parent__.SendValidMeasurements = False
		return value
	
	def GetArea(self, overOnly1Cycle = False) -> float:
		savedSendValidMeas = self.__parent__.SendValidMeasurements
		self.__parent__.SendValidMeasurements = True
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT,
	    		self.__commandAddress__]
		value = float(self.__parent__.Query('MEAS:AREA', ','.join(args)).split(',')[0])
		if not savedSendValidMeas:
			self.__parent__.SendValidMeasurements = False
		return value

	WITH_DC_COMPONENT_ARGUMENT = 'DC'
	WITHOUT_DC_COMPONENT_ARGUMENT = 'AC'
	def GetRMS(self, overOnly1Cycle = False, removeDCComponent = True) -> float:
		savedSendValidMeas = self.__parent__.SendValidMeasurements
		self.__parent__.SendValidMeasurements = True
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT,
	    		AnalogChannel.WITHOUT_DC_COMPONENT_ARGUMENT if removeDCComponent else AnalogChannel.WITH_DC_COMPONENT_ARGUMENT,
	    		self.__commandAddress__]
		value = float(self.__parent__.Query('MEAS:VRMS', ','.join(args)).split(',')[0])
		if not savedSendValidMeas:
			self.__parent__.SendValidMeasurements = False
		return value

class AnalogChannel(VerticalMeasurePossibleChannel):
	@property
	def Label(self) -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:LAB?")
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

class DigitalChannel(Channel):
	TYPE_COMMAND_HEADER = 'DIG'

class WaveformMemoryChannel(VerticalMeasurePossibleChannel):
	TYPE_COMMAND_HEADER = 'WMEM'
	def Save(self, channel:Channel):
		self.__parent__.Write(f"{self.__commandAddress__}:SAVE", channel.__commandAddress__)
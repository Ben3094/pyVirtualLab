from aenum import Enum, MultiValueEnum

class MeasurementState(Enum):
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

class StatisticMode(MultiValueEnum):
	All = 'ON' 
	Value = 'CURR', 'OFF' 
	Maximum = 'MAX' 
	Mean = 'MEAN' 
	Minimum = 'MIN' 
	StandardDeviation = 'STDD' 
	Count = 'COUN'

class Measurement():
	MEASUREMENT_NAME_COLUMN_NAME:str = "Name"
	MEASUREMENT_CURRENT_VALUE_COLUMN_NAME:str = "Value"
	MEASUREMENT_STATE_COLUMN_NAME:str = "State"
	MEASUREMENTS_MIN_INDEX = 1
	MEASUREMENTS_MAX_INDEX = 20
	MEASUREMENTS_LIMITS = MEASUREMENTS_MAX_INDEX - MEASUREMENTS_MIN_INDEX
	
	def __init__(self, values:dict[str, str]):
		self.__string__ = str(values)

		for value in values:
			match value:
				case self.MEASUREMENT_NAME_COLUMN_NAME:
					self.__name__ = str(values[value])
				case StatisticMode.Value.name:
					self.__value__ = float(values[value])
				case self.MEASUREMENT_STATE_COLUMN_NAME:
					self.__state__ = MeasurementState(int(values[value]))
				case StatisticMode.Minimum.name:
					self.__minimum__ = float(values[value])
				case StatisticMode.Maximum.name:
					self.__maximum__ = float(values[value])
				case StatisticMode.Mean.name:
					self.__mean__ = float(values[value])
				case StatisticMode.StandardDeviation.name:
					self.__standardDeviation__ = float(values[value])
				case StatisticMode.Count.name:
					self.__count__ = int(float(values[value]))

	__string__:str = None
	
	__name__:str = None
	@property
	def Name(self) -> str:
		return self.__name__

	__value__:float = None
	@property
	def Value(self) -> float:
		return self.__value__

	__state__:MeasurementState = None
	@property
	def State(self) -> MeasurementState:
		return self.__state__

	__minimum__:float = None
	@property
	def Minimum(self) -> float:
		return self.__minimum__
	
	__maximum__:float = None
	@property
	def Maximum(self) -> float:
		return self.__maximum__
		
	__mean__:float = None
	@property
	def Mean(self) -> float:
		return self.__mean__
	
	__standardDeviation__:float = None
	@property
	def StandardDeviation(self) -> float:
		return self.__standardDeviation__
	
	__count__:int = None
	@property
	def Count(self) -> int:
		return self.__count__

	def __float__(self):
		return self.__value__
	
	def __repr__(self):
		return self.__string__
from aenum import Enum
from pyVirtualLab.Helpers import GetProperty, SetProperty, CreateReadOnlyProperty
from . import Channels

MEASUREMENT_COMMAND:str = "MEAS"
MEASUREMENTS_MIN_INDEX = 1
MEASUREMENTS_MAX_INDEX = 8
MEASUREMENTS_LIMITS = MEASUREMENTS_MAX_INDEX - MEASUREMENTS_MIN_INDEX

class MeasurementType(Enum):
	Frequency = "FREQ"
	Period = "PER"
	PositiveDutyCycle = "PDCY"
	NegativeDutyCycle = "NDCY"
	RiseTime = "RTIM"
	FallTime = "FTIM"
	PositivePulseWidth = "PPW"
	NegativePulseWidth = "NPW"
	DelayToTrigger = "DTOT"
	Delay = "DEL"
	Phase = "PHAS"
	PositiveSlewRate = "SRR"
	NegativeSlewRate = "SRF"
	BurstWidth = "BWID"
	Amplitude = "AMPL"
	Top = "HIGH"
	Base = "LOW"
	CycleMean = "CYCM"
	CycleRootMeanSquare = "CYCR"
	CycleStandardDeviation = "CYCS"
	PeakPeak = "PEAK"
	UpperPeakValue = "UPE"
	LowerPeakValue = "LPE"
	PositiveOvershoot = "POV"
	NegativeOvershoot = "NOV"
	WindowMean = "MEAN"
	WindowRootMeanSquare = "RMS"
	WindowStandardDeviation = "STDD"
	CrestFactor = ""
	PositivePulseCount = "PPC"
	NegativePulseCount = "NPC"
	RECount = "REC"
	FECount = "FEC"

class Measurement():
	__parent__ = None
	
	def __init__(self, parent, address):
		self.__parent__ = parent
		self.__address__ = address
		self.__commandAddress__ = f"{MEASUREMENT_COMMAND}{self.__address__}"

		self.IsEnabled2 = CreateReadOnlyProperty(self, bool, Measurement.STATE_COMMAND) #TODO: Test this !!!

	@property
	def Address(self) -> float:
		return self.__address__

	def Read(self) -> str:
		return self.__parent__.Read()
	def Write(self, command:str, arguments:str='') -> str:
		return self.__parent__.Write(f"{self.__commandAddress__}:{command}", arguments)
	def Query(self, command:str, arguments:str='') -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:{command}", arguments)
	
	STATE_COMMAND:str = 'STAT'
	@property
	@GetProperty(bool, STATE_COMMAND)
	def IsEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(bool, STATE_COMMAND)
	def IsEnabled(self, value:bool) -> bool:
		pass
	
	TYPE_COMMAND:str = 'MAIN'
	@property
	@GetProperty(MeasurementType, TYPE_COMMAND)
	def Type(self, getMethodReturn) -> MeasurementType:
		return getMethodReturn
	@Type.setter
	@SetProperty(MeasurementType, TYPE_COMMAND)
	def Type(self, value:MeasurementType) -> MeasurementType:
		pass

	SOURCE_COMMAND:str = "SOUR"
	@property
	def Source(self) -> Channels.Source:
		return self.__parent__.StringToChannel(self.Query(Measurement.SOURCE_COMMAND))
	@Source.setter
	def Source(self, value:Channels.Source) -> Channels.Source:
		self.Write(Measurement.SOURCE_COMMAND, f"{value.ARGUMENT_COMMAND_HEADER}{value.Address}")
		if self.Source != value:
			raise Exception(f"Error while setting measurement {self.Address} source")
		return value
	
	RESULT_COMMAND:str = "RES"
	@property
	@GetProperty(float, RESULT_COMMAND)
	def Result(self, getMethodReturn) -> float:
		return getMethodReturn
	@Result.setter
	@SetProperty(float, RESULT_COMMAND)
	def Result(self, value:float) -> float:
		pass
	
	AVERAGE_COMMAND:str = "RES:AVG"
	@property
	@GetProperty(float, AVERAGE_COMMAND)
	def Average(self, getMethodReturn) -> float:
		return getMethodReturn
	@Average.setter
	@SetProperty(float, AVERAGE_COMMAND)
	def Average(self, value:float) -> float:
		pass
	
	STANDARD_DEVIATION_COMMAND:str = "RES:STDD"
	@property
	@GetProperty(float, STANDARD_DEVIATION_COMMAND)
	def StandardDeviation(self, getMethodReturn) -> float:
		return getMethodReturn
	@StandardDeviation.setter
	@SetProperty(float, STANDARD_DEVIATION_COMMAND)
	def StandardDeviation(self, value:float) -> float:
		pass
	
	MINIMUM_COMMAND:str = "RES:NPE"
	@property
	@GetProperty(float, MINIMUM_COMMAND)
	def Minimum(self, getMethodReturn) -> float:
		return getMethodReturn
	@Minimum.setter
	@SetProperty(float, MINIMUM_COMMAND)
	def Minimum(self, value:float) -> float:
		pass
	
	MAXIMUM_COMMAND:str = "RES:PPE"
	@property
	@GetProperty(float, MAXIMUM_COMMAND)
	def Maximum(self, getMethodReturn) -> float:
		return getMethodReturn
	@Maximum.setter
	@SetProperty(float, MAXIMUM_COMMAND)
	def Maximum(self, value:float) -> float:
		pass
	
	COUNT_COMMAND:str = "RES:WFMC"
	@property
	@GetProperty(float, COUNT_COMMAND)
	def Count(self, getMethodReturn) -> float:
		return getMethodReturn
	@Count.setter
	@SetProperty(float, COUNT_COMMAND)
	def Count(self, value:float) -> float:
		pass

	def __float__(self):
		return self.Result
	
	def __repr__(self):
		return self.__string__
from aenum import Enum, MultiValueEnum

class MeasurementType(Enum):
	Amplitude:str = 'AMPL'
	Area:str = 'AREA'
	Base:str = 'BASE'
	Delay:str = 'DLY'
	DutyCycle:str = 'DUTY'
	FallTime90To10:str = 'FALL'
	FallTime80To20:str = 'FALL82'
	Frequency:str = 'FREQ'
	MaximumValue:str = 'MAX'
	MeanValue:str = 'MEAN'
	MinimumValue:str = 'MIN'
	Null:str = 'NULL'
	OvershootNegative:str = 'OVSN'
	OvershootPositive:str = 'OVSP'
	PeakToPeak:str = 'PKPK'
	Period:str = 'PER'
	PhaseDifference:str = 'PHASE'
	RiseTime10To90:str = 'RISE'
	RiseTime20To80:str = 'RISE28'
	RootMeanSquare:str = 'RMS'
	TimeClockToClockEdge:str = 'SKEW'
	StandardDeviation:str = 'SDEV'
	Top:str = 'TOP'
	Width50PercentPositiveSlope:str = 'WID'
	Width50PercentNegativeSlope:str = 'WIDN'
	DeltaPeriodAtLevel:str = 'DPLEV'
	DeltaTimeAtLevel:str = 'DTLEV'
	DutyCycleAtLevel:str = 'DULEV'
	EdgeAtLevel:str = 'EDLEV'
	FrequencyAtLevel:str = 'FREQLEV'
	PeriodAtLevel:str = 'PLEV'
	TimeAtLevel:str = 'TLEV'
	HistogramMean:str = 'AVG'
	MathOnParameters:str = 'CALC'
	CyclesOnScreen:str = 'CYCL'
	DeltaDelay:str = 'DDLY'
	DeltaTriggerTime:str = 'DTRIG'
	DeltaWidthAtLevel:str = 'DWIDLEV'
	DurationOfAcquisition:str = 'DUR'
	ExcelParameter:str = 'EXCELPARAM'
	FallAtLevel:str = 'FLEV'
	FirstSampleInMeasureGate:str = 'FRST'
	HistogramFwhm:str = 'FWHM'
	HistogramPeakFwAtLevel:str = 'FW'
	HalfPeriod:str = 'HPER'
	HistogramAmplitudeHistogram:str = 'HAMPL'
	HistogramBaseLevel:str = 'HBASE'
	HistogramRightBin:str = 'HIGH'
	HistoricalMean:str = 'HMEAN'
	HistogramMedian:str = 'HMEDI'
	TimeClockEdge:str = 'HOLDLEV'
	HistogramRms:str = 'HRMS'
	HistogramTopLevel:str = 'HTOP'
	LastSampleInGate:str = 'LAST'
	HistogramLeftBin:str = 'LOW'
	MathcadParameter:str = 'MATHCADPARAMARITH'
	MatlabParameter:str = 'MATLABPARAM'
	HistogramMaximumPopulation:str = 'MAXP'
	Median:str = 'MEDI'
	HistogramMode:str = 'MODE'
	NarrowBandPhase:str = 'NBPH'
	NarrowBandPower:str = 'NBPW'
	NumberCycleJitter:str = 'NCYCLE'
	VbsScriptParameter:str = 'PARAMSCRIPT'
	HistogramPercentile:str = 'PCTL'
	NumberOfPeaks:str = 'PKS'
	NumberOfPoints:str = 'PNTS'
	PopulationOfHistogamBinAt:str = 'POPAT'
	HistogramRange:str = 'RANGE'
	RiseTimeAtLevel:str = 'RLEV'
	DataEdgeToClockEdge:str = 'SETUP'
	HistogramStandardDeviatm:str = 'SIGMA'
	TirneIntervalErrorAtLevel:str = 'TIELEV'
	HistogramTotalPopulation:str = 'TOTP'
	WidthAtLevel:str = 'WIDLV'
	PositionOfMaxDataValue:str = 'XMAX'
	PositionOfMinDataValue:str = 'XMIN'
	HistogramNthHighestPeak:str = 'XAPK'
	EdgeDisplacement:str = 'EDGEDA'
	PatternTime:str = 'PATTERNTIME'
	RingBackHighLow:str = 'RING'
	LaneToLaneSkew:str = 'SD2SKEW'
	StripDdjFromSource:str = 'STRIPDDJ'
	EyeDiagramZeroLevel:str = 'ZEROLVL'
	EyeAcRms:str = 'EYEACRMS'
	EyePowerLevelRatio:str = 'EXTRATIO'
	EyeAmplitude:str = 'EYEAMPL'
	EyeBitRateEstimate:str = 'EYEBER'
	EyeBitRate:str = 'EYEBITRATE'
	EyeBitTime:str = 'EYEBITTIME'
	EyeCrossing:str = 'EYECROSSING'
	EyeNegativeCrossing:str = 'EYECROSSN'
	EyePositiveCrossing:str = 'EYECROSSP'
	EyeCycArea:str = 'EYECYCAREA'
	EyeDelay:str = 'EYEDELAY'
	EyeDeltaDelay:str = 'EYEDELTDLY'
	EyeFallTime:str = 'EYEFALLTIME'
	EyeHeight:str = 'EYEHEIGHT'
	EyeMean:str = 'EYEMEAN'
	EyeOneLevel:str = 'EYEONE'
	EyeOpeningFactor:str = 'EYEOPENFAC'
	EyeNegativeOvershoot:str = 'EYEOVERN'
	EyePositiveOvershoot:str = 'EYEOVERP'
	EyePeakNoise:str = 'EYEPKNOISE'
	EyePeakToPeakJitter:str = 'EYEPKPKJIT'
	EyePulseWidth:str = 'EYEPULSEWIO'
	EyeQFactor:str = 'EYEQ'
	EyeRiseTime:str = 'EYERISETIME'
	EyeRmsJitter:str = 'EYERMSJIT'
	EyeStandardDeviationNoise:str = 'EYESDNOISE'
	EyeSignalToNoise:str = 'EYESGTONOISE'
	EyeSuppressionRatio:str = 'EYESIJPRATIO'
	EyeWidth:str = 'EYEWIDTH'
	JitterPerDutyCycleDistortion:str = 'PERDCD'
	PersistenceDutyCycle:str = 'PERDUTYCYC'
	PerPulseSymmetry:str = 'PERPULSESYM'
	PcieMiscMeasurements:str = 'PCIEMISC'
	PcieMinPulseWidth:str = 'TMNPLS'
	PcieUncorrelatedPulseWidthDj:str = 'UPWJDD'
	PcieUncorrelatedPulseWidthTj:str = 'UPWTJ'

class MeasurementState(Enum):
	Averaged = 'AV'
	Greater = 'GT'
	Invalid = 'IV'
	Lower = 'LT'
	NoPulse = 'NP'
	Overflow = 'OF'
	OK = 'OK'
	PartialOverflow = 'OU'
	Truncated = 'PT'
	PartiallyUnderflow = 'UF'
MEASUREMENT_STATES_RECOGNITION_PATTERN:str = f"({'|'.join([value.value for value in MeasurementState])}),?"

class StatisticMode(MultiValueEnum):
	# Custom = 'CUST'
	# HorizontalStandard = 'HPAR'
	# VerticalStandard = 'VPAR'
	# ParameterDefined = 'PARAM'
	Average = 'AVG'
	Maximum = 'HIGH'
	Minimum = 'LOW'
	StandardDeviation = 'SIGMA'
	Count = 'SWEEPS'

class Measurement():
	MEASUREMENT_NAME_COLUMN_NAME:str = "Name"
	MEASUREMENT_CURRENT_VALUE_COLUMN_NAME:str = "Value"
	MEASUREMENT_STATE_COLUMN_NAME:str = "State"
	
	def __init__(self, values:dict[str, str]):
		self.__string__ = str(values)

		for value in values:
			match value:
				case self.MEASUREMENT_NAME_COLUMN_NAME:
					self.__name__ = str(values[value])
				case self.MEASUREMENT_CURRENT_VALUE_COLUMN_NAME:
					self.__value__ = float(values[value])
				case self.MEASUREMENT_STATE_COLUMN_NAME:
					self.__state__ = MeasurementState(values[value])
				case StatisticMode.Minimum.name:
					self.__minimum__ = float(values[value])
				case StatisticMode.Maximum.name:
					self.__maximum__ = float(values[value])
				case StatisticMode.Average.name:
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
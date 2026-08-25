from .Channels import Channel, VerticalMeasurePossibleChannel, MeasurementState
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES
from aenum import Enum
import re

class Function(VerticalMeasurePossibleChannel):
	TYPE_COMMAND_HEADER = 'F'
	EQUATION_FORMAT = str()
	PARAMS_STRING_PREFIX:str = "EQN,\""
	PARAMS_STRING_SUFFIX:str = "\""
	PARAMS_STRING_FORMAT = str()
	PARAMS = dict()

	def __init__(self, parentKeysightMSOS804A, address: str):
		super().__init__(parentKeysightMSOS804A, address)

	def ChangeFunction(self, targetedFunction):
		functionType = self.__parent__.GetFunctionType(self.Address)
		if targetedFunction != functionType:
			self.__parent__.Write(f"{self.__commandAddress__}:DEF", targetedFunction.INIT_PARAMS)

	def GetParams(self) -> dict[str, object]:
		savedReturnHeader = self.__parent__.ReturnHeader
		self.__parent__.ReturnHeader = True
		response = self.__parent__.GetFunctionEquation(self.Address)
		self.__parent__.ReturnHeader = savedReturnHeader
		match = re.match(self.PARAMS_STRING_FORMAT, response)
		return match.groupdict()

	def SetParam(self, name: str, value: str) -> str:
		savedReturnHeader = self.__parent__.ReturnHeader
		self.__parent__.ReturnHeader = True
		response = self.__parent__.GetFunctionEquation(self.Address)
		self.__parent__.ReturnHeader = savedReturnHeader
		match = re.match(self.PARAMS_STRING_FORMAT, response)
		currentValue = match.group(name)
		response = str(match.group(0)).replace(currentValue, value)
		self.__parent__.Write(f"{self.__commandAddress__}:DEF {response}")

	AUTO_SCALE_ON_ARGUMENT = 'AUTO'
	AUTO_SCALE_OFF_ARGUMENT = 'MAN'
	@property
	def IsAutoScaleEnabled(self) -> bool:
		return self.__parent__.Query(f"{self.__commandAddress__}:VERT") == Function.AUTO_SCALE_ON_ARGUMENT
	@IsAutoScaleEnabled.setter
	def IsAutoScaleEnabled(self, value:bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:VERT", Function.AUTO_SCALE_ON_ARGUMENT if value else Function.AUTO_SCALE_OFF_ARGUMENT)
		if self.IsAutoScaleEnabled != value:
			raise Exception("Error while setting auto scale")
		
	# @property
	# def Scale(self) -> float:
	# 	return round(float(self.__parent__.Query(f"{self.__commandAddress__}:VERT:RANG")) / 10, 7) # TODO: Check number of reticules
	# @Scale.setter
	# def Scale(self, value:float) -> float:
	# 	value = round(float(value), 7)
	# 	self.__parent__.Write(f"{self.__commandAddress__}:VERT:RANG", str(round(value * 10, 7))) # TODO: Check number of reticules
	# 	if self.Scale != value:
	# 		raise Exception("Error while setting scale")
	
	# @property
	# def Offset(self) -> float:
	# 	return round(float(self.__parent__.Query(f"{self.__commandAddress__}:VERT:OFFS")), 6)
	# @Offset.setter
	# def Offset(self, value:float) -> float:
	# 	value = round(float(value), 6)
	# 	self.__parent__.Write(f"{self.__commandAddress__}:VERT:OFFS", str(value))
	# 	if self.Offset != value:
	# 		raise Exception("Error while setting offset")
	
	SCALE_COMMAND:str = 'VMAG'
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
	
	OFFSET_COMMAND:str = 'VPOS'	
	@property
	def Offset(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:{self.OFFSET_COMMAND}"))
	@Offset.setter
	def Offset(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:{self.OFFSET_COMMAND}", value)
		if self.Offset != value:
			raise Exception("Error while setting offset")
	
	HORIZONTAL_ZOOM_COMMAND:str = 'HMAG'
	@property
	def TimeScale(self) -> float:
		"""
		When doing FFT, it is equal to 1 GHz divided by the frequency scale by division.
		"""
		return float(self.__parent__.Query(f"{self.__commandAddress__}:{self.HORIZONTAL_ZOOM_COMMAND}"))
	@TimeScale.setter
	def TimeScale(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:{self.HORIZONTAL_ZOOM_COMMAND}", value)
		if self.TimeScale != value:
			raise Exception("Error while setting time scale")
	
	
	HORIZONTAL_POSITION_COMMAND:str = 'HPOS'
	@property
	def Delay(self) -> float:
		"""
		When doing FFT, it is equal to the center frequency (GHz).
		"""
		return float(self.__parent__.Query(f"{self.__commandAddress__}:{self.HORIZONTAL_POSITION_COMMAND}"))
	@Delay.setter
	def Delay(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:{self.HORIZONTAL_POSITION_COMMAND}", value)
		if self.Delay != value:
			raise Exception("Error while setting delay")

	def DefineMaxScale(self, extraGap:float=0.5):
		'''
		extraGap: Factor to extend scale to be sure that all signal is displayed
		'''
		min = self.GetMinimum(addToResultsList=False)
		max = self.GetMaximum(addToResultsList=False)
		if any([extreme.State != MeasurementState.Correct for extreme in [min, max]]):
			raise Exception(f"Function {self.Address} signal exceed screen limits")
		self.Scale = (max.Value - min.Value) / 10 * (1 + extraGap)
		self.Offset = (max.Value + min.Value) / 2
		
class AbsoluteFunction(Function):
	NAME = 'ABS'
	INIT_PARAMS = f"{Function.PARAMS_STRING_PREFIX}{NAME}(C1){Function.PARAMS_STRING_SUFFIX}"
	EQUATION_FORMAT = f"{NAME}\((?P<Operand>[A-Z]+\d+)\)"
	PARAMS_STRING_FORMAT = f"{Function.PARAMS_STRING_PREFIX}{EQUATION_FORMAT}{Function.PARAMS_STRING_SUFFIX}"

	@property
	def Operand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Operand'])
	@Operand.setter
	def Operand(self, value: Channel):
		self.SetParam('Operand', value.__commandAddress__)
		if self.Operand.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting operand channel")
		
class ZoomFunction(Function):
	NAME = 'ZOOMONLY'
	INIT_PARAMS = f"{Function.PARAMS_STRING_PREFIX}{NAME}(C1){Function.PARAMS_STRING_SUFFIX}"
	EQUATION_FORMAT = f"{NAME}\((?P<Operand>[A-Z]+\d+)\)"
	PARAMS_STRING_FORMAT = f"{Function.PARAMS_STRING_PREFIX}{EQUATION_FORMAT}{Function.PARAMS_STRING_SUFFIX}"

	@property
	def Operand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Operand'])
	@Operand.setter
	def Operand(self, value: Channel):
		self.SetParam('Operand', value.__commandAddress__)
		if self.Operand.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting operand channel")

class AddFunction(Function):
	NAME = 'SUM'
	INIT_PARAMS = f"{Function.PARAMS_STRING_PREFIX}{NAME}C1+C2{Function.PARAMS_STRING_SUFFIX}"
	EQUATION_FORMAT = f"{NAME}(?P<FirstOperand>[A-Z]+\d+)+(?P<SecondOperand>[A-Z]+\d+)"
	PARAMS_STRING_FORMAT = f"{Function.PARAMS_STRING_PREFIX}{EQUATION_FORMAT}{Function.PARAMS_STRING_SUFFIX}"

	@property
	def FirstOperand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['FirstOperand'])
	@FirstOperand.setter
	def FirstOperand(self, value: Channel):
		self.SetParam('FirstOperand', value.__commandAddress__)
		if self.FirstOperand.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting first operand channel")
			
	@property
	def SecondOperand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['SecondOperand'])
	@FirstOperand.setter
	def SecondOperand(self, value: Channel):
		self.SetParam('SecondOperand', value.__commandAddress__)
		if self.SecondOperand.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting second operand channel")
		
class SubstractFunction(Function):
	NAME = ''
	INIT_PARAMS = f"{Function.PARAMS_STRING_PREFIX}C1-C2{Function.PARAMS_STRING_SUFFIX}"
	EQUATION_FORMAT = f"(?P<FirstOperand>[A-Z]+\d+)-(?P<SecondOperand>[A-Z]+\d+)"
	PARAMS_STRING_FORMAT = f"{Function.PARAMS_STRING_PREFIX}{EQUATION_FORMAT}{Function.PARAMS_STRING_SUFFIX}"

	@property
	def FirstOperand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['FirstOperand'])
	@FirstOperand.setter
	def FirstOperand(self, value: Channel):
		self.SetParam('FirstOperand', value.__commandAddress__)
		if self.FirstOperand.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting first operand channel")
			
	@property
	def SecondOperand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['SecondOperand'])
	@FirstOperand.setter
	def SecondOperand(self, value: Channel):
		self.SetParam('SecondOperand', value.__commandAddress__)
		if self.SecondOperand.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting second operand channel")
		
class EnvelopeFunction(Function):
	NAME = 'EXTR'
	INIT_PARAMS = f"{Function.PARAMS_STRING_PREFIX}{NAME}(C1){Function.PARAMS_STRING_SUFFIX}"
	EQUATION_FORMAT = f"{NAME}\((?P<Source>[A-Z]+\d+)\)"
	PARAMS_STRING_FORMAT = f"{Function.PARAMS_STRING_PREFIX}{EQUATION_FORMAT}{Function.PARAMS_STRING_SUFFIX},SWEEPS,(?P<Sweeps>[A-Z]+\d+)"

	@property
	def Source(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Source'])
	@Source.setter
	def Source(self, value: Channel):
		self.SetParam('Source', value.__commandAddress__)
		if self.Source.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting source channel")
		
	@property
	def Sweeps(self) -> int:
		params = self.GetParams()
		return int(params['Sweeps'])
	@Sweeps.setter
	def Sweeps(self, value: int):
		self.SetParam('Sweeps', int(value))
		if self.Sweeps != value:
			raise Exception("Error while setting sweep number")

class AverageFunction(Function):
	NAME = 'AVG'
	INIT_PARAMS = f"{Function.PARAMS_STRING_PREFIX}{NAME}(C1){Function.PARAMS_STRING_SUFFIX}"
	EQUATION_FORMAT = f"{NAME}\((?P<Operand>[A-Z]+\d+)\)"
	PARAMS_STRING_FORMAT = f"{Function.PARAMS_STRING_PREFIX}{EQUATION_FORMAT}{Function.PARAMS_STRING_SUFFIX},AVERAGETYPE,CONTINUOUS,WEIGHT,(?P<Averages>\d+)"

	@property
	def Operand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Operand'])
	@Operand.setter
	def Operand(self, value: Channel):
		self.SetParam('Operand', value.__commandAddress__)
		if self.Operand.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting operand channel")

	@property
	def Averages(self) -> int:
		params = self.GetParams()
		return int(params['Averages'])
	@Averages.setter
	def Averages(self, value: int):
		self.SetParam('Averages', str(value))
		if self.Averages != value:
			raise Exception("Error while setting averages")

class PowerUnit(Enum):
	dB = 'DB'
	dBmV = 'DBMV'
	dBuV = 'DBUV'
	Watt = 'WATT'
	VRMS = 'VRMS'

class FFTType(Enum):
	Real = 'REAL'
	Imaginary = 'IMAGINARY'
	Magnitude = 'MAGNITUDE'
	Phase = 'PHASE'
	PowerSpectrum = 'POWERSPECTRUM'
	PowerDensity = 'POWERDENSITY'
class FFTWindow(Enum):
	Rectangular = 'RECTANGULAR'
	FlatTop = 'FLATTOP'
	BlackmanHarris = 'BLACKMANHARRIS'
	Hamming = 'HAMMING'
	VonHann = 'VONHANN'
class FFT(Function):
	NAME = 'FFT'
	INIT_PARAMS = f"{Function.PARAMS_STRING_PREFIX}{NAME}(C1){Function.PARAMS_STRING_SUFFIX}"
	EQUATION_FORMAT = f"{NAME}\((?P<Operand>[A-Z]+\d+)\)"
	PARAMS_STRING_FORMAT = f"{Function.PARAMS_STRING_PREFIX}{EQUATION_FORMAT}{Function.PARAMS_STRING_SUFFIX},TYPE,(?P<Type>\w+),WINDOW,(?P<Window>\w+)"

	@property
	def Type(self) -> FFTType:
		params = self.GetParams()
		return FFTType(params['Type'])
	@Type.setter
	def Type(self, value: FFTType) -> FFTType:
		self.SetParam('Type', value.value)
		if self.Type != value:
			raise Exception("Error while setting FFT type")

	@property
	def Operand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Operand'])
	@Operand.setter
	def Operand(self, value: Channel):
		self.SetParam('Operand', value.__commandAddress__)
		if self.Operand != value:
			raise Exception("Error while setting operand channel")
		
	#TODO: Add offset

	@property
	def PeaksAnnotation(self) -> bool:
		return bool(self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:STAT"))
	@PeaksAnnotation.setter
	def PeaksAnnotation(self, value: bool):
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:PEAK:STAT", str(int(value)))
		if self.PeaksAnnotation != value:
			raise Exception("Error while setting peaks annotation")

	@property
	def PeaksMinLevel(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:LEV"))
	@PeaksMinLevel.setter
	def PeaksMinLevel(self, value: float):
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:PEAK:LEV", str(value))
		if self.PeaksMinLevel != value:
			raise Exception("Error while setting peaks minimum level")

	@property
	def PeaksCount(self) -> int:
		return int(self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:COUN"))
	@PeaksCount.setter
	def PeaksCount(self, value: int):
		value = int(value)
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:PEAK:COUN", str(value))
		if self.PeaksCount != value:
			raise Exception("Error while setting peaks count")

	def GetFFTPeaks(self) -> dict:
		savedPeaksAnnotation = self.PeaksAnnotation
		self.PeaksAnnotation = True
		
		peaksFrequencies = self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:FREQ").strip('"').split(',')
		peaksFrequencies = [float(peakFrequency) for peakFrequency in peaksFrequencies if peakFrequency != '']
		peaksMagnitudes = self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:MAGN").strip('"').split(',')
		peaksMagnitudes = [float(peakMagnitude) for peakMagnitude in peaksMagnitudes if peakMagnitude != '']
		
		self.PeaksAnnotation = savedPeaksAnnotation

		return dict(zip(peaksFrequencies, peaksMagnitudes))

	@property
	def IsHorizontalScaleLogarithmic(self) -> bool:
		return True if self.__parent__.Query(f"{self.__commandAddress__}:FFT:HSC") != 'LOG' else False
	@IsHorizontalScaleLogarithmic.setter
	def IsHorizontalScaleLogarithmic(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:HSC", 'LOG' if value else 'LIN')
		if self.IsHorizontalScaleLogarithmic != value:
			raise Exception("Error while setting horizontal scale")
		return self.Span

	@property
	def Resolution(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:FFT:RES"))
	@Resolution.setter
	def Resolution(self, value: float) -> float:
		# if self.__parent__.SampledPoints == 0 and  self.__parent__.AcquiredPoints == 0:
		# 	raise Exception("Sampled points and sampling rate are both fixed to a value")
		# else:
		value = float(value)
		value = round(value/10)*10
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:RES", str(value))
		if self.Resolution != value:
			raise Exception("Error while setting frequency resolution")
		return self.Resolution
		
	@property
	def Span(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:FFT:SPAN"))
	@Span.setter
	def Span(self, value: float) -> float:
		"""Set span will change start and stop frequency"""
		value = float(value)
		value = round(value/10)*10
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:SPAN", str(value))
		if self.Span != value:
			raise Exception("Error while setting frequency span")
		return self.Span
		
	@property
	def CenterFrequency(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:FFT:FREQ"))
	@CenterFrequency.setter
	def CenterFrequency(self, value: float) -> float:
		"""Set center frequency will change start and stop frequency"""
		value = float(value)
		value = round(value/10)*10
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:FREQ", str(value))
		if self.CenterFrequency != value:
			raise Exception("Error while setting center frequency")
		return self.CenterFrequency
		
	@property
	def StopFrequency(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:FFT:STOP"))
	@StopFrequency.setter
	def StopFrequency(self, value: float) -> float:
		"""Set stop frequency will change span and center frequency"""
		value = float(value)
		value = round(value/10)*10
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:STOP", str(value))
		if self.StopFrequency != value:
			raise Exception("Error while setting stop frequency")
		return self.StopFrequency
		
	@property
	def StartFrequency(self) -> float:
		return self.StopFrequency - self.Span
	@StartFrequency.setter
	def StartFrequency(self, value: float) -> float:
		"""Set start frequency will change span and center frequency"""
		value = float(value)
		value = round(value/10)*10
		if value < self.StopFrequency: # Keep the same stop frequency by changing the span
			self.Span = self.StopFrequency - value
		self.CenterFrequency = value + (self.Span/2)
		if self.StartFrequency != value:
			raise Exception("Error while setting start frequency")
		return self.StartFrequency

	@property
	def Unit(self) -> PowerUnit:
		return PowerUnit(self.__parent__.Query(f"{self.__commandAddress__}:FFT:VUN"))
	@Unit.setter
	def Unit(self, value: PowerUnit) -> PowerUnit:
		value = PowerUnit(value)
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:VUN", str(value.value))
		if self.Unit != value:
			raise Exception("Error while setting unit")
		return self.Unit

	@property
	def Window(self) -> FFTWindow:
		params = self.GetParams()
		return FFTWindow(params['Window'])
	@Window.setter
	def Window(self, value: FFTWindow) -> FFTWindow:
		self.SetParam('Window', value.value)
		if self.Window != value:
			raise Exception("Error while setting FFT window")

FUNCTIONS_EQUATIONS = dict([(subclass.EQUATION_FORMAT, subclass) for subclass in RECURSIVE_SUBCLASSES(Function)])
from pyVirtualLab.Instruments.KeysightMSOS804A.Channels import Channel, VerticalMeasurePossibleChannel, MeasurementState
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES
from aenum import Enum
import re

class Function(VerticalMeasurePossibleChannel):
	TYPE_COMMAND_HEADER = 'FUNC'
	NAME = str()
	PARAMS_STRING_FORMAT = str()
	PARAMS = dict()

	def __init__(self, parentKeysightMSOS804A, address: str, involvedChannels: list[Channel]):
		super().__init__(parentKeysightMSOS804A, address)
		self._involvedChannels = involvedChannels

	def ChangeFunction(self, targetedFunction):
		self.__parent__.Write(f"{self.__commandAddress__}:{targetedFunction.NAME}", targetedFunction.INIT_PARAMS)

	def GetParams(self) -> dict[str, object]:
		savedReturnHeader = self.__parent__.ReturnHeader
		self.__parent__.ReturnHeader = True
		response = self.__parent__.Query(self.__commandAddress__)
		self.__parent__.ReturnHeader = savedReturnHeader
		match = re.match(f":{self.NAME} {self.PARAMS_STRING_FORMAT}", response)
		return match.groupdict()

	def SetParam(self, name: str, value: str) -> str:
		savedReturnHeader = self.__parent__.ReturnHeader
		self.__parent__.ReturnHeader = True
		response = self.__parent__.Query(self.__commandAddress__)
		self.__parent__.ReturnHeader = savedReturnHeader
		match = re.match(f":{self.NAME} {self.PARAMS_STRING_FORMAT}", response)
		currentValue = match.group(name)
		response = str(response).replace(currentValue, value)
		self.__parent__.Write(self.__commandAddress__ + response)

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
		
	@property
	def Scale(self) -> float:
		return round(float(self.__parent__.Query(f"{self.__commandAddress__}:VERT:RANG")) / 10, 7) # TODO: Check number of reticules
	@Scale.setter
	def Scale(self, value:float) -> float:
		value = round(float(value), 7)
		self.__parent__.Write(f"{self.__commandAddress__}:VERT:RANG", str(round(value * 10, 7))) # TODO: Check number of reticules
		if self.Scale != value:
			raise Exception("Error while setting scale")
	
	@property
	def Offset(self) -> float:
		return round(float(self.__parent__.Query(f"{self.__commandAddress__}:VERT:OFFS")), 6)
	@Offset.setter
	def Offset(self, value:float) -> float:
		value = round(float(value), 6)
		self.__parent__.Write(f"{self.__commandAddress__}:VERT:OFFS", str(value))
		if self.Offset != value:
			raise Exception("Error while setting offset")

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
	INIT_PARAMS = 'CHAN1'
	PARAMS_STRING_FORMAT = "(?P<Operand>[A-Z]+\d+)"

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
	NAME = 'ADD'
	INIT_PARAMS = 'CHAN1,CHAN2'
	PARAMS_STRING_FORMAT = "(?P<FirstOperand>[A-Z]+\d+)\s*,*\s*(?P<SecondOperand>[A-Z]+\d+)"

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
	NAME = 'ENV'
	INIT_PARAMS = 'CHAN1'
	PARAMS_STRING_FORMAT = "(?P<Source>[A-Z]+\d+)"

	@property
	def Source(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Source'])
	@Source.setter
	def Source(self, value: Channel):
		self.SetParam('Source', value.__commandAddress__)
		if self.Source.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting source channel")
		
class AnalogDemodulationFunction(EnvelopeFunction):
	NAME = 'ADEM'
	INIT_PARAMS = 'CHAN1'
	PARAMS_STRING_FORMAT = "(?P<Source>[A-Z]+\d+)"

	@property
	def Source(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Source'])
	@Source.setter
	def Source(self, value: Channel):
		self.SetParam('Source', value.__commandAddress__)
		if self.Source.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting source channel")

class AverageFunction(Function):
	NAME = 'AVER'
	INIT_PARAMS = 'CHAN1,2'
	PARAMS_STRING_FORMAT = "(?P<Operand>[A-Z]+\d+)\s*,*\s*(?P<Averages>\d+)"

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

class CommonModeFunction(Function):
	NAME = 'COMM'
class DifferentiateFunction(Function):
	NAME = 'DIFF'
class DivideFunction(Function):
	NAME = 'DIV'
class GateFunction(Function):
	NAME = 'GAT'

class PowerUnit(Enum):
	dB = 'DB'
	dBmV = 'DBMV'
	dBuV = 'DBUV'
	Watt = 'WATT'
	VRMS = 'VRMS'

class FFTWindow(Enum):
	Rectangular = 'RECT'
	Hanning = 'HANN'
	FlatTop = 'FLAT'
	BlackmanHarris = 'BHAR'
	Hamming = 'HAMM'
class FFTMagnitudeFunction(Function):
	NAME = 'FFTM'
	INIT_PARAMS = 'CHAN1'
	PARAMS_STRING_FORMAT = "(?P<Operand>[A-Z]+\d+)"

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
	def WindowType(self) -> FFTWindow:
		return FFTWindow(self.__parent__.Query(f"{self.__commandAddress__}:FFT:WIND"))
	@WindowType.setter
	def WindowType(self, value: FFTWindow) -> FFTWindow:
		value = FFTWindow(value)
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:WIND", str(value.value))
		if self.WindowType != value:
			raise Exception("Error while setting window type")
		return self.WindowType
	
		
class FFTPhaseFunction(Function):
	NAME = 'FFTP'
class SideFilterFunction(Function):
	INIT_PARAMS = 'CHAN1'
	PARAMS_STRING_FORMAT = "(?P<Target>[A-Z]+\d+)\s*,*\s*(?P<Bandwidth>[-+E.\d]+)"

	@property
	def Target(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Target'])
	@Target.setter
	def Target(self, value: Channel):
		self.SetParam('Target', value.__commandAddress__)
		if self.Target.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting target channel")

	@property
	def Bandwidth(self) -> float:
		params = self.GetParams()
		return float(params['Bandwidth'])
	@Bandwidth.setter
	def Bandwidth(self, value: float):
		value = float(value)
		self.SetParam('Bandwidth', str(value))
		if self.Bandwidth != value:
			raise Exception("Error while setting bandwidth")
class HighPassFunction(SideFilterFunction):
	NAME = 'HIGH'
class LowPassFunction(SideFilterFunction):
	NAME = 'LOW'
class IntegrateFunction(Function):
	NAME = 'INT'
class InvertFunction(Function):
	NAME = 'INV'
class MagnifyFunction(Function):
	NAME = 'MAGN'
class MaximumFunction(Function):
	NAME = 'MAX'
class MinimumFunction(Function):
	NAME = 'MIN'
class MultiplyFunction(Function):
	NAME = 'MULT'
class SmoothFunction(Function):
	NAME = 'SMO'
class SubtractFunction(Function):
	NAME = 'SUBT'
	INIT_PARAMS = 'CHAN1,CHAN2'
	PARAMS_STRING_FORMAT = "(?P<FirstOperand>[A-Z]+\d+)\s*,*\s*(?P<SecondOperand>[A-Z]+\d+)"

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
	@SecondOperand.setter
	def SecondOperand(self, value: Channel):
		self.SetParam('SecondOperand', value.__commandAddress__)
		if self.SecondOperand.__commandAddress__ != value.__commandAddress__:
			raise Exception("Error while setting second operand channel")
		
class VersusFunction(Function):
	NAME = 'VERS'
		
class UserDefinedFunction(Function):
	NAME = 'USER_DEF_FN'

FUNCTIONS_NAMES = dict([(subclass.NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(Function)])
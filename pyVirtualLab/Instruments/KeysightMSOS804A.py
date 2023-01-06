from enum import Enum, unique
from pyVirtualLab.VISAInstrument import Instrument
import re

@unique
class RunState(Enum):
	Stop = 0
	Single = 1
	Run = 2
   
@unique
class AcquisitionState(Enum):
	Armed = 0
	Triggered = 1
	Done = 3

@unique
class ChannelUnit(Enum):
	Volt = 0
	Ampere = 1
	Watt = 2
	Unknown = 3

class Channel():
	TYPE_COMMAND_HEADER = 'CHAN'

	def __init__(self, parentKeysightMSOS804A, address):
		self.__parent__ = parentKeysightMSOS804A
		self.__address__ = address
		self.__commandAddress__ = f"{self.TYPE_COMMAND_HEADER}{self.__address__}"

	@property
	def Address(self) -> float:
		return self.__address__

class AnalogChannel(Channel):
	@property
	def Label(self) -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:LAB?")
	@Label.setter
	def Label(self, value: str):
		value = str(value)
		if value.isascii() & len(value) <= 16:
			return self.__parent__.Write(f"{self.__commandAddress__}:LAB {value}")
		else:
			raise Exception("Label must be ASCII and less or equal 16 characters long")

	@property
	def IsEnabled(self) -> bool:
		return bool(self.__parent__.Query(f"{self.__commandAddress__}:DISP?"))
	@IsEnabled.setter
	def IsEnabled(self, value: bool):
		return self.__parent__.Write(f"{self.__commandAddress__}:DISP {int(bool(value))}")

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
	
	# Measurements
	def GetMaximum(self) -> float:
		return float(self.__parent__.Query(f"MEAS:VMAX", f"{self.__commandAddress__}"))
	def GetMinimum(self) -> float:
		return float(self.__parent__.Query(f"MEAS:VMIN", f"{self.__commandAddress__}"))
	def GetAverage(self) -> float:
		return float(self.__parent__.Query(f"MEAS:VAV", f"DISP,{self.__commandAddress__}"))
	def GetRange(self) -> float:
		return float(self.__parent__.Query(f"MEAS:VPP", f"{self.__commandAddress__}"))
	def GetFrequency(self) -> float:
		return float(self.__parent__.Query(f"MEAS:FREQ", f"{self.__commandAddress__}"))
	def GetPeriod(self) -> float:
		return float(self.__parent__.Query(f"MEAS:PER", f"{self.__commandAddress__}"))
	def GetRiseTime(self) -> float:
		return float(self.__parent__.Query(f"MEAS:RIS", f"{self.__commandAddress__}"))
	def GetFallTime(self) -> float:
		return float(self.__parent__.Query(f"MEAS:FALL", f"{self.__commandAddress__}"))

class DigitalChannel(Channel):
	TYPE_COMMAND_HEADER = 'DIG'

class Function(Channel):
	TYPE_COMMAND_HEADER = 'FUNC'
	NAME = str()
	PARAMS_STRING_FORMAT = str()
	PARAMS = dict()

	def __init__(self, parentKeysightMSOS804A, address: str, involvedChannels: list[Channel]):
		super().__init__(parentKeysightMSOS804A, address)
		self._involvedChannels = involvedChannels

	@property
	def IsEnabled(self) -> bool:
		return bool(self.__parent__.Query(f"{self.__commandAddress__}:DISP?"))
	@IsEnabled.setter
	def IsEnabled(self, value: bool):
		return self.__parent__.Write(f"{self.__commandAddress__}:DISP {int(bool(value))}")

	def ChangeFunction(self, targetedFunction):
		self.__parent__.Write(f"{self.__commandAddress__}:{targetedFunction.NAME}", targetedFunction.INIT_PARAMS)

	def GetParams(self) -> dict[str, object]:
		savedReturnHeader = self.__parent__.ReturnHeader
		self.__parent__.ReturnHeader = True
		response = self.__parent__.Query(self.__commandAddress__)
		self.__parent__.ReturnHeader = savedReturnHeader
		match = re.match(self.PARAMS_STRING_FORMAT, response)
		return match.groupdict()

	def SetParam(self, name: str, value: str) -> str:
		savedReturnHeader = self.__parent__.ReturnHeader
		self.__parent__.ReturnHeader = True
		response = self.__parent__.Query(self.__commandAddress__)
		self.__parent__.ReturnHeader = savedReturnHeader
		match = re.match(self.PARAMS_STRING_FORMAT, response)
		currentValue = match.group(name)
		response = str(response).replace(currentValue, value)
		self.__parent__.Write(self.__commandAddress__, response)

class AddFunction(Function):
	NAME = 'ADD'
	INIT_PARAMS = 'CHAN1,CHAN2'
	PARAMS_STRING_FORMAT = "(?P<Operand1>[A-Z]\d+)\s*,*\s*(?P<Operand2>[A-Z]\d+)"

	@property
	def Operand1(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Operand1'])
	@Operand1.setter
	def Operand1(self, value: Channel):
		self.SetParam(self.Operand1.__name__, value.__commandAddress__)
		if self.Operand1 != value:
			raise Exception("Error while setting operand 1 channel")
			
	@property
	def Operand2(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Operand2'])
	@Operand1.setter
	def Operand2(self, value: Channel):
		self.SetParam(self.Operand2.__name__, value.__commandAddress__)
		if self.Operand2 != value:
			raise Exception("Error while setting operand 2 channel")
class EnvelopeFunction(Function):
	NAME = 'ADEM'
	INIT_PARAMS = 'CHAN1'
	PARAMS_STRING_FORMAT = "(?P<Source>[A-Z]\d+)"

	@property
	def Source(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Source'])
	@Source.setter
	def Source(self, value: Channel):
		self.SetParam(self.Source.__name__, value.__commandAddress__)
		if self.Source != value:
			raise Exception("Error while setting source channel")

class AverageFunction(Function):
	NAME = 'AVER'
	INIT_PARAMS = 'CHAN1,2'
	PARAMS_STRING_FORMAT = "(?P<Operand>[A-Z]\d+)\s*,*\s*(?<Averages>\d+)"

	@property
	def Operand(self) -> Channel:
		params = self.GetParams()
		return self.__parent__.StringToChannel(params['Operand'])
	@Operand.setter
	def Operand(self, value: Channel):
		self.SetParam(self.Operand.__name__, value.__commandAddress__)
		if self.Operand != value:
			raise Exception("Error while setting operand channel")

	@property
	def Averages(self) -> int:
		params = self.GetParams()
		return int(params['Averages'])
	@Averages.setter
	def Averages(self, value: int):
		self.SetParam(self.Averages.__name__, str(value))
		if self.Averages != value:
			raise Exception("Error while setting averages")

class CommonModeFunction(Function):
	NAME = 'COMM'
class DifferentiateFunction(Function):
	NAME = 'DIFF'
class DivideFunction(Function):
	NAME = 'DIV'
class FFTMagnitudeFunction(Function):
	NAME = 'FFTM'
	INIT_PARAMS = 'CHAN1'
	PARAMS_STRING_FORMAT = "(?P<Operand>[A-Z]\d+)"

	@property
	def Operand(self) -> Channel:
		params = self.ParseParams()
		return self.__parent__.StringToChannel(params['Operand'])
	@Operand.setter
	def Operand(self, value: Channel):
		self.SetParam(self.Operand.__name__, value.__commandAddress__)
		if self.Operand != value:
			raise Exception("Error while setting operand channel")

	@property
	def PeaksAnnotation(self) -> bool:
		return bool(self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:STAT"))
	@PeaksAnnotation.setter
	def PeaksAnnotation(self, value: bool):
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:FFT:PEAK:STAT", str(int(value)))
		if self.PeaksMinLevel != value:
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
		
		frequencies = self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:FREQ").strip('"').split(',')
		frequencies = [float(peakFrequency) for peakFrequency in frequencies]
		magnitudes = self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:MAGN").strip('"').split(',')
		magnitudes = [float(peakMagnitude) for peakMagnitude in magnitudes]
		
		self.PeaksAnnotation = savedPeaksAnnotation

		return dict(zip(frequencies, magnitudes))
		
class FFTPhaseFunction(Function):
	NAME = 'FFTP'
class HighPassFunction(Function):
	NAME = 'HIGH'
class IntegrateFunction(Function):
	NAME = 'INT'
class InvertFunction(Function):
	NAME = 'INV'
class LowPassFunction(Function):
	NAME = 'LOW'
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
	NAME = 'SUB'
class VersusFunction(Function):
	NAME = 'VERS'

FUNCTIONS_NAMES = dict([(subclass.NAME, subclass) for subclass in Function.__subclasses__()])

class KeysightMSOS804A(Instrument):
	def __init__(self, address: str):
		super(KeysightMSOS804A, self).__init__(address)
		self.__analogChannels__ = dict()
		self.__digitalChannels__ = dict()
		self.__functions__ = dict()

	def GetAnalogData(self) -> list:
		self.Write("WAV:BYT LSBF")
		self.Write("WAV:FORM WORD")
		yIncrement = float(self.Query("WAV:YINC"))
		yOrigin = float(self.Query("WAV:YOR"))
		return [yIncrement * float(result) + yOrigin for result in self._instr.query_binary_values("WAV:DATA?", datatype='h', is_big_endian=False)]
	
	@property
	def Average(self) -> int:
		if not bool(self.Query("ACQ:AVER")):
			return 1
		else:
			return int(self.Query("ACQ:AVER:COUN"))
	@Average.setter
	def Average(self, count: int):
		if count < 2:
			self.Write("ACQ:AVER OFF")
		else:
			self.Write("ACQ:AVER:COUN " + str(int(count)))
			self.Write("ACQ:AVER ON")

	@property
	def RunState(self) -> RunState:
		match str(self.Query("RST")):
			case 'RUN':
				return RunState.Run
			case 'STOP':
				return RunState.Stop
			case 'SING':
				return RunState.Single
	@RunState.setter
	def RunState(self, runState: RunState):
		match runState:
			case RunState.Run:
				self.Write("RUN")
			case RunState.Stop:
				self.Write("STOP")
			case RunState.Single:
				self.Write("SING")

	@property
	def AcquisitionState(self) -> AcquisitionState:
		match str(self.Query("AST")):
			case 'ARM':
				return AcquisitionState.Armed
			case 'TRIG' | 'ATRIG':
				return AcquisitionState.Triggered
			case 'ADONE':
				return AcquisitionState.Done

	def AutoScale(self):
		self.Write("AUT")

	@property
	def ReturnHeader(self) -> bool:
		return bool(int(self.Query('SYST:HEAD')))
	@ReturnHeader.setter
	def ReturnHeader(self, value: bool):
		self.Write('SYST:HEAD', str(int(bool(value))))

	ANALOG_CHANNELS = 4
	@property
	def AnalogChannels(self) -> dict[int, AnalogChannel]:
		if len(self.__analogChannels__) < 1:
			for address in range(1, self.ANALOG_CHANNELS+1):
				self.__analogChannels__[address] = AnalogChannel(self, address)
		return self.__analogChannels__

	DIGITAL_CHANNELS = 16
	@property
	def DigitalChannels(self) -> dict[int, DigitalChannel]:
		if len(self.__digitalChannels__) < 1:
			for address in range(0, self.DIGITAL_CHANNELS):
				self.__digitalChannels__[address] = DigitalChannel(self, address)
		return self.__digitalChannels__

	FUNCTIONS = 16
	@property
	def Functions(self) -> dict[int, Function]:
		savedReturnHeader = self.ReturnHeader
		self.ReturnHeader = True

		for address in range(1, self.FUNCTIONS+1):
			query = f"{Function.TYPE_COMMAND_HEADER}{address}"
			response = self.Query(query).lstrip(':').split()
			params = response[1].split(',')
			channelsInvolved = [channelInvolved for channelInvolved in params if channelInvolved.startswith(AnalogChannel.TYPE_COMMAND_HEADER) or channelInvolved.startswith(DigitalChannel.TYPE_COMMAND_HEADER) or channelInvolved.startswith(Function.TYPE_COMMAND_HEADER)]
			self.__functions__[address] = FUNCTIONS_NAMES[response[0]](self, address, channelsInvolved)

		self.ReturnHeader = savedReturnHeader
		return self.__functions__

	def StringToChannel(self, value) -> Channel:
		match = re.match('([A-Z]+)(\d+)', value)
		match match.groups(0)[0]:
			case AnalogChannel.TYPE_COMMAND_HEADER:
				return self.AnalogChannels[int(match.groups(0)[1])]

			case DigitalChannel.TYPE_COMMAND_HEADER:
				return self.DigitalChannels[int(match.groups(0)[1])]

			case Function.TYPE_COMMAND_HEADER:
				return self.__functions__[int(match.groups(0)[1])]

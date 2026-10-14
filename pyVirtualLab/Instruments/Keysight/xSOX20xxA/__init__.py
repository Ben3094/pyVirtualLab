from pyVirtualLab import Instrument
from pyVirtualLab.Helpers import GetProperty, SetProperty, roundScientificNumber
from aenum import Enum
from .Functions import Function, FUNCTIONS_NAMES
from .Channels import AuxSource, LineSource, Channel, AnalogChannel, DigitalChannel, WaveformMemoryChannel, AuxSource, LineSource
from .Triggers import Trigger, TRIGGERS_NAMES
import re
from time import time, sleep
	
class RunState(Enum):
	Stop = 0
	Single = 1
	Run = 2

class AcquiringTypes(Enum):
	Normal = 'NORM'
	Average = 'AVER'
	HighResolution = 'HRES'
	Peak = 'PEAK'

DEFAULT_TIMEOUT:int = 5000

class xSOX20xxA(Instrument):
	def __init__(self, address: str):
		super(xSOX20xxA, self).__init__(address, timeout=DEFAULT_TIMEOUT)
		self.__analogChannels__ = dict()
		self.__digitalChannels__ = dict()
		self.__waveformMemoryChannels__ = dict()
		self.__functions__ = dict()
		self.__measurements__:dict[tuple[str, str], str] = dict()
		self.AuxSource:AuxSource = AuxSource()
		self.LineSource:LineSource = LineSource()

	def Wait(self, delay:float=0.01, timeout:float=5):
		def isNotAvailable():
			try: return self.Query('PDER') != '1'
			except: return True

		startTime:float = time()
		stopTime = startTime+timeout
		while (time() < stopTime) & isNotAvailable():
			sleep(delay)

	def Clear(self):
		self.Write('CDIS')

	ACQUIRING_TYPE_COMMAND:str = 'ACQ:TYPE'
	@property
	@GetProperty(AcquiringTypes, ACQUIRING_TYPE_COMMAND)
	def AcquiringType(self, getMethodReturn) -> AcquiringTypes:
		return getMethodReturn
	@AcquiringType.setter
	@SetProperty(AcquiringTypes, ACQUIRING_TYPE_COMMAND)
	def AcquiringType(self, count: AcquiringTypes):
		pass

	AVERAGE_COUNT_COMMAND:str = 'ACQ:COUN'
	@property
	@GetProperty(int, AVERAGE_COUNT_COMMAND)
	def Average(self, getMethodReturn) -> int:
		return getMethodReturn
	@Average.setter
	@SetProperty(int, AVERAGE_COUNT_COMMAND)
	def Average(self, count: int):
		pass

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
	def IsAutoTriggerEnabled(self) -> bool:
		return True if str(self.Query('TRIG:SWE')) == 'AUTO' else False
	@IsAutoTriggerEnabled.setter
	def IsAutoTriggerEnabled(self, value: bool) -> bool:
		self.Write('TRIG:SWE', 'AUTO' if value else 'TRIG')
		if self.IsAutoTriggerEnabled != value:
			raise Exception('Error while en/dis-abling auto trigger')
		return value

	def AutoScale(self):
		self.Write("AUT")

	__trigger__ = None
	@property
	def Trigger(self) -> Trigger:
		reply:str = self.Query('TRIG:MODE')
		if self.__trigger__ is not TRIGGERS_NAMES[reply]:
			if self.__trigger__:
				self.__trigger__.__parent__ = None # Unlink old trigger object
			self.__trigger__ = TRIGGERS_NAMES[reply]()
		self.__trigger__.__parent__ = self
		return self.__trigger__
	@Trigger.setter
	def Trigger(self, value:Trigger) -> Trigger:
		self.Write('TRIG:MODE', value.NAME)
		self.__trigger__ = value
		currentTrigger = self.Trigger
		if value == currentTrigger:
			raise Exception("Error while setting trigger mode")
		return currentTrigger

	@property
	@GetProperty(float, 'TIM:SCAL')
	def TimeScale(self, getMethodReturn) -> float:
		return getMethodReturn
	@TimeScale.setter
	@SetProperty(float, 'TIM:SCAL', rounding=lambda x : roundScientificNumber(x, 2))
	def TimeScale(self, value: float) -> float:
		pass

	@property
	@GetProperty(float, 'TIM:POS')
	def Delay(self, getMethodReturn) -> float:
		return getMethodReturn
	@Delay.setter
	@SetProperty(float, 'TIM:POS', rounding=lambda x : roundScientificNumber(x, 2))
	def Delay(self, value: float) -> float:
		pass

	def GetMeasurements(self) -> dict[str,float]:
		values = self.Query('MEAS:RES').split(',')
		measurements:dict = dict()
		for rowIndex in range(int(len(values)/2)):
			measurements[values.pop(0)] = float(values.pop(1))
		return measurements
	
	def DeleteMeasurements(self):
		self.Write('MEAS:CLE')
	
	@property
	def IsZoomEnabled(self) -> bool:
		return True if str(self.Query('TIM:VIEW')) == 'WIND' else False
	@IsZoomEnabled.setter
	def IsZoomEnabled(self, value: bool) -> bool:
		self.Write('TIM:VIEW', 'WIND' if value else 'MAIN')
		if self.IsZoomEnabled != value:
			raise Exception('Error while en/dis-abling horizontal zoom')
		return value

	@property
	@GetProperty(float, 'TIM:WIND:POS')
	def ZoomDelay(self, getMethodReturn) -> float:
		return getMethodReturn
	@ZoomDelay.setter
	@SetProperty(float, 'TIM:WIND:POS', rounding=lambda x : roundScientificNumber(x, 5))
	def ZoomDelay(self, value: float) -> float:
		pass
	@property
	@GetProperty(float, 'TIM:WIND:SCAL')
	def ZoomTimeScale(self, getMethodReturn) -> float:
		return getMethodReturn
	@ZoomTimeScale.setter
	@SetProperty(float, 'TIM:WIND:SCAL', rounding=lambda x : roundScientificNumber(x, 5))
	def ZoomTimeScale(self, value: float) -> float:
		pass
	
	def GetZoomedMeasurement(self, measurementIndex:int) -> bool:
		measurementIndex = int(measurementIndex)
		return True if str(self.Query('MEAS:WIND', f"MEAS{measurementIndex}")) == 'ZOOM' else False
	def SetZoomedMeasurement(self, measurementIndex:int, value:bool):
		measurementIndex = int(measurementIndex)
		self.Write('MEAS:WIND', f"{'ZOOM' if value else 'MAIN'}, MEAS{measurementIndex}")
		if self.GetZoomedMeasurement(measurementIndex) != value:
			raise Exception(f"Error while en/dis-abling measurement {measurementIndex} on zoom")
		return value

	ANALOG_CHANNELS = 4
	@property
	def AnalogChannels(self) -> dict[int, AnalogChannel]:
		if len(self.__analogChannels__) < 1:
			for address in range(1, self.ANALOG_CHANNELS+1):
				self.__analogChannels__[address] = AnalogChannel(self, address)
		return self.__analogChannels__

	WAVEFORM_MEMORIES = 2
	@property
	def WaveformMemoryChannels(self) -> dict[int, WaveformMemoryChannel]:
		if len(self.__waveformMemoryChannels__) < 1:
			for address in range(1, self.WAVEFORM_MEMORIES+1):
				self.__waveformMemoryChannels__[address] = WaveformMemoryChannel(self, address)
		return self.__waveformMemoryChannels__

	@property
	@GetProperty(float, 'ACQ:SRAT')
	def SampleRate(self, getMethodReturn) -> float:
		return getMethodReturn

	DIGITAL_CHANNELS = 16
	@property
	def DigitalChannels(self) -> dict[int, DigitalChannel]:
		if len(self.__digitalChannels__) < 1:
			for address in range(0, self.DIGITAL_CHANNELS):
				self.__digitalChannels__[address] = DigitalChannel(self, address)
		return self.__digitalChannels__

	@property
	def Function(self) -> Function:
		savedReturnHeader = self.ReturnHeader
		self.ReturnHeader = True

		query = f"{Function.TYPE_COMMAND_HEADER}"
		response = self.Query(query).lstrip(':').split()
		params = response[1].split(',')
		channelsInvolved = [channelInvolved for channelInvolved in params if channelInvolved.startswith(AnalogChannel.TYPE_COMMAND_HEADER) or channelInvolved.startswith(DigitalChannel.TYPE_COMMAND_HEADER) or channelInvolved.startswith(Function.TYPE_COMMAND_HEADER)]

		self.ReturnHeader = savedReturnHeader
		return FUNCTIONS_NAMES[response[0]](self, 0, channelsInvolved)

	def StringToChannel(self, value) -> Channel:
		match = re.match('([A-Z]+)(\d+)?', value)
		match match.groups(0)[0]:
			case AnalogChannel.TYPE_COMMAND_HEADER:
				return self.AnalogChannels[int(match.groups(0)[1])]

			case DigitalChannel.TYPE_COMMAND_HEADER:
				return self.DigitalChannels[int(match.groups(0)[1])]

			case Function.TYPE_COMMAND_HEADER:
				return self.__functions__[int(match.groups(0)[1])]

			case WaveformMemoryChannel.TYPE_COMMAND_HEADER:
				return self.WaveformMemoryChannels[int(match.groups(0)[1])]
			
			case AuxSource.TYPE_COMMAND_HEADER:
				return self.AuxSource
			
			case LineSource.TYPE_COMMAND_HEADER:
				return self.LineSource
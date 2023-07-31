from pyVirtualLab.VISAInstrument import Instrument, GetProperty, SetProperty
from aenum import Enum
from pyVirtualLab.Instruments.KeysightMSOS804A.Functions import Function, FUNCTIONS_NAMES
from pyVirtualLab.Instruments.KeysightMSOS804A.Channels import AuxSource, LineSource, Channel, AnalogChannel, DigitalChannel, WaveformMemoryChannel, AuxSource, LineSource
from pyVirtualLab.Instruments.KeysightMSOS804A.Triggers import Trigger, AdvancedTrigger, TRIGGERS_NAMES
import re
from time import time, sleep
	
class RunState(Enum):
	Stop = 0
	Single = 1
	Run = 2

class AcquisitionState(Enum):
	Armed = 0
	Triggered = 1
	Done = 3

class KeysightMSOS804A(Instrument):
	def __init__(self, address: str):
		super(KeysightMSOS804A, self).__init__(address)
		self.__analogChannels__ = dict()
		self.__digitalChannels__ = dict()
		self.__waveformMemoryChannels__ = dict()
		self.__functions__ = dict()
		self.AuxSource:AuxSource = AuxSource()
		self.LineSource:LineSource = LineSource()

	def Wait(self, delay:float=0.01, timeout:float=5):
		startTime:float = time()
		stopTime = startTime+timeout
		while (time() < stopTime) & (self.Query('PDER') != '1'):
			sleep(delay)

	def Clear(self):
		self.Write('CDIS')

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
	def IsAutoTriggerEnabled(self) -> bool:
		return True if str(self.Query('TRIG:SWE')) == 'AUTO' else False
	@IsAutoTriggerEnabled.setter
	def IsAutoTriggerEnabled(self, value: bool) -> bool:
		self.Write('TRIG:SWE', 'AUTO' if value else 'TRIG')
		if self.IsAutoTriggerEnabled != value:
			raise Exception('Error while en/dis-abling auto trigger')
		return value

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

	__trigger__ = None
	@property
	def Trigger(self) -> Trigger:
		reply:str = self.Query('TRIG:MODE')
		if reply == 'ADV':
			reply = self.Query('TRIG:ADV:MODE')
		if self.__trigger__ is not TRIGGERS_NAMES[reply]:
			if self.__trigger__:
				self.__trigger__.__parent__ = None # Unlink old trigger object
			self.__trigger__ = TRIGGERS_NAMES[reply]()
		self.__trigger__.__parent__ = self
		return self.__trigger__
	@Trigger.setter
	def Trigger(self, value:Trigger) -> Trigger:
		if value is AdvancedTrigger:
			self.Write('TRIG:ADV:MODE', value.NAME)
		else:
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
	@SetProperty(float, 'TIM:SCAL')
	def TimeScale(self, value: float) -> float:
		pass

	@property
	@GetProperty(float, 'TIM:POS')
	def Delay(self, getMethodReturn) -> float:
		return getMethodReturn
	@Delay.setter
	@SetProperty(float, 'TIM:POS')
	def Delay(self, value: float) -> float:
		pass

	@property
	@GetProperty(bool, 'MEAS:SEND')
	def SendValidMeasurements(self, getMethodReturn) -> bool:
		return getMethodReturn
	@SendValidMeasurements.setter
	@SetProperty(bool, 'MEAS:SEND')
	def SendValidMeasurements(self, value: bool) -> bool:
		pass

	ANALOG_CHANNELS = 4
	@property
	def AnalogChannels(self) -> dict[int, AnalogChannel]:
		if len(self.__analogChannels__) < 1:
			for address in range(1, self.ANALOG_CHANNELS+1):
				self.__analogChannels__[address] = AnalogChannel(self, address)
		return self.__analogChannels__

	SINGLE_OSCILLOSCOPE_MEMORIES = 4
	@property
	def WaveformMemoryChannels(self) -> dict[int, WaveformMemoryChannel]:
		if len(self.__waveformMemoryChannels__) < 1:
			for address in range(1, self.SINGLE_OSCILLOSCOPE_MEMORIES+1):
				self.__waveformMemoryChannels__[address] = WaveformMemoryChannel(self, address)
		return self.__waveformMemoryChannels__

	@property
	@GetProperty(bool, 'ACQ:SRAT:ANAL:AUTO')
	def __isAutoAnalogSampleRateEnabled__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__isAutoAnalogSampleRateEnabled__.setter
	@SetProperty(bool, 'ACQ:SRAT:ANAL:AUTO')
	def __isAutoAnalogSampleRateEnabled__(self, value: bool) -> bool:
		pass
	AUTO_SAMPLE_RATE_ENABLED_VALUE = float('inf')
	@property
	def AnalogSampleRate(self) -> float:
		if self.__isAutoAnalogSampleRateEnabled__:
			return KeysightMSOS804A.AUTO_SAMPLE_RATE_ENABLED_VALUE
		else:
			return float(self.Query('ACQ:SRAT:ANAL'))
	@AnalogSampleRate.setter
	def AnalogSampleRate(self, value: float) -> float:
		value = float(value)
		if value == KeysightMSOS804A.AUTO_SAMPLE_RATE_ENABLED_VALUE:
			self.__isAutoAnalogSampleRateEnabled__ = True
			return value
		else:
			if self.__isAutoAnalogSampleRateEnabled__ == True:
				self.__isAutoAnalogSampleRateEnabled__ = False
			self.Write('ACQ:SRAT:ANAL', str(value))
			return self.AnalogSampleRate

	DIGITAL_CHANNELS = 16
	@property
	def DigitalChannels(self) -> dict[int, DigitalChannel]:
		if len(self.__digitalChannels__) < 1:
			for address in range(0, self.DIGITAL_CHANNELS):
				self.__digitalChannels__[address] = DigitalChannel(self, address)
		return self.__digitalChannels__

	@property
	@GetProperty(bool, 'ACQ:SRAT:DIG:AUTO')
	def __isAutoDigitalSampleRateEnabled__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__isAutoDigitalSampleRateEnabled__.setter
	@SetProperty(bool, 'ACQ:SRAT:DIG:AUTO')
	def __isAutoDigitalSampleRateEnabled__(self, value: bool) -> bool:
		pass
	@property
	def DigitalSampleRate(self) -> float:
		if self.__isAutoDigitalSampleRateEnabled__:
			return KeysightMSOS804A.AUTO_SAMPLE_RATE_ENABLED_VALUE
		else:
			return float(self.Query('ACQ:SRAT:DIG'))
	@DigitalSampleRate.setter
	def DigitalSampleRate(self, value: float) -> float:
		value = float(value)
		if value == KeysightMSOS804A.AUTO_SAMPLE_RATE_ENABLED_VALUE:
			self.__isAutoDigitalSampleRateEnabled__ = True
			return value
		else:
			if self.__isAutoDigitalSampleRateEnabled__ == True:
				self.__isAutoDigitalSampleRateEnabled__ = False
			self.Write('ACQ:SRAT:DIG', str(value))
			return self.DigitalSampleRate

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
from pyVirtualLab.VISAInstrument import Instrument
from pyVirtualLab.Helpers import GetProperty, SetProperty, roundScientificNumber
from time import time, sleep
import re
from .Triggers import Trigger, TRIGGERS_NAMES
from .Channels import Source, AuxSource, LineSource, AnalogChannel, DigitalChannel, WaveformMemoryChannel
from . import Measurements as m
from .Helpers import DataFormat

DEFAULT_TIMEOUT:int = 5000

class RTB2XXX(Instrument):
	def __init__(self, address: str):
		super(RTB2XXX, self).__init__(address, timeout=DEFAULT_TIMEOUT)
		self.__analogChannels__ = dict()
		self.__digitalChannels__ = dict()
		self.__waveformMemoryChannels__ = dict()
		self.__functions__ = dict()
		self.__measurements__:dict[int, m.Measurement] = dict()
		self.AuxSource:AuxSource = AuxSource()
		self.LineSource:LineSource = LineSource()

	def Clear(self):
		self.Write('DISP:CLE')
		
	PERSISTENCE_TYPE_COMMAND:str = 'DISP:PERS:TYPE'
	PERSISTENCE_TYPE_OFF:str = 'OFF'
	PERSISTENCE_TYPE_OFF_VALUE:float = 0
	PERSISTENCE_TYPE_TIME:str = 'TIME'
	PERSISTENCE_TYPE_INFINITE:str = 'INF'
	PERSISTENCE_TYPE_INFINITE_VALUE:float = float('inf')
	PERSISTENCE_TIME_COMMAND:str = 'DISP:PERS:TIME'
	@property
	def PersistenceTime(self) -> float:
		"""
		Time (s) in which previous traces are still displayed.
		"""
		match self.Query(RTB2XXX.PERSISTENCE_TYPE_COMMAND):
			case RTB2XXX.PERSISTENCE_TYPE_OFF: return RTB2XXX.PERSISTENCE_TYPE_OFF_VALUE
			case RTB2XXX.PERSISTENCE_TYPE_INFINITE: return RTB2XXX.PERSISTENCE_TYPE_INFINITE_VALUE
			case RTB2XXX.PERSISTENCE_TYPE_TIME:
				return float(self.Query(RTB2XXX.PERSISTENCE_TIME_COMMAND))
	@PersistenceTime.setter
	def PersistenceTime(self, value:float) -> float:
		value = float(value)
		match value:
			case RTB2XXX.PERSISTENCE_TYPE_OFF_VALUE: self.Write(RTB2XXX.PERSISTENCE_TYPE_COMMAND, RTB2XXX.PERSISTENCE_TYPE_OFF)
			case RTB2XXX.PERSISTENCE_TYPE_INFINITE_VALUE: self.Write(RTB2XXX.PERSISTENCE_TYPE_COMMAND, RTB2XXX.PERSISTENCE_TYPE_INFINITE)
			case RTB2XXX.PERSISTENCE_TYPE_TIME:
				self.Write(RTB2XXX.PERSISTENCE_TYPE_COMMAND, RTB2XXX.PERSISTENCE_TYPE_TIME)
				self.Write(RTB2XXX.PERSISTENCE_TIME_COMMAND, value)
		if (self.PersistenceTime != value): raise Exception("Error while setting the persistence time")
		return value
			
	DISPLAY_MESSAGE_COMMAND:str = 'DISP:DIAL:MESS'
	def DisplayMessage(self, message:str):
		"""
		Display a message on the screen
		
		:param message: Message to be du
		:type message: str
		"""
		self.Write(RTB2XXX.DISPLAY_MESSAGE_COMMAND, str(message))
	CLEAR_MESSAGE_COMMAND:str = 'DISP:DIAL:CLOS'
	def ClearMessage(self):
		"""
		Close the message displayed on the screen
		"""
		self.Write(RTB2XXX.CLEAR_MESSAGE_COMMAND)

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

	# @property
	# def RunState(self) -> RunState:
	# 	match str(self.Query("RST")):
	# 		case 'RUN':
	# 			return RunState.Run
	# 		case 'STOP':
	# 			return RunState.Stop
	# 		case 'SING':
	# 			return RunState.Single
	# @RunState.setter
	# def RunState(self, runState: RunState):
	# 	match runState:
	# 		case RunState.Run:
	# 			self.Write("RUN")
	# 		case RunState.Stop:
	# 			self.Write("STOP")
	# 		case RunState.Single:
	# 			self.Write("SING")

	# @property
	# def AcquisitionState(self) -> AcquisitionState:
	# 	match str(self.Query("AST")):
	# 		case 'ARM':
	# 			return AcquisitionState.Armed
	# 		case 'TRIG' | 'ATRIG':
	# 			return AcquisitionState.Triggered
	# 		case 'ADONE':
	# 			return AcquisitionState.Done

	def AutoScale(self):
		self.Write("AUT")

	@property
	def ReturnHeader(self) -> bool:
		return bool(int(self.Query('SYST:HEAD')))
	@ReturnHeader.setter
	def ReturnHeader(self, value: bool):
		self.Write('SYST:HEAD', str(int(bool(value))))


	#region TRIGGER

	TRIGGER_MODE_COMMAND:str = 'TRIG:A:MODE'
	TRIGGER_MODE_AUTO:str = 'AUTO'
	TRIGGER_MODE_NORMAL:str = 'NORM'
	@property
	def IsAutoTriggerEnabled(self) -> bool:
		return True if str(self.Query(RTB2XXX.TRIGGER_MODE_COMMAND)) == RTB2XXX.TRIGGER_MODE_AUTO else False
	@IsAutoTriggerEnabled.setter
	def IsAutoTriggerEnabled(self, value: bool) -> bool:
		self.Write(RTB2XXX.TRIGGER_MODE_COMMAND, RTB2XXX.TRIGGER_MODE_AUTO if value else RTB2XXX.TRIGGER_MODE_NORMAL)
		if self.IsAutoTriggerEnabled != value:
			raise Exception('Error while en/dis-abling auto trigger')
		return value

	TRIGGER_TYPE_COMMAND:str = 'TRIG:A:TYPE'
	__trigger__ = None
	@property
	def Trigger(self) -> Trigger:
		reply:str = self.Query(RTB2XXX.TRIGGER_TYPE_COMMAND)
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

	#endregion

	#region TIME SCALE

	@property
	@GetProperty(float, 'TIM:SCAL')
	def TimeScale(self, getMethodReturn) -> float:
		return getMethodReturn
	@TimeScale.setter
	@SetProperty(float, 'TIM:SCAL', rounding=lambda x : round(roundScientificNumber(x, 2), 12))
	def TimeScale(self, value: float) -> float:
		pass

	@property
	@GetProperty(float, 'TIM:POS')
	def Delay(self, getMethodReturn) -> float:
		return getMethodReturn
	@Delay.setter
	@SetProperty(float, 'TIM:POS', rounding=lambda x : round(roundScientificNumber(x, 2), 12))
	def Delay(self, value: float) -> float:
		pass

	#endregion

	#region CHANNELS

	ANALOG_CHANNELS = 4
	@property
	def AnalogChannels(self) -> dict[int, AnalogChannel]:
		if len(self.__analogChannels__) < 1:
			for address in range(1, self.ANALOG_CHANNELS+1):
				self.__analogChannels__[address] = AnalogChannel(self, address)
		return self.__analogChannels__

	WAVEFORM_MEMORIES = 4
	@property
	def WaveformMemoryChannels(self) -> dict[int, WaveformMemoryChannel]:
		if len(self.__waveformMemoryChannels__) < 1:
			for address in range(1, self.WAVEFORM_MEMORIES+1):
				self.__waveformMemoryChannels__[address] = WaveformMemoryChannel(self, address)
		return self.__waveformMemoryChannels__

	DIGITAL_CHANNELS = 16
	@property
	def DigitalChannels(self) -> dict[int, DigitalChannel]:
		if len(self.__digitalChannels__) < 1:
			for address in range(0, self.DIGITAL_CHANNELS):
				self.__digitalChannels__[address] = DigitalChannel(self, address)
		return self.__digitalChannels__

	def StringToChannel(self, value) -> Source:
		match = re.match('([A-Z]+)(\d+)?', value)
		match match.groups(0)[0]:
			case AnalogChannel.ARGUMENT_COMMAND_HEADER:
				return self.AnalogChannels[int(match.groups(0)[1])]

			case DigitalChannel.ARGUMENT_COMMAND_HEADER:
				return self.DigitalChannels[int(match.groups(0)[1])]

			# case Function.ARGUMENT_COMMAND_HEADER:
			# 	return self.__functions__[int(match.groups(0)[1])]

			case WaveformMemoryChannel.ARGUMENT_COMMAND_HEADER:
				return self.WaveformMemoryChannels[int(match.groups(0)[1])]
			
			case AuxSource.ARGUMENT_COMMAND_HEADER:
				return self.AuxSource
			
			case LineSource.ARGUMENT_COMMAND_HEADER:
				return self.LineSource
		
	#endregion


	#region MEASUREMENTS

	MEASUREMENTS = 8
	@property
	def Measurements(self) -> dict[int, m.Measurement]:
		if len(self.__measurements__) < 1:
			for address in range(1, self.MEASUREMENTS+1):
				self.__measurements__[address] = m.Measurement(self,  address)
		return self.__measurements__

	#endregion


	#region SAMPLE RATES

	SAMPLES_NUMBER_COMMAND:str = 'ACQ:POIN'
	@property
	@GetProperty(float, SAMPLES_NUMBER_COMMAND)
	def SamplesNumber(self, getMethodReturn) ->float:
		return getMethodReturn
	@SamplesNumber.setter
	@SetProperty(float, SAMPLES_NUMBER_COMMAND)
	def SamplesNumber(self, value: float) -> float:
		pass

	AUTO_SAMPLE_RATE_COMMAND:str = 'ACQ:POIN:AUT'
	@property
	@GetProperty(bool, AUTO_SAMPLE_RATE_COMMAND)
	def __isAutoAnalogSampleRateEnabled__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__isAutoAnalogSampleRateEnabled__.setter
	@SetProperty(bool, AUTO_SAMPLE_RATE_COMMAND)
	def __isAutoAnalogSampleRateEnabled__(self, value: bool) -> bool:
		pass
	AUTO_SAMPLE_RATE_ENABLED_VALUE = float('inf')
	SAMPLE_RATE_READ_COMMAND:str = 'ACQ:SRAT'
	@property
	def SampleRate(self) -> float:
		if self.__isAutoAnalogSampleRateEnabled__:
			return RTB2XXX.AUTO_SAMPLE_RATE_ENABLED_VALUE
		else:
			return float(self.Query(RTB2XXX.SAMPLE_RATE_READ_COMMAND))/(self.TimeScale) #TODO: Add reticule number
	@SampleRate.setter
	def SampleRate(self, value: float) -> float:
		value = float(value)
		if value == RTB2XXX.AUTO_SAMPLE_RATE_ENABLED_VALUE:
			self.__isAutoAnalogSampleRateEnabled__ = True
			return value
		else:
			if self.__isAutoAnalogSampleRateEnabled__ == True:
				self.__isAutoAnalogSampleRateEnabled__ = False
			self.Write(RTB2XXX.SAMPLE_RATE_COMMAND, str(value))
			return self.SampleRate

	#endregion

	FORMAT_COMMAND:str = "FORM:DATA"
	@property
	@GetProperty(DataFormat, FORMAT_COMMAND)
	def Format(self, getMethodReturn) -> DataFormat:
		return getMethodReturn
	@Format.setter
	@SetProperty(DataFormat, FORMAT_COMMAND)
	def Format(self, value:DataFormat) -> DataFormat:
		pass
	
	BYTE_ORDER_COMMAND:str = "FORM:BORD"
	BIG_ENDIAN_BYTE_ORDER:str = 'MSBF'
	LITTLE_ENDIAN_BYTE_ORDER:str = 'LSBF'
	BYTE_ORDER_TO_BOOLEAN = lambda x: True if x == RTB2XXX.BIG_ENDIAN_BYTE_ORDER else False
	BOOLEAN_TO_BYTE_ORDER = lambda x: RTB2XXX.BIG_ENDIAN_BYTE_ORDER if x else RTB2XXX.LITTLE_ENDIAN_BYTE_ORDER
	@property
	@GetProperty(bool, BYTE_ORDER_COMMAND, BYTE_ORDER_TO_BOOLEAN)
	def IsDataBigEndian(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsDataBigEndian.setter
	@SetProperty(bool, BYTE_ORDER_COMMAND, converter=BOOLEAN_TO_BYTE_ORDER)
	def IsDataBigEndian(self, value: bool) -> bool:
		pass
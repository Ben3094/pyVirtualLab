from pyVirtualLab.VISAInstrument import Instrument
from pyVirtualLab.Helpers import GetProperty, SetProperty, roundScientificNumber
from aenum import Enum

class Channel:
	TYPE_COMMAND_HEADER:str = 'CHAN'
	__address__:int = None
	__commandAddress__:str = None
	__parent__ = None

	def __init__(self, parent, address:int):
		self.__address__ = int(address)
		self.__commandAddress__ = f"{self.TYPE_COMMAND_HEADER}{self.__address__}"
		self.__parent__ = parent

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

	SCALE_COMMAND:str = 'SCAL'
	@property
	@GetProperty(float, SCALE_COMMAND)
	def IsEnabled(self, getMethodReturn) -> float:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(float, SCALE_COMMAND)
	def IsEnabled(self, value:float) -> float:
		pass

	OFFSET_COMMAND:str = 'OFFS'
	@property
	@GetProperty(float, OFFSET_COMMAND)
	def Offset(self, getMethodReturn) -> float:
		return getMethodReturn
	@Offset.setter
	@SetProperty(float, OFFSET_COMMAND)
	def Offset(self, value:float) -> float:
		pass

class State(Enum):
	Continuous = 'RUN'
	Single = 'SING'
	Stop = 'STOP'

class Oscilloscope(Instrument):
	def __init__(self, address = None, timeout = Instrument.DEFAULT_VISA_TIMEOUT):
		super().__init__(address, timeout)
		self.__updateChannels__()

	def AutoScale(self):
		self.Write("AUT")

	def SetState(self, value:State):
		value = State(value)
		self.Write(value.value)
		# TODO: Watch event register to monitor states

	#region TIME SCALE

	TIMESCALE_COMMAND:str = 'TIM:SCAL'
	@property
	@GetProperty(float, TIMESCALE_COMMAND)
	def TimeScale(self, getMethodReturn) -> float:
		return getMethodReturn
	@TimeScale.setter
	@SetProperty(float, TIMESCALE_COMMAND, rounding=lambda x : roundScientificNumber(x, 2))
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

	#endregion


	# region CHANNEL

	__channels__:dict[int, Channel] = {}
	def __updateChannels__(self):
		index = 0
		try:
			while True:
				index = index + 1
				channel = Channel(self, index)
				channel.IsEnabled # Will fail at the channel limit
				self.__channels__[index] = channel
		except:
			return
	def Channels(self) -> dict[int, Channel]:
		return self.__channels__

	# endregion
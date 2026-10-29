from pyVirtualLab import Instrument
from pyVirtualLab.Helpers import GetProperty, SetProperty, roundScientificNumber
from aenum import Enum
from abc import ABC

class Channel(ABC):
	TYPE_COMMAND_HEADER:str = 'CHAN'

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
	def IsEnabled(self) -> bool:
		return bool(int(self.Query(self.STATE_COMMAND)))
	@IsEnabled.setter
	def IsEnabled(self, value:bool) -> bool:
		value = bool(value)
		self.Write(self.STATE_COMMAND, str(int(value)))
		if self.IsEnabled != value:
			raise Exception(f"Failed to set channel {self.__commandAddress__} state to {value}. Current state: {self.IsEnabled}")
		return value

	SCALE_COMMAND:str = 'SCAL'
	@property
	def Scale(self) -> float:
		return float(self.Query(self.SCALE_COMMAND))
	@Scale.setter
	def Scale(self, value:float) -> float:
		value = float(value)
		self.Write(self.SCALE_COMMAND, str(value))
		if self.Scale != value:
			raise Exception(f"Failed to set channel {self.__commandAddress__} scale to {value}. Current scale: {self.Scale}")
		return value

	OFFSET_COMMAND:str = 'OFFS'
	@property
	def Offset(self) -> float:
		return float(self.Query(self.OFFSET_COMMAND))
	@Offset.setter
	def Offset(self, value:float) -> float:
		value = float(value)
		self.Write(self.OFFSET_COMMAND, str(value))
		if self.Offset != value:
			raise Exception(f"Failed to set channel {self.__commandAddress__} offset to {value}. Current offset: {self.Offset}")
		return value

	@property
	def Range(self) -> float:
		return 8 * self.Scale
	@property
	def MinValue(self) -> float:
		return -(4 * self.Scale) - self.Offset
	@property
	def MaxValue(self) -> float:
		return +(4 * self.Scale) - self.Offset

class State(Enum):
	Continuous = 'RUN'
	Single = 'SING'
	Stop = 'STOP'

class Oscilloscope(Instrument, ABC):
	def __init__(self, address = None, timeout = Instrument.DEFAULT_VISA_TIMEOUT):
		super().__init__(address, timeout)

	def AutoScale(self):
		self.Write("AUT")

	def SetState(self, value:State):
		value = State(value)
		self.Write(value.value)
		# TODO: Watch event register to monitor states

	#region TIME SCALE

	TIMESCALE_COMMAND:str = 'TIM:SCAL'
	@property
	def TimeScale(self) -> float:
		return float(self.Query(self.TIMESCALE_COMMAND))
	@TimeScale.setter
	def TimeScale(self, value: float) -> float:
		value = float(value)
		self.Write(self.TIMESCALE_COMMAND, str(value))
		if self.TimeScale != value:
			raise Exception(f"Failed to set time scale to {value}. Current time scale: {self.TimeScale}")
		return value

	DELAY_COMMAND:str = 'TIM:POS'
	@property
	def Delay(self) -> float:
		return float(self.Query(self.DELAY_COMMAND))
	@Delay.setter
	def Delay(self, value: float) -> float:
		value = float(value)
		self.Write(self.DELAY_COMMAND, str(value))
		if self.Delay != value:
			raise Exception(f"Failed to set delay to {value}. Current delay: {self.Delay}")
		return value

	@property
	def TimeRange(self) -> float:
		return 10 * self.TimeScale
	@property
	def MinTimeValue(self) -> float:
		return self.Delay - 5 * self.TimeScale
	@property
	def MaxTimeValue(self) -> float:
		return self.Delay + 5 * self.TimeScale

	#endregion


	# region CHANNEL
	CHANNEL_TYPE:Type = None
	__channels__:dict[int, Channel] = {}
	def __updateChannels__(self):
		index = 0
		try:
			while True:
				index = index + 1
				channel = self.CHANNEL_TYPE(self, index)
				channel.IsEnabled # Will fail at the channel limit
				self.__channels__[index] = channel
		except:
			return
	@property
	def Channels(self) -> dict[int, Channel]:
		if len(self.__channels__) == 0:
			self.__updateChannels__()
		return self.__channels__

	# endregion
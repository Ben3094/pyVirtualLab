from aenum import Enum
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES, GetProperty, SetProperty
from .Helpers import DataFormat

class Source():
	TYPE_COMMAND_HEADER = None
	ARGUMENT_COMMAND_HEADER = None
	
	__commandAddress__:str = None

	def __init__(self):
		self.__commandAddress__ = self.TYPE_COMMAND_HEADER
		
	def __eq__(self, value):
		if hasattr(value, 'TYPE_COMMAND_HEADER'):
			return self.TYPE_COMMAND_HEADER == value.TYPE_COMMAND_HEADER
		else: return False

class AnalogSource(Source):
	TYPE_COMMAND_HEADER = 'CH'

class AuxSource(Source):
	TYPE_COMMAND_HEADER = 'EXT'

class LineSource(Source):
	TYPE_COMMAND_HEADER = 'LINE'
 
class SerialBusSource(Source):
	TYPE_COMMAND_HEADER = 'SBUS'

class DigitalSource(Source):
	TYPE_COMMAND_HEADER = 'D'

class Channel(Source):
	"""
	A channel can be displayed
	"""

	ALLOWED_SOURCES:list[type] = [AnalogSource, DigitalSource, SerialBusSource]
	TYPE_COMMAND_HEADER = 'CHAN'
	
	__parent__ = None
	__address__:str = None

	def __init__(self, parent, address):
		super().__init__()
		self.__parent__ = parent
		self.__address__ = address
		self.__commandAddress__ = f"{self.__commandAddress__}{self.__address__}"

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

	GET_WAVEFORM_COMMAND_FORMAT:str = 'CHAN{0}:DATA?'
	X_INCREMENT_COMMAND:str = 'DATA:XINC'
	Y_INCREMENT_COMMAND:str = 'DATA:YINC'
	X_ORIGIN_COMMAND:str = 'DATA:XOR'
	Y_ORIGIN_COMMAND:str = 'DATA:YOR'
	def GetWaveform(self) -> dict[float, float]:
		yIncrement = float(self.Query(Channel.Y_INCREMENT_COMMAND))
		yOrigin = float(self.Query(Channel.Y_ORIGIN_COMMAND))
		xIncrement = float(self.Query(Channel.X_INCREMENT_COMMAND))
		xOrigin = float(self.Query(Channel.X_ORIGIN_COMMAND))

		savedIsDataBigEndian = self.__parent__.IsDataBigEndian
		savedFormat = self.__parent__.Format
		self.__parent__.IsDataBigEndian = False
		self.__parent__.Format = DataFormat.UnsignedInteger32its
		savedTimeout = self.__parent__.Timeout
		self.__parent__.Timeout = 200000

		data = self.__parent__.__resource__.query_binary_values(Channel.GET_WAVEFORM_COMMAND_FORMAT.format(self.Address), datatype='L', is_big_endian=True)
		data = [yIncrement * float(result) + yOrigin for result in data]
		abscissae = range(0, len(data))
		abscissae = [xIncrement * float(abscissa) + xOrigin for abscissa in abscissae]
		data = dict(zip(abscissae, data))

		self.__parent__.Timeout = savedTimeout
		self.__parent__.IsDataBigEndian = savedIsDataBigEndian
		self.__parent__.Format = savedFormat
		return data
	
	@property
	def Scale(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:SCAL"))
	@Scale.setter
	def Scale(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:SCAL {value}")
		if self.Scale != value:
			raise Exception("Error while setting scale")
		return value
	
	@property
	def Offset(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:OFFS"))
	@Offset.setter
	def Offset(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:OFFS {value}")
		if self.Offset != value:
			raise Exception("Error while setting offset")
		return value
	
class AnalogChannel(Channel):
	NAME:str = 'CH'
	ARGUMENT_COMMAND_HEADER = 'CH'

class DigitalChannel(Channel):
	NAME:str = 'D'
	ARGUMENT_COMMAND_HEADER = 'D'

class WaveformMemoryChannel(Channel):
	NAME:str = 'W'
	ARGUMENT_COMMAND_HEADER = 'RE'
	
CHANNELS_NAMES = dict([(subclass.NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(Channel)])
from aenum import Enum
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES

class Source():
	TYPE_COMMAND_HEADER = None
	
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

	def __init__(self, parentKeysightMSOS804A, address):
		super().__init__()
		self.__parent__ = parentKeysightMSOS804A
		self.__address__ = address
		self.__commandAddress__ = f"{self.__commandAddress__}{self.__address__}"

	@property
	def Address(self) -> float:
		return self.__address__

	@property
	def IsEnabled(self) -> bool:
		return bool(int(self.__parent__.Query(f"{self.__commandAddress__}:DISP")))
	@IsEnabled.setter
	def IsEnabled(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:DISP {int(value)}")
		if self.IsEnabled != value:
			raise Exception(f"Error when en/dis-able {self.__commandAddress__}")
		return value

	def GetWaveform(self) -> dict[float, float]:
		self.__parent__.Write("WAV:SOUR", self.__commandAddress__)
		self.__parent__.Write("WAV:BYT LSBF")
		self.__parent__.Write("WAV:FORM WORD")
		yIncrement = float(self.__parent__.Query("WAV:YINC"))
		yOrigin = float(self.__parent__.Query("WAV:YOR"))
		xIncrement = float(self.__parent__.Query("WAV:XINC"))
		xOrigin = float(self.__parent__.Query("WAV:XOR"))
		savedTimeout = self.__parent__.Timeout
		self.__parent__.Timeout = 200000
		data = self.__parent__.__resource__.query_binary_values("WAV:DATA?", datatype='h', is_big_endian=False)
		data = [yIncrement * float(result) + yOrigin for result in data]
		abscissae = range(0, len(data))
		abscissae = [xIncrement * float(abscissa) + xOrigin for abscissa in abscissae]
		data = dict(zip(abscissae, data))
		self.__parent__.Timeout = savedTimeout
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

class DigitalChannel(Channel):
	NAME:str = 'D'

class WaveformMemoryChannel(Channel):
	NAME:str = 'W'
	
CHANNELS_NAMES = dict([(subclass.NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(Channel)])
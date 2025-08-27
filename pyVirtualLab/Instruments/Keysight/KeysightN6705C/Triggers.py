from re import match
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES

SOURCE_PATTERN = '([A-Z]+)(\\d+)?'

class Trigger:
	DEFAULT_NAME:str = None
	__parent__ = None
	__name__:str = None
	def __init__(self, parent) -> None:
		self.__parent__ = parent
		self.__name__ = self.DEFAULT_NAME
class BusTrigger(Trigger):
	DEFAULT_NAME:str = 'BUS'
	def __init__(self, parent) -> None:
		super().__init__(parent)
class ExtTrigger(Trigger):
	DEFAULT_NAME:str = 'EXT'
	def __init__(self, parent) -> None:
		super().__init__(parent)
class PinTrigger(Trigger):
	DEFAULT_NAME:str = 'PIN'
	PIN_INDEX_PATTERN:str = DEFAULT_NAME + f"{0}"
	def __init__(self, parent) -> None:
		super().__init__(parent)
	__pin__:int = None
	@property
	def Pin(self) -> int:
		reply:str = self.__parent__.__parent__.Query('TRIG:ACQ:SOUR', f"(@{self.__parent__.Address})")
		return float(match(PinTrigger.PIN_INDEX_PATTERN.format('(\\d+)'), reply)[1])
	@Pin.setter
	def Pin(self, value:int) -> int:
		value = int(value)
		value = PinTrigger.PIN_INDEX_PATTERN.format(str(value))
		self.__parent__.__parent__.Query('TRIG:ACQ:SOUR', f"{value}, (@{self.__parent__.Address})")
		if self.Pin != value:
			raise Exception("Error while setting trigger pin")

class OutputTrigger(Trigger):
	OUTPUT_INDEX_PATTERN:str = None
	__defautOutputIndex__:int = None
	def __init__(self, parent) -> None:
		super().__init__(parent)
		self.OUTPUT_INDEX_PATTERN:str = self.DEFAULT_NAME + "{0}"
		self.__defautOutputIndex__ = self.__parent__.Address
		self.__name__ = self.OUTPUT_INDEX_PATTERN.format(self.__defautOutputIndex__)
	__output__ = None
	@property
	def Output(self):
		if not self.__output__:
			self.__output__ = self.__parent__.__parent__.Outputs[self.__defautOutputIndex__]
		else:
			reply = self.__parent__.__parent__.Query('TRIG:ACQ:SOUR', f"(@{self.__parent__.Address})")
			self.__output__ = self.__parent__.__parent__.Outputs[int(match(self.OUTPUT_INDEX_PATTERN.format('(\\d+)'), reply)[1])]
		return self.__output__
	@Output.setter
	def Output(self, value):
		self.__name__ = self.OUTPUT_INDEX_PATTERN.format(value.Address)
		self.__parent__.__parent__.Write('TRIG:ACQ:SOUR', f"{self.__name__}, (@{self.__parent__.Address})")
		print(self.Output.Address)
		print(value.Address)
		if self.Output.Address != value.Address:
			raise Exception("Error while setting triggering output")
		return value
	@property
	def Level(self) -> float:
		return float(self.__parent__.__parent__.Query(f"TRIG:ACQ:{self.DEFAULT_NAME}, (@{self.__parent__.Address})"))
	@Level.setter
	def Level(self, value: float) -> float:
		value = float(value)
		self.__parent__.__parent__.Write(f"TRIG:ACQ:{self.DEFAULT_NAME}", f"{value}, (@{self.__parent__.Address})")
		if self.TriggeringVoltage != value:
			raise Exception("Error while setting the triggering level")
		return value
	TRIGGERING_POSITIVE_SLOPE_HEADER = 'POS'
	TRIGGERING_NEGATIVE_SLOPE_HEADER = 'NEG'
	@property
	def IsSlopePositive(self) -> bool:
		return self.__parent__.__parent__.Query(f"TRIG:ACQ:{self.DEFAULT_NAME}:SLOP", f"(@{self.__parent__.Address})") == OutputTrigger.TRIGGERING_POSITIVE_SLOPE_HEADER
	@IsSlopePositive.setter
	def IsSlopePositive(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.__parent__.Write(f"TRIG:ACQ:{self.DEFAULT_NAME}:SLOP", f"{OutputTrigger.TRIGGERING_POSITIVE_SLOPE_HEADER if value else OutputTrigger.TRIGGERING_NEGATIVE_SLOPE_HEADER}, (@{self.__parent__.Address})")
		if self.IsSlopePositive != value:
			raise Exception("Error while setting trigger slope direction")
		return value
class CurrentTrigger(OutputTrigger):
	DEFAULT_NAME:str = 'CURR'
	def __init__(self, parent) -> None:
		super().__init__(parent)
class VoltageTrigger(OutputTrigger):
	DEFAULT_NAME:str = 'VOLT'
	def __init__(self, parent) -> None:
		super().__init__(parent)
class TransientTrigger(OutputTrigger):
	DEFAULT_NAME:str = 'TRAN'
	def __init__(self, parent) -> None:
		super().__init__(parent)

NAMES = dict([(subclass.DEFAULT_NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(Trigger)])
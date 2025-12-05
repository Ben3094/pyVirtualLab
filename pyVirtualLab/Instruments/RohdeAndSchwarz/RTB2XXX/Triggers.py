from aenum import Enum
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES
from . import Channels
from .Channels import AnalogSource, AuxSource, DigitalSource, SerialBusSource, LineSource

class Trigger:
	NAME:str = None	
	ALLOWED_SOURCES:list[type] = [] #TODO: search for allowed sources as they are not documented
	__parent__ = None

	@property
	def Source(self) -> Channels.Source:
		return self.__parent__.StringToChannel(self.__parent__.Query(f"TRIG:{self.NAME}:SOUR"))
	@Source.setter
	def Source(self, value: Channels.Source) -> Channels.Source:
		if not type(value) in self.ALLOWED_SOURCES:
			raise Exception("Source type is not allowed")
		self.__parent__.Write(f"TRIG:{self.NAME}:SOUR", value.__commandAddress__)
		if self.Source != value:
			raise Exception("Error while setting source")
		return value

class EdgeTrigger(Trigger):
	NAME:str = 'EDGE'
	ALLOWED_SOURCES:list[type] = [AnalogSource, AuxSource, DigitalSource]

class WidthTrigger(Trigger):
	NAME:str = 'WIDT'
	ALLOWED_SOURCES:list[type] = [AnalogSource]

class TVTrigger(Trigger):
	NAME:str = 'TV'
	ALLOWED_SOURCES:list[type] = [AnalogSource]

class LogicTrigger(Trigger):
	NAME:str = 'LOG'
	ALLOWED_SOURCES:list[type] = [AnalogSource]

class RuntTrigger(Trigger):
	NAME:str = 'RUNT'
	ALLOWED_SOURCES:list[type] = [AnalogSource]

class RiseTimeTrigger(Trigger):
	NAME:str = 'RIS'
	ALLOWED_SOURCES:list[type] = [AnalogSource]

class TimeoutTrigger(Trigger):
	NAME:str = 'TIM'
	ALLOWED_SOURCES:list[type] = [AnalogSource]

class BusTrigger(Trigger):
	NAME:str = 'BUS'
	ALLOWED_SOURCES:list[type] = [SerialBusSource]

class LineTrigger(Trigger):
	NAME:str = 'LINE'
	ALLOWED_SOURCES:list[type] = [LineSource]

TRIGGERS_NAMES = dict([(subclass.NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(Trigger)])
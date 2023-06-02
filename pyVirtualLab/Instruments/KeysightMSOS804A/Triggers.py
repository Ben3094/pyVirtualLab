from aenum import enum
from pyVirtualLab.Instruments.KeysightMSOS804A.Channels import Channel, AnalogChannel, DigitalChannel

class Trigger:
	NAME:str = None
	
	__parent__ = None

class SourcedTrigger(Trigger):
	ALLOWED_SOURCES:list[type] = []
	
	@property
	def Source(self) -> Channel:
		return self.__parent__.StringToChannel(self.__parent__.Query(f"TRIG:{self.NAME}:SOUR"))
	@Source.setter
	def Source(self, value: Channel) -> Channel:
		if not type(value) in self.ALLOWED_SOURCES:
			raise Exception("Channel type is not allowed")
		self.Write(f"TRIG:{self.NAME}:SOUR", value.__commandAddress__)
		if self.Source != value:
			raise Exception("Error while setting source")
		return value

class AdvancedTrigger(Trigger):
	pass

class CommunicationSerialPatternTrigger(SourcedTrigger):
	NAME:str = 'COMM'
	ALLOWED_SOURCES:list[type] = [AnalogChannel]

	@property
	def IsReturnToZeroLineCode(self) -> bool:
		return True if self.__parent__.Query('TRIG:COMM:ENC') == 'RZ' else False
	@IsReturnToZeroLineCode.setter
	def IsReturnToZeroLineCode(self, value: bool) -> bool:
		self.__parent__.Write('TRIG:COMM:ENC', 'RZ' if value else 'NRZ')
		if self.IsReturnToZeroLineCode != value:
			raise Exception('Error while en/dis-abling Return-to-Zero line code')
		return value
	
	@property
	def Pattern(self) -> list[int]:
		return [int(bit) for bit in self.__parent__.Query('TRIG:COMM:PATT').split(',')]
	@Pattern.setter
	def Pattern(self, value: list[int]) -> list[int]:
		value = [-1 if bit < 0 else (1 if bit > 0 else 0) for bit in value]
		self.__parent__.Write('TRIG:COMM:PATT', ','.join([str(bit) for bit in value]))
		if self.Pattern != value:
			raise Exception("Error while setting pattern")
		return value
	
	@property
	def IsPolarityNegative(self) -> bool:
		return True if self.__parent__.Query('TRIG:COMM:POL') == 'NEG' else False
	@IsPolarityNegative.setter
	def IsPolarityNegative(self, value: bool) -> bool:
		self.__parent__.Write('TRIG:COMM:POL', 'NEG' if value else 'POS')
		if self.IsPolarityNegative != value:
			raise Exception('Error while en/dis-abling polarity')
		return value

class DelayTrigger(Trigger):
	NAME:str = 'DEL'

class EdgeCoupling(enum):
	AC = 'AC'
	DC = 'DC'
	LowFrequencyReject = 'LFR'
	HighFrequencyReject = 'HFR'
class EdgeSlope(enum):
	Positive = 'POS'
	Negative = 'NEG'
	Either = 'EITH'
class EdgeTrigger(SourcedTrigger):
	NAME:str = 'EDGE'
	ALLOWED_SOURCES:list[type] = [AnalogChannel, DigitalChannel] # TODO: add Aux and Line

	@property
	def Coupling(self) -> EdgeCoupling:
		return EdgeCoupling(self.__parent__.Query('TRIG:EDGE:COUP'))
	@Coupling.setter
	def Coupling(self, value: EdgeCoupling) -> EdgeCoupling:
		value = EdgeCoupling(value)
		self.__parent__.Write('TRIG:EDGE:COUP', value.value)
		if self.Coupling != value:
			raise Exception("Error while setting edge coupling")
		return value
	
	@property
	def Slope(self) -> EdgeSlope:
		return EdgeSlope(self.__parent__.Query('TRIG:EDGE:SLOP'))
	@Slope.setter
	def Slope(self, value: EdgeSlope) -> EdgeSlope:
		value = EdgeSlope(value)
		self.__parent__.Write('TRIG:EDGE:SLOP', value.value)
		if self.Slope != value:
			raise Exception("Error while setting edge slope")
		return value
class GlitchTrigger(SourcedTrigger):
	NAME:str = 'GLIT'
	ALLOWED_SOURCES:list[type] = [AnalogChannel, DigitalChannel]
class PatternTrigger(Trigger):
	NAME:str = 'PATT'
class PulseWidthTrigger(SourcedTrigger):
	NAME:str = 'PWID'
	ALLOWED_SOURCES:list[type] = [AnalogChannel, DigitalChannel]
class RuntTrigger(SourcedTrigger):
	NAME:str = 'RUNT'
	ALLOWED_SOURCES:list[type] = [AnalogChannel]

class SerialBusTrigger(Trigger):
	pass
class SerialBus1Trigger(SerialBusTrigger):
	NAME:str = 'SBUS1'
class SerialBus2Trigger(SerialBusTrigger):
	NAME:str = 'SBUS2'
class SerialBus3Trigger(SerialBusTrigger):
	NAME:str = 'SBUS3'
class SerialBus4Trigger(SerialBusTrigger):
	NAME:str = 'SBUS4'
	
class SequenceTrigger(Trigger):
	NAME:str = 'SEQ'
class SetupAndHoldTrigger(SourcedTrigger):
	NAME:str = 'SHOL'
	ALLOWED_SOURCES:list[type] = [AnalogChannel]
class StateTrigger(SourcedTrigger):
	NAME:str = 'STAT'
	ALLOWED_SOURCES:list[type] = [AnalogChannel, DigitalChannel]
class TimeoutTrigger(SourcedTrigger):
	NAME:str = 'TIM'
	ALLOWED_SOURCES:list[type] = [AnalogChannel]
class TransitionTrigger(SourcedTrigger):
	NAME:str = 'TRAN'
	ALLOWED_SOURCES:list[type] = [AnalogChannel]
class TVTrigger(SourcedTrigger):
	NAME:str = 'TV'
	ALLOWED_SOURCES:list[type] = [AnalogChannel]
class WindowTrigger(SourcedTrigger):
	NAME:str = 'WIND'
	ALLOWED_SOURCES:list[type] = [AnalogChannel]
class ViolationTrigger(AdvancedTrigger):
	NAME:str = 'VIOL'

TRIGGERS_NAMES = dict([(subclass.NAME, subclass) for subclass in Trigger.__subclasses__()])
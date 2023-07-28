from aenum import enum
import pyVirtualLab.Instruments.KeysightMSOS804A.Channels as Channels
from Channels import AuxSource, LineSource, AnalogChannel, DigitalChannel

class Trigger:
	NAME:str = None
	
	__parent__ = None

class SourcedTrigger(Trigger):
	ALLOWED_SOURCES:list[type] = []
	
	@property
	def Source(self) -> Channels.Source:
		return self.__parent__.StringToChannel(self.__parent__.Query(f"TRIG:{self.NAME}:SOUR"))
	@Source.setter
	def Source(self, value: Channels.Source) -> Channels.Source:
		if not type(value) in self.ALLOWED_SOURCES:
			raise Exception("Source type is not allowed")
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
	ALLOWED_SOURCES:list[type] = [AnalogChannel, DigitalChannel, AuxSource, LineSource]

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


class SequenceResetCondition:
	NAME:str = None
	__parent__ = None
	def __init__(self, parentSequenceTrigger) -> None:
		self.__parent__ = parentSequenceTrigger
class ChannelLogicalCondition(enum):
	High = 'HIGH'
	Low = 'LOW'
	Any = 'DONT'
class ChannelsResetCondition(SequenceResetCondition):
	NAME:str = 'EVEN'

	@property
	def ChannelsLogicalConditions(self) -> dict[AnalogChannel, ChannelLogicalCondition]:
		values = dict()
		for channel in self.__parent__.__parent.AnalogChannels.values():
			values[channel] = ChannelLogicalCondition(self.__parent__.__parent__.Query('TRIG:SEQ:RES:EVEN', channel.__commandAddress__))
		return values
	@ChannelsLogicalConditions.setter
	def ChannelsLogicalConditions(self, values:dict[AnalogChannel, ChannelLogicalCondition]) -> dict[AnalogChannel, ChannelLogicalCondition]:
		forbiddenChannel = list()
		if self.__parent__.FirstTrigger is SourcedTrigger:
			forbiddenChannel.append(self.__parent__.FirstTrigger.Source)
		if self.__parent__.SecondTrigger is SourcedTrigger:
			forbiddenChannel.append(self.__parent__.SecondTrigger.Source)
		for channel in values:
			if channel in forbiddenChannel:
				raise Exception(f"Channel {channel.__Address__} is already an event source")
		for channel in values:
			self.__parent__.__parent__.Write(f"TRIG:SEQ:RES:EVEN {channel.__commandAddress__}", values[channel].value)

class TimeResetCondition(SequenceResetCondition):
	NAME:str = 'TIME'

	@property
	def TimeLeft(self) -> float:
		return float(self.__parent__.__parent__.Query('TRIG:SEQ:RES:TIME'))
	@TimeLeft.setter
	def TimeLeft(self, value:float) -> float:
		value = float(value)
		self.__parent__.__parent__.Write('TRIG:SEQ:RES:TIME', value)
		if self.TimeLeft != value:
			raise Exception("Error while setting max time until reset")
		return value

class SequenceTrigger(Trigger):
	NAME:str = 'SEQ'
	ALLOWED_TRIGGER_TYPES = [EdgeTrigger, GlitchTrigger, PulseWidthTrigger, PatternTrigger, RuntTrigger, SetupAndHoldTrigger, StateTrigger, TimeoutTrigger, TransitionTrigger, WindowTrigger]

	@property
	def __isDelayEnabled__(self) -> bool:
		return bool(int(self.__parent__.Query('TRIG:SEQ:WAIT:ENAB')))
	@__isDelayEnabled__.setter
	def __isDelayEnabled__(self, value: bool):
		value = bool(value)
		self.__parent__.Write('TRIG:SEQ:WAIT:ENAB', str(int(value)))
		if self.__isDelayEnabled__ != value:
			raise Exception("Error while en/dis-abling delay between sequence events")
	@property
	def MinDelayBetweenEvents(self) -> float:
		if self.__isDelayEnabled__:
			return float(self.__parent__.Query('TRIG:SEQ:WAIT:TIME'))
		else:
			return 0
	@MinDelayBetweenEvents.setter
	def MinDelayBetweenEvents(self, value: float) -> float:
		value = float(value)
		if value < 0:
			value = 0
		if value == 0:
			self.__isDelayEnabled__ = False
		else:
			self.__isDelayEnabled__ = True
			self.__parent__.Write('TRIG:SEQ:WAIT:TIME', str(value))
		if self.MinDelayBetweenEvents != value:
			raise Exception("Error while setting sequenced triggers delay")
		return value
	
	__resetCondition__: SequenceResetCondition = None	
	@property
	def ResetCondition(self) -> SequenceResetCondition:
		type = TimeResetCondition if self.__parent__.Query('TRIG:SEQ:RES:TYPE') == TimeResetCondition.NAME else ChannelsResetCondition
		if not self.__resetCondition__ is type:
			self.__resetCondition__ = type(self)
		return self.__resetCondition__
	def ChangeResetCondition(self, resetCondition: type) -> SequenceResetCondition:
		if self.ResetCondition != resetCondition:
			if self.ResetCondition is SequenceResetCondition:
				self.ResetCondition.__parent__ = None
			self.__resetCondition__ = resetCondition(self)
			self.__parent__.__parent__.Write('TRIG:SEQ:RES:TYPE', self.NAME)
		return self.ResetCondition

	# TODO: Deal with limitations
	__triggers__:tuple[Trigger,Trigger] = dict(zip([1,2], [None, None]))
	def __changeTrigger__(self, newTriggerType:type, address:float) -> Trigger:
		if not newTriggerType in self.ALLOWED_TRIGGER_TYPES:
			raise Exception(f"{newTriggerType.__name__} not allowed in sequence")
		if not self.__triggers__[address] is newTriggerType:
			self.__parent__.Write(f"TRIG:SEQ:TERM{address}", newTriggerType.NAME)
			if self.__triggers__[address] is Trigger:
				self.__triggers__[address].__parent__ = None
			self.__triggers__[address] = newTriggerType()
			self.__triggers__[address].__parent__ = self
			self.__triggers__[address].NAME = self.__triggers__[address].NAME + str(address)
		return self.__triggers__[address]
	def __getTrigger__(self, address:float) -> Trigger:
		newTriggerType = TRIGGERS_NAMES[self.__parent__.Query(f"TRIG:SEQ:TERM{address}").rstrip(str(address))]
		return self.__changeTrigger__(newTriggerType, address)
	
	@property
	def FirstTrigger(self) -> Trigger:
		return self.__getTrigger__(1)
	def ChangeFirstTrigger(self, triggerType:type) -> Trigger:
		return self.__changeTrigger__(triggerType, 1)
	@property
	def SecondTrigger(self) -> Trigger:
		return self.__getTrigger__(2)
	def ChangeSecondTrigger(self, triggerType:type) -> Trigger:
		return self.__changeTrigger__(triggerType, 2)

TRIGGERS_NAMES = dict([(subclass.NAME, subclass) for subclass in Trigger.__subclasses__()])
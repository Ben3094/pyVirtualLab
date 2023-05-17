class Trigger:
	NAME:str = None
	
	__parent__ = None

class AdvancedTrigger(Trigger):
	pass

class CommunicationSerialPatternTrigger(Trigger):
	NAME:str = 'COMM'
class DelayTrigger(Trigger):
	NAME:str = 'DEL'
class EdgeTrigger(Trigger):
	NAME:str = 'EDGE'
class GlitchTrigger(Trigger):
	NAME:str = 'GLIT'
class PatternTrigger(Trigger):
	NAME:str = 'PATT'
class PulseWidthTrigger(Trigger):
	NAME:str = 'PWID'
class RuntTrigger(Trigger):
	NAME:str = 'RUNT'

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
class SetupAndHoldTrigger(Trigger):
	NAME:str = 'SHOL'
class StateTrigger(Trigger):
	NAME:str = 'STAT'
class TimeoutTrigger(Trigger):
	NAME:str = 'TIM'
class TransitionTrigger(Trigger):
	NAME:str = 'TRAN'
class TVTrigger(Trigger):
	NAME:str = 'TV'
class WindowTrigger(Trigger):
	NAME:str = 'WIND'
class ViolationTrigger(AdvancedTrigger):
	NAME:str = 'VIOL'

TRIGGERS_NAMES = dict([(subclass.NAME, subclass) for subclass in Trigger.__subclasses__()])
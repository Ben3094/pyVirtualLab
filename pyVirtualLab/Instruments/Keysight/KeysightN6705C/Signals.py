from aenum import Flag, unique, Enum
from abc import ABC
from pyVirtualLab.Helpers import GetProperty, SetProperty, RECURSIVE_SUBCLASSES

@unique
class SignalType(Enum):
	Voltage = 'VOLT'
	Current = 'CURR'

class Signal(ABC):
	DEFAULT_NAME:str = 'NONE'
	__parent__ = None
	__name__:str = None
	__type__:SignalType = None
	def __init__(self, parentOutput, type:SignalType=SignalType.Voltage):
		self.__parent__ = parentOutput
		self.__name__ = self.DEFAULT_NAME
		self.__type__ = type
	
	def Read(self) -> str:
		return self.__parent__.__parent__.Read()
	def Write(self, command:str, arguments:str='') -> str:
		return self.__parent__.__parent__.Write(command, arguments + f", (@{self.__parent__.__address__})")
	def Query(self, command:str, arguments:str='') -> str:
		return self.__parent__.__parent__.Query(command, ('' if arguments == '' else (arguments + ', ')) + f"(@{self.__parent__.__address__})")

	TYPE_COMMAND:str = "SOUR:ARB:FUNC:TYPE"
	@property
	@GetProperty(SignalType, TYPE_COMMAND)
	def Type(self, getMethodReturn) -> SignalType:
		return getMethodReturn
	@Type.setter
	@SetProperty(SignalType, TYPE_COMMAND)
	def Type(self, value:SignalType) -> SignalType:
		self.__type__ = value

	KEEP_LAST_VALUE_COMMAND:str = "SOUR:ARB:TERM:LAST"
	@property
	@GetProperty(bool, KEEP_LAST_VALUE_COMMAND)
	def KeepLastValue(self, getMethodReturn) -> bool:
		return getMethodReturn
	@KeepLastValue.setter
	@SetProperty(bool, KEEP_LAST_VALUE_COMMAND)
	def KeepLastValue(self, value:bool) -> bool:
		pass

class ConstantSignal(Signal):
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput)
class StepSignal(Signal):
	DEFAULT_NAME:str = 'STEP'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput)
class RampSignal(Signal):
	DEFAULT_NAME:str = 'RAMP'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput) 
class StaircaseSignal(Signal):
	DEFAULT_NAME:str = 'STA'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput) 
class SinusoidSignal(Signal):
	DEFAULT_NAME:str = 'SIN'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput) 
class PulseSignal(Signal):
	DEFAULT_NAME:str = 'PULS'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput)

	LOW_VOLTAGE_COMMAND:str = "SOUR:ARB:VOLT:PULS:STAR:LEV"
	@property
	@GetProperty(float, LOW_VOLTAGE_COMMAND)
	def LowVoltage(self, getMethodReturn) -> float:
		return getMethodReturn
	@LowVoltage.setter
	@SetProperty(float, LOW_VOLTAGE_COMMAND)
	def LowVoltage(self, value:float) -> float:
		pass
	HIGH_VOLTAGE_COMMAND:str = "SOUR:ARB:VOLT:PULS:TOP:LEV"
	@property
	@GetProperty(float, HIGH_VOLTAGE_COMMAND)
	def HighVoltage(self, getMethodReturn) -> float:
		return getMethodReturn
	@HighVoltage.setter
	@SetProperty(float, HIGH_VOLTAGE_COMMAND)
	def HighVoltage(self, value:float) -> float:
		pass

	WAITING_TIME_COMMAND:str = "SOUR:ARB:VOLT:PULS:STAR:TIM"
	@property
	@GetProperty(float, WAITING_TIME_COMMAND)
	def WaitingTime(self, getMethodReturn) -> float:
		return getMethodReturn
	@WaitingTime.setter
	@SetProperty(float, WAITING_TIME_COMMAND)
	def WaitingTime(self, value:float) -> float:
		pass
	PULSE_TIME_COMMAND:str = "SOUR:ARB:VOLT:PULS:TOP:TIM"
	@property
	@GetProperty(float, PULSE_TIME_COMMAND)
	def PulseTime(self, getMethodReturn) -> float:
		return getMethodReturn
	@PulseTime.setter
	@SetProperty(float, PULSE_TIME_COMMAND)
	def PulseTime(self, value:float) -> float:
		pass
	END_TIME_COMMAND:str = "SOUR:ARB:VOLT:PULS:END:TIM"
	@property
	@GetProperty(float, END_TIME_COMMAND)
	def EndTime(self, getMethodReturn) -> float:
		return getMethodReturn
	@EndTime.setter
	@SetProperty(float, END_TIME_COMMAND)
	def EndTime(self, value:float) -> float:
		pass
	
class TrapezoidSignal(Signal):
	DEFAULT_NAME:str = 'TRAP'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput) 
class ExponentialSignal(Signal):
	DEFAULT_NAME:str = 'EXP'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput) 
class UserDefinedSignal(Signal):
	DEFAULT_NAME:str = 'UDEF'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput) 
class ConstantDwellSignal(Signal):
	DEFAULT_NAME:str = 'CDW'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput) 
class SequenceSignal(Signal):
	DEFAULT_NAME:str = 'SEQ'
	def __init__(self, parentOutput) -> None:
		super().__init__(parentOutput)

NAMES = dict([(subclass.DEFAULT_NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(Signal)])
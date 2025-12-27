from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES, GetProperty, SetProperty

FUNCTION_COMMAND:str = 'FUNC'

class Function:
	NAME:str = None
	__parent__ = None

	def Read(self) -> str:
		return self.__parent__.Read()
	def Write(self, command:str, arguments:str='') -> str:
		return self.__parent__.Write(f"{FUNCTION_COMMAND}:{self.NAME}:{command}", arguments)
	def Query(self, command:str, arguments:str='') -> str:
		return self.__parent__.Query(f"{FUNCTION_COMMAND}:{self.NAME}:{command}", arguments)

class SineFunction(Function):
	NAME:str = 'SIN'

class SquareFunction(Function):
	NAME:str = 'SQU'

	DUTY_CYCLE_COMMAND:str = 'DCYC'
	@property
	@GetProperty(float, DUTY_CYCLE_COMMAND)
	def DutyCycle(self, getMethodReturn) -> float:
		return getMethodReturn
	@DutyCycle.setter
	@SetProperty(float, DUTY_CYCLE_COMMAND)
	def DutyCycle(self, value:float) -> float:
		pass

class RampFunction(Function):
	NAME:str = 'RAMP'

	SYMMETRY_COMMAND:str = 'SYMM'
	@property
	@GetProperty(float, SYMMETRY_COMMAND)
	def Symmetry(self, getMethodReturn) -> float:
		return getMethodReturn
	@Symmetry.setter
	@SetProperty(float, SYMMETRY_COMMAND)
	def Symmetry(self, value:float) -> float:
		pass

class PulseFunction(Function):
	NAME:str = 'PULS'

	PERIOD_COMMAND:str = 'PULS:PER'
	@property
	def Period(self) -> float:
		return float(self.__parent__.Query(PulseFunction.PERIOD_COMMAND))
	@Period.setter
	def Period(self, value:float) -> float:
		value = float(value)
		self.__parent__.Write(PulseFunction.PERIOD_COMMAND, str(value))
		if self.Period != value:
			raise Exception('Error while setting pulse period')
		return value

	PULSE_WIDTH_HOLD_COMMAND:str = 'HOLD'
	PULSE_WIDTH_HOLD:str = 'WIDT'
	DUTY_CYCLE_HOLD:str = 'DCYC'
	@property
	def IsWidtHoldWithPeriod(self) -> bool:
		return True if self.Query(PulseFunction.PULSE_WIDTH_HOLD_COMMAND) == PulseFunction.PULSE_WIDTH_HOLD else False
	@IsWidtHoldWithPeriod.setter
	def IsWidtHoldWithPeriod(self, value:bool) -> bool:
		value = bool(value)
		self.Write(PulseFunction.PULSE_WIDTH_HOLD_COMMAND, PulseFunction.PULSE_WIDTH_HOLD if value else PulseFunction.DUTY_CYCLE_HOLD)
		if self.IsWidtHoldWithPeriod != value:
			raise Exception('Error while setting the hold parameter')
		return value

	WIDTH_COMMAND:str = 'WIDT'
	@property
	@GetProperty(float, WIDTH_COMMAND)
	def Width(self, getMethodReturn) -> float:
		return getMethodReturn
	@Width.setter
	@SetProperty(float, WIDTH_COMMAND)
	def Width(self, value:float) -> float:
		pass

	DUTY_CYCLE_COMMAND:str = 'DCYC'
	@property
	@GetProperty(float, DUTY_CYCLE_COMMAND)
	def DutyCycle(self, getMethodReturn) -> float:
		return getMethodReturn
	@DutyCycle.setter
	@SetProperty(float, DUTY_CYCLE_COMMAND)
	def DutyCycle(self, value:float) -> float:
		pass

	EDGE_TIME_COMMAND:str = 'TRAN'
	@property
	@GetProperty(float, EDGE_TIME_COMMAND)
	def EdgeTime(self, getMethodReturn) -> float:
		return getMethodReturn
	@EdgeTime.setter
	@SetProperty(float, EDGE_TIME_COMMAND)
	def EdgeTime(self, value:float) -> float:
		pass

class NoiseFunction(Function):
	NAME:str = 'NOIS'

class DCFunction(Function):
	NAME:str = 'DC'

class ArbitraryFunction(Function):
	NAME:str = 'USER'

FUNCTIONS_NAMES = dict([(subclass.NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(Function)])
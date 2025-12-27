from aenum import Enum
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES, GetProperty, SetProperty

class Function(Enum):
	Sinusoid = 'SIN'
	Square = 'SQU'
	PositiveRamp = 'RAMP'
	NegativeRamp = 'NRAM'
	Triangle = 'TRI'
	Noise = 'NOIS'
	User = 'USER'

class Modulation:
	NAME:str = None
	__parent__ = None

	def Read(self) -> str:
		return self.__parent__.Read()
	def Write(self, command:str, arguments:str='') -> str:
		return self.__parent__.Write(f"{self.NAME}:{command}", arguments)
	def Query(self, command:str, arguments:str='') -> str:
		return self.__parent__.Query(f"{self.NAME}:{command}", arguments)
	
	STATE_COMMAND:str = 'STAT'
	@property
	@GetProperty(bool, STATE_COMMAND)
	def IsEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(bool, STATE_COMMAND)
	def IsEnabled(self, value:bool) -> bool:
		pass

class PossibleExternalModulation(Modulation):
	SOURCE_COMMAND:str = 'SOUR'
	INTERNAL_SOURCE:str = 'INT'
	EXTERNAL_SOURCE:str = 'EXT'
	@property
	def IsSourceExternal(self) -> bool:
		return True if self.Query(PossibleExternalModulation.SOURCE_COMMAND) == PossibleExternalModulation.EXTERNAL_SOURCE else False
	@IsSourceExternal.setter
	def IsSourceExternal(self, value:bool) -> bool:
		value = bool(value)
		self.Write(PossibleExternalModulation.SOURCE_COMMAND, PossibleExternalModulation.EXTERNAL_SOURCE if value else PossibleExternalModulation.INTERNAL_SOURCE)
		if self.IsSourceExternal != value:
			raise Exception(f"Error while setting {type(self).__class__.__name__} {"external" if value else "internal"} source")
		return value
	
	INTERNAL_FUNCTION_COMMAND:str = 'INT:FUNC'
	@property
	@GetProperty(Function, INTERNAL_FUNCTION_COMMAND)
	def InternalFunction(self, getMethodReturn) -> Function:
		return getMethodReturn
	@InternalFunction.setter
	@SetProperty(Function, INTERNAL_FUNCTION_COMMAND)
	def InternalFunction(self, value:Function) -> Function:
		pass
	
	INTERNAL_FREQUENCY_COMMAND:str = 'INT:FREQ'
	@property
	@GetProperty(float, INTERNAL_FREQUENCY_COMMAND)
	def InternalFrequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@InternalFrequency.setter
	@SetProperty(float, INTERNAL_FREQUENCY_COMMAND)
	def InternalFrequency(self, value:float) -> float:
		pass

class AmplitudeModulation(PossibleExternalModulation):
	NAME:str = 'AM'

	DEPTH_COMMAND:str = 'DEPT'
	@property
	@GetProperty(float, DEPTH_COMMAND)
	def Depth(self, getMethodReturn) -> float:
		return getMethodReturn
	@Depth.setter
	@SetProperty(float, DEPTH_COMMAND)
	def Depth(self, value:float) -> float:
		pass

class FrequencyModulation(PossibleExternalModulation):
	NAME:str = 'FM'

	DEVIATION_COMMAND:str = 'DEV'
	@property
	@GetProperty(float, DEVIATION_COMMAND)
	def Deviation(self, getMethodReturn) -> float:
		return getMethodReturn
	@Deviation.setter
	@SetProperty(float, DEVIATION_COMMAND)
	def Deviation(self, value:float) -> float:
		pass

class PulseWidthModulation(PossibleExternalModulation):
	NAME:str = 'PWM'

	DEVIATION_COMMAND:str = 'DEV'
	@property
	@GetProperty(float, DEVIATION_COMMAND)
	def Deviation(self, getMethodReturn) -> float:
		return getMethodReturn
	@Deviation.setter
	@SetProperty(float, DEVIATION_COMMAND)
	def Deviation(self, value:float) -> float:
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

class Trigger(Enum):
	Immediate = 'IMM'
	External = 'EXT'
	Bus = 'BUS'

class TriggeredModulation(Modulation):
	TRIGGER_SOURCE_COMMAND:str = 'TRIG:SOUR'
	@property
	def TriggerSource(self) -> Trigger:
		return Trigger(self.__parent__.Query(TriggeredModulation.TRIGGER_SOURCE_COMMAND))
	@TriggerSource.setter
	def TriggerSource(self, value:Trigger) -> Trigger:
		value = Trigger(value)
		self.__parent__.Write(TriggeredModulation.TRIGGER_SOURCE_COMMAND, value.value)
		if self.TriggerSource != value:
			raise Exception(f"Error while setting {type(self).__class__.__name__} {value.name} trigger source")
		return value

	TRIGGER_SLOPE_COMMAND:str = 'TRIG:SLOP'
	POSITIVE_SLOPE:str = 'POS'
	NEGATIVE_SLOPE:str = 'NEG'
	@property
	def IsTriggerSlopeNegative(self) -> bool:
		return True if self.__parent__.Query(TriggeredModulation.TRIGGER_SLOPE_COMMAND) == TriggeredModulation.NEGATIVE_SLOPE else False
	@IsTriggerSlopeNegative.setter
	def IsTriggerSlopeNegative(self, value:bool) -> bool:
		value = bool(value)
		self.__parent__.Write(TriggeredModulation.TRIGGER_SLOPE_COMMAND, TriggeredModulation.NEGATIVE_SLOPE if value else TriggeredModulation.POSITIVE_SLOPE)
		if self.IsTriggerSlopeNegative != value:
			raise Exception(f"Error while setting {"negative" if value else "positive"} trigger slope")
		return value
	
	OUTPUT_TRIGGER_SLOPE_COMMAND:str = 'OUTP:TRIG:SLOP'
	@property
	def IsOutputTriggerSlopeNegative(self) -> bool:
		return True if self.__parent__.Query(TriggeredModulation.OUTPUT_TRIGGER_SLOPE_COMMAND) == TriggeredModulation.NEGATIVE_SLOPE else False
	@IsOutputTriggerSlopeNegative.setter
	def IsOutputTriggerSlopeNegative(self, value:bool) -> bool:
		value = bool(value)
		self.__parent__.Write(TriggeredModulation.OUTPUT_TRIGGER_SLOPE_COMMAND, TriggeredModulation.NEGATIVE_SLOPE if value else TriggeredModulation.POSITIVE_SLOPE)
		if self.IsOutputTriggerSlopeNegative != value:
			raise Exception(f"Error while setting {"negative" if value else "positive"} output trigger slope")
		return value
	
	OUTPUT_TRIGGER_COMMAND:str = 'OUTP:TRIG'
	@property
	def IsOutputTriggerEnabled(self) -> bool:
		return bool(int(self.__parent__.Query(TriggeredModulation.OUTPUT_TRIGGER_COMMAND)))
	@IsOutputTriggerEnabled.setter
	def IsOutputTriggerEnabled(self, value:bool) -> bool:
		value = bool(value)
		if self.TriggerSource is Trigger.External:
			raise Exception("Trigger should be by bus or manual")
		self.__parent__.Write(TriggeredModulation.OUTPUT_TRIGGER_COMMAND, int(value))
		if self.IsOutputTriggerEnabled != value:
			raise Exception(f"Error while en/dis-abling output trigger")
		return value

class FrequencySweepModulation(TriggeredModulation):
	NAME:str = 'SWE'

	SWEEP_SPACING_COMMAND:str = 'SPAC'
	LINEAR_SPACING:str = 'LIN'
	LOG_SPACING:str = 'LOG'
	@property
	def IsSpacingLinear(self) -> bool:
		return True if self.Query(FrequencySweepModulation.SWEEP_SPACING_COMMAND) == FrequencySweepModulation.LINEAR_SPACING else False
	@IsSpacingLinear.setter
	def IsSpacingLinear(self, value:bool) -> bool:
		value = bool(value)
		self.Write(FrequencySweepModulation.SWEEP_SPACING_COMMAND, FrequencySweepModulation.LINEAR_SPACING if value else FrequencySweepModulation.LOG_SPACING)
		if self.IsSpacingLinear != value:
			raise Exception(f"Error while setting {type(self).__class__.__name__} {"linear" if value else "log"} spacing")
		return value

	SWEEP_TIME_COMMAND:str = 'TIME'
	@property
	@GetProperty(float, SWEEP_TIME_COMMAND)
	def SweepTime(self, getMethodReturn) -> float:
		return getMethodReturn
	@SweepTime.setter
	@SetProperty(float, SWEEP_TIME_COMMAND)
	def SweepTime(self, value:float) -> float:
		pass
	
	FREQUENCY_START_COMMAND:str = 'FREQ:STAR'
	@property
	def FrequencyStart(self) -> float:
		return float(self.__parent__.Query(FrequencySweepModulation.FREQUENCY_START_COMMAND))
	@FrequencyStart.setter
	def FrequencyStart(self, value:float) -> float:
		value = float(value)
		self.__parent__.Write(FrequencySweepModulation.FREQUENCY_START_COMMAND)
		if self.FrequencyStart != value:
			raise Exception(f"Error while setting start frequency")
		return value
	
	FREQUENCY_STOP_COMMAND:str = 'FREQ:STOP'
	@property
	def FrequencyStop(self) -> float:
		return float(self.__parent__.Query(FrequencySweepModulation.FREQUENCY_STOP_COMMAND))
	@FrequencyStop.setter
	def FrequencyStop(self, value:float) -> float:
		value = float(value)
		self.__parent__.Write(FrequencySweepModulation.FREQUENCY_STOP_COMMAND)
		if self.FrequencyStop != value:
			raise Exception(f"Error while setting stop frequency")
		return value
	
	FREQUENCY_CENTER_COMMAND:str = 'FREQ:CENT'
	@property
	def FrequencyCenter(self) -> float:
		return float(self.__parent__.Query(FrequencySweepModulation.FREQUENCY_CENTER_COMMAND))
	@FrequencyCenter.setter
	def FrequencyCenter(self, value:float) -> float:
		value = float(value)
		self.__parent__.Write(FrequencySweepModulation.FREQUENCY_CENTER_COMMAND)
		if self.FrequencyCenter != value:
			raise Exception(f"Error while setting center frequency")
		return value
	
	FREQUENCY_SPAN_COMMAND:str = 'FREQ:SPAN'
	@property
	def FrequencySpan(self) -> float:
		return float(self.__parent__.Query(FrequencySweepModulation.FREQUENCY_SPAN_COMMAND))
	@FrequencySpan.setter
	def FrequencySpan(self, value:float) -> float:
		value = float(value)
		self.__parent__.Write(FrequencySweepModulation.FREQUENCY_SPAN_COMMAND)
		if self.FrequencySpan != value:
			raise Exception(f"Error while setting span frequency")
		return value
	
	SYNC_FREQUENCY_COMMAND:str = 'MARK:FREQ'
	@property
	def SyncFrequency(self) -> float:
		return float(self.__parent__.Query(FrequencySweepModulation.SYNC_FREQUENCY_COMMAND))
	@SyncFrequency.setter
	def SyncFrequency(self, value:float) -> float:
		value = float(value)
		self.__parent__.Write(FrequencySweepModulation.SYNC_FREQUENCY_COMMAND, value)
		if self.SyncFrequency != value:
			raise Exception(f"Error while setting marker frequency")
		return value
	
	SYNC_COMMAND:str = 'OUTP:SYNC'
	@property
	def IsSynced(self) -> bool:
		return bool(int(self.__parent__.Query(FrequencySweepModulation.SYNC_COMMAND)))
	@IsSynced.setter
	def IsSynced(self, value:bool) -> bool:
		value = bool(value)
		self.__parent__.Write(FrequencySweepModulation.SYNC_COMMAND, int(value))
		if self.IsSynced != value:
			raise Exception(f"Error while en/dis-abling output trigger")
		return value

class BurstModulation(TriggeredModulation):
	NAME:str = 'BURS'

	MODE_COMMAND:str = 'MODE'
	FIXED_COUNT_MODE:str = 'TRIG'
	INFINITE_MODE:str = 'GAT'
	@property
	def IsBurstInfiniteWhenTrigger(self) -> bool:
		return True if self.Query(BurstModulation.MODE_COMMAND) == BurstModulation.INFINITE_MODE else False
	@IsBurstInfiniteWhenTrigger.setter
	def IsBurstInfiniteWhenTrigger(self, value:bool) -> bool:
		value = bool(value)
		self.Write(BurstModulation.MODE_COMMAND, BurstModulation.INFINITE_MODE if value else BurstModulation.FIXED_COUNT_MODE)
		if self.IsBurstInfiniteWhenTrigger != value:
			raise Exception(f"Error while setting {type(self).__class__.__name__} {"linear" if value else "log"} spacing")
		return value

	CYCLES_COMMAND:str = 'NCYC'
	@property
	@GetProperty(int, CYCLES_COMMAND)
	def Cycles(self, getMethodReturn) -> int:
		return getMethodReturn
	@Cycles.setter
	@SetProperty(int, CYCLES_COMMAND)
	def Cycles(self, value:int) -> int:
		pass

	CYCLE_PERIOD_COMMAND:str = 'INT:PER'
	@property
	@GetProperty(float, CYCLE_PERIOD_COMMAND)
	def CyclePeriod(self, getMethodReturn) -> float:
		return getMethodReturn
	@CyclePeriod.setter
	@SetProperty(float, CYCLE_PERIOD_COMMAND)
	def CyclePeriod(self, value:float) -> float:
		pass

	PHASE_COMMAND:str = 'PHAS'
	@property
	@GetProperty(float, PHASE_COMMAND)
	def Phase(self, getMethodReturn) -> float:
		return getMethodReturn
	@Phase.setter
	@SetProperty(float, PHASE_COMMAND)
	def Phase(self, value:float) -> float:
		pass

	TRIGGER_IN_INVERTED_COMMAND:str = 'GATE:POL'
	INVERTED_TRIGGER_IN_MODE:str = 'INV'
	NORMAL_TRIGGER_IN_MODE:str = 'NORM'
	@property
	def IsTriggerInInverted(self) -> bool:
		return True if self.Query(BurstModulation.TRIGGER_IN_INVERTED_COMMAND) == BurstModulation.INVERTED_TRIGGER_IN_MODE else False
	@IsTriggerInInverted.setter
	def IsTriggerInInverted(self, value:bool) -> bool:
		value = bool(value)
		self.Write(BurstModulation.TRIGGER_IN_INVERTED_COMMAND, BurstModulation.INVERTED_TRIGGER_IN_MODE if value else BurstModulation.NORMAL_TRIGGER_IN_MODE)
		if self.IsTriggerInInverted != value:
			raise Exception(f"Error while setting {type(self).__class__.__name__} {"inverted" if value else "normal"} trigger-in polarisation")
		return value

MODULATIONS_NAMES = dict([(subclass.NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(Modulation) if subclass.NAME])
import math
from aenum import Enum
from numpy import log10, linspace, logspace
from pyVirtualLab.VISAInstrument import Source, GetProperty, SetProperty

class OutSignal(Enum):
	Sweep = 'SWE'
	SourceSettled = 'SETT'
	PulseVideo = 'PVID'
	PulseSync = 'PSYN'
	LXI = 'LXI'
	Pulse = 'PULS'
	Sweep8757DCompatible = 'SW8757'
	SweepStart = 'SRUN'
	Trigger1In = 'TRIG1'
	Trigger2In = 'TRIG2'
	SweepEnd = 'SFD'
	Disconnected = 'NONE'

class TriggerSource(Enum):
	VISACommand = 'BUS'
	Immediate = 'IMM'
	Trigger1 = 'TRIG'
	Trigger2 = 'TRIG2'
	Pulse = 'PULS'
	PulseVideo = 'PVID'
	PulseSync = 'PSYN'
	TriggerKey = 'KEY'
	Timer = 'TIM'
	Off = 'MAN'

class PulseType(Enum):
	Square = 'SQU'
	FreeRun = 'FRUN'
	Triggered = 'TRIG'
	AdjustableDoublet = 'ADO'
	Doublet = 'DOUB'
	Gated = 'GATE'
	External = 'EXT'

class AgilentN5183B(Source):
	def __init__(self, address: str):
		super(AgilentN5183B, self).__init__(address, 20000)

	def __abort__(self):
		self.IsEnabled = False

	DEFAULT_POWER_FORMAT = "{:2.2f}"
	DEFAULT_MAX_POWER = 30
	@property
	def MaxPower(self) -> float:
		return float(self.Query("SOUR:POW:USER:MAX"))
	@MaxPower.setter
	def MaxPower(self, value: float):
		if value == +math.inf:
			self.Write("SOUR:POW:USER:ENAB OFF")
		else:
			self.Write("SOUR:POW:USER:MAX " + str(value))
			if self.MaxPower != float(self.DEFAULT_POWER_FORMAT.format(value)):
				raise Exception("Error while setting the power protection value")
			self.Write("SOUR:POW:USER:ENAB ON")
			if not bool(int(self.Query("SOUR:POW:USER:ENAB"))):
				raise Exception("Error while setting the power protection feature")

	@property
	@GetProperty(float, 'SOUR:POW:LEV:IMM:AMPL')
	def Power(self, getMethodReturn) -> float:
		return getMethodReturn
	@Power.setter
	@SetProperty(float, 'SOUR:POW:LEV:IMM:AMPL')
	def Power(self, value: float):
		pass

	@property
	@GetProperty(float, 'SOUR:FREQ:FIX')
	def Frequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@Frequency.setter
	def Frequency(self, value: float):
		value = round(value, 2)
		self.Write('SOUR:FREQ:FIX', str(value))
		if self.Frequency != value:
			raise Exception("Error while setting the frequency")

	@property
	@GetProperty(float, 'SOUR:FREQ:MULT')
	def FrequencyMultiplier(self, getMethodReturn) -> float:
		return getMethodReturn
	@FrequencyMultiplier.setter
	@SetProperty(float, 'SOUR:FREQ:MULT')
	def FrequencyMultiplier(self, value: float) -> float:
		return value

	@property
	@GetProperty(bool, 'OUTP:MOD:STAT')
	def IsModulationEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsModulationEnabled.setter
	@SetProperty(bool, 'OUTP:MOD:STAT')
	def IsModulationEnabled(self, value: bool) -> bool:
		return value

	@property
	@GetProperty(bool, 'OUTP:STAT')
	def IsEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(bool, 'OUTP:STAT')
	def IsEnabled(self, value: bool) -> bool:
		return value
	
	def CompensateDeviceGain(self, deviceFrequencyDependentGain: dict[float, float], desiredGain: float) -> dict[float, float]:
		compensatingPowers = dict(zip(deviceFrequencyDependentGain.keys(), [(desiredGain - gain) for gain in deviceFrequencyDependentGain.values()]))
		self.LoadCompensation(compensatingPowers)
		return compensatingPowers

	def LoadCompensation(self, compensations: dict[float, float]):
		self.ClearCompensation()
		for compensation in compensations:
			self.Write("SOUR:CORR:FLAT:PAIR " + str(compensation) + ',' + str(compensations[compensation]))

	def ClearCompensation(self):
		self.Write("SOUR:CORR:FLAT:LOAD TMP")
		self.Write("SOUR:CORR:FLAT:PRES")

	@property
	@GetProperty(bool, 'SOUR:CORR:STAT')
	def IsCompensated(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsCompensated.setter
	@SetProperty(bool, 'SOUR:CORR:STAT')
	def IsCompensated(self, value: bool) -> bool:
		return value

	@property
	@GetProperty(bool, 'SOUR:PULM:STAT')
	def IsPulseEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsPulseEnabled.setter
	@SetProperty(bool, 'SOUR:PULM:STAT')
	def IsPulseEnabled(self, value: bool) -> bool:
		return value

	AVOID_DELAY_SET_PULSE_TYPES = [PulseType.Square,
								   PulseType.FreeRun,
								   PulseType.Gated,
								   PulseType.External]
	@property
	def PulseDelay(self) -> float:
		return float(self.Query('SOUR:PULM:INT:DEL'))
	@PulseDelay.setter
	def PulseDelay(self, value: float):
		if self.PulseTypeSet in AgilentN5183B.AVOID_DELAY_SET_PULSE_TYPES:
			raise Exception("Pulse delay not available with this pulse type")
		value = float(value)
		self.Write('SOUR:PULM:INT:DEL', str(value))
		if self.PulseDelay != value:
			raise Exception("Error while setting the pulse delay")

	@property
	def PulsePeriod(self) -> float:
		return float(self.Query('SOUR:PULM:INT:PER'))
	@PulsePeriod.setter
	def PulsePeriod(self, value: float):
		value = float(value)
		if value <= self.PulseWidth:
			raise Exception("Pulse width must be inferior to pulse period")
		self.Write('SOUR:PULM:INT:PER', str(value))
		if self.PulsePeriod != value:
			raise Exception("Error while setting the pulse period")

	@property
	def PulseWidth(self) -> float:
		return float(self.Query('SOUR:PULM:INT:PWID'))
	@PulseWidth.setter
	def PulseWidth(self, value: float):
		value = float(value)
		if value >= self.PulsePeriod:
			raise Exception("Pulse width must be inferior to pulse period")
		self.Write('SOUR:PULM:INT:PWID', str(value))
		if self.PulseWidth != value:
			raise Exception("Error while setting the pulse width")
	
	EXTERNAL_PULSE_SOURCE = str(PulseType.External.value)
	INTERNAL_PULSE_SOURCE = 'INT'
	@property
	def PulseTypeSet(self) -> PulseType:
		if self.Query('SOUR:PULM:SOUR') == AgilentN5183B.EXTERNAL_PULSE_SOURCE:
			return PulseType.External
		else:
			return PulseType(self.Query('SOUR:PULM:SOUR:INT'))
	@PulseTypeSet.setter
	def PulseTypeSet(self, value: PulseType):
		e = None
		savedIsPulseEnabled = self.IsPulseEnabled
		try:
			if not savedIsPulseEnabled:
				self.IsPulseEnabled = True
			value = PulseType(value)
			if value == PulseType.External:
				self.Write('SOUR:PULM:SOUR', AgilentN5183B.EXTERNAL_PULSE_SOURCE)
			else:
				self.Write('SOUR:PULM:SOUR', AgilentN5183B.INTERNAL_PULSE_SOURCE)
				self.Write('SOUR:PULM:SOUR:INT', str(value.value))
			if self.PulseTypeSet != value:
				raise Exception("Error while setting pulse type")
		except Exception as e: e = e
		finally:
			if not savedIsPulseEnabled:
				self.IsPulseEnabled = savedIsPulseEnabled
			if e: raise e

	SWEEP_ON_MODE = 'LIST'
	SWEEP_OFF_MODE = 'FIX'
	@property
	def IsFrequencySweepEnabled(self) -> bool:
		return self.Query('SOUR:FREQ:MODE') == AgilentN5183B.SWEEP_ON_MODE
	@IsFrequencySweepEnabled.setter
	def IsFrequencySweepEnabled(self, value: bool) -> bool:
		value = bool(value)
		self.Write('SOUR:FREQ:MODE', AgilentN5183B.SWEEP_ON_MODE if value else AgilentN5183B.SWEEP_OFF_MODE)
		if self.IsFrequencySweepEnabled != value:
			raise Exception('Error while en/dis-abling frequency sweep')
		return value
	@property
	def IsPowerSweepEnabled(self) -> bool:
		return self.Query('SOUR:POW:MODE') == AgilentN5183B.SWEEP_ON_MODE
	@IsPowerSweepEnabled.setter
	def IsPowerSweepEnabled(self, value: bool) -> bool:
		value = bool(value)
		self.Write('SOUR:POW:MODE', AgilentN5183B.SWEEP_ON_MODE if value else AgilentN5183B.SWEEP_OFF_MODE)
		if self.IsPowerSweepEnabled != value:
			raise Exception('Error while en/dis-abling power sweep')
		return value

	LINEAR_SPACE_FORMAT_NAME = 'LIN'
	LOGARITHMIC_SPACE_FORMAT_NAME = 'LOG'
	LIST_SWEEP_TYPE = 'LIST'
	STEPS_SWEEP_TYPE = 'STEP'
	@property
	def SweepPoints(self) -> list[float, float]:
		isDwellTimeUnique = True
		if self.Query('SOUR:LIST:TYPE') == AgilentN5183B.STEPS_SWEEP_TYPE:
			frequencyStart = float(self.Query('SOUR:FREQ:STAR'))
			frequencyStop = float(self.Query('SOUR:FREQ:STOP'))
			points = int(self.Query('SOUR:SWE:POIN'))
			if self.Query('SOUR:SWE:SPAC') == AgilentN5183B.LOGARITHMIC_SPACE_FORMAT_NAME:
				frequencies = logspace(log10(frequencyStart), log10(frequencyStop), points)
			else:
				frequencies = linspace(frequencyStart, frequencyStop, points)
			frequencies = [round(frequency, 2) for frequency in frequencies]
			powerStart = float(self.Query('SOUR:POW:STAR'))
			powerStop = float(self.Query('SOUR:POW:STOP'))
			powers = linspace(powerStart, powerStop, points)
		else:
			frequencies = [float(freq) for freq in self.Query('SOUR:LIST:FREQ').split(',')]
			powers = [float(freq) for freq in self.Query('SOUR:LIST:POW').split(',')]
			isDwellTimeUnique = self.Query('SOUR:LIST:DWEL:TYPE') == AgilentN5183B.STEPS_SWEEP_TYPE
		
		if isDwellTimeUnique:
			dwellTimes = [float(self.Query('SOUR:SWE:DWEL'))] * len(frequencies)
		else:
			dwellTimes = [float(dwellTime) for dwellTime in self.Query('SOUR:LIST:DWEL').split(',')]
		
		return list(zip(frequencies, powers, dwellTimes))
	@SweepPoints.setter
	def SweepPoints(self, value: list[float, float, float]) -> list[float, float, float]:
		self.Write('SOUR:LIST:TYPE', 'LIST')
		self.Write('SOUR:LIST:TYPE:LIST:INIT:PRES')
		self.Write('SOUR:LIST:FREQ', ','.join([str(piece[0]) for piece in value]))
		self.Write('SOUR:LIST:POW', ','.join([str(piece[1]) for piece in value]))

		dwellTimes = [piece[2] for piece in value]
		uniqueDwellTimes = len(set(dwellTimes)) 
		if uniqueDwellTimes > 1:
			self.Write('SOUR:LIST:DWEL', ','.join([str(dwellTime) for dwellTime in dwellTimes]))
			self.Write('SOUR:LIST:DWEL:TYPE', AgilentN5183B.LIST_SWEEP_TYPE)
		else:
			self.Write('SOUR:SWE:DWEL', str(dwellTimes[0]))
			self.Write('SOUR:LIST:DWEL:TYPE', AgilentN5183B.STEPS_SWEEP_TYPE)
		return self.SweepPoints

	def SetSweepPointsByRanges(self, frequencyStart: float, frequencyStop: float, powerStart: float, powerStop: float, points: int, isFrequencyRangeLogarithmic: bool, dwellTime: float):
		self.Write('SOUR:LIST:TYPE', 'STEP')
		self.Write('SOUR:FREQ:STAR', str(frequencyStart))
		self.Write('SOUR:FREQ:STOP', str(frequencyStop))
		self.Write('SOUR:POW:STAR', str(powerStart))
		self.Write('SOUR:POW:STOP', str(powerStop))
		self.Write('SOUR:SWE:POIN', str(points))
		self.Write('SOUR:SWE:SPAC', AgilentN5183B.LOGARITHMIC_SPACE_FORMAT_NAME if isFrequencyRangeLogarithmic else AgilentN5183B.LINEAR_SPACE_FORMAT_NAME)
		self.Write('SOUR:SWE:DWEL', str(dwellTime))
	
	EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME = 'EXT'
	EXTERNAL_SWEEP_TRIGGER_SOURCES = [
		TriggerSource.Trigger1,
		TriggerSource.Trigger2,
		TriggerSource.Pulse
	]
	INTERNAL_SWEEP_TRIGGER_SOURCE_NAME = 'INT'
	INTERNAL_SWEEP_TRIGGER_SOURCES = [
		TriggerSource.PulseSync,
		TriggerSource.PulseVideo
	]
	@property
	def SweepTriggerSource(self) -> TriggerSource:
		value = self.Query('TRIG:SOUR')
		match value:
			case AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME:
				return TriggerSource(self.Query('TRIG:EXT:SOUR'))
			case AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCE_NAME:
				return TriggerSource(self.Query('TRIG:INT:SOUR'))
			case _:
				return TriggerSource(value)
	@SweepTriggerSource.setter
	def SweepTriggerSource(self, value: TriggerSource) -> TriggerSource:
		value = TriggerSource(value)
		if value in AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCES:
			self.Write('TRIG:EXT:SOUR', str(value.value))
			self.Write('TRIG:SOUR', AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME)
		elif value in AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCES:
			self.Write('TRIG:INT:SOUR', str(value.value))
			self.Write('TRIG:SOUR', AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCE_NAME)
		else:
			self.Write('TRIG:SOUR', str(value.value))
		if self.SweepTriggerSource != value:
			raise Exception("Error while setting sweep trigger source")
		return value
	@property
	def SweepPointTriggerSource(self) -> TriggerSource:
		value = self.Query('LIST:TRIG:SOUR')
		match value:
			case AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME:
				return TriggerSource(self.Query('LIST:TRIG:EXT:SOUR'))
			case AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCE_NAME:
				return TriggerSource(self.Query('LIST:TRIG:INT:SOUR'))
			case _:
				return TriggerSource(value)
	@SweepPointTriggerSource.setter
	def SweepPointTriggerSource(self, value: TriggerSource) -> TriggerSource:
		value = TriggerSource(value)
		if value in AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCES:
			self.Write('LIST:TRIG:EXT:SOUR', str(value.value))
			self.Write('LIST:TRIG:SOUR', AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME)
		elif value in AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCES:
			self.Write('LIST:TRIG:INT:SOUR', str(value.value))
			self.Write('LIST:TRIG:SOUR', AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCE_NAME)
		else:
			self.Write('LIST:TRIG:SOUR', str(value.value))
		if self.SweepPointTriggerSource != value:
			raise Exception("Error while setting sweep point trigger source")
		return value

	SWEEP_NORMAL_DIRECTION = 'DOWN'
	SWEEP_REVERSED = 'UP'
	@property
	def IsSweepReversed(self) -> bool:
		return self.Query('SOUR:LIST:DIR') == AgilentN5183B.SWEEP_REVERSED
	@IsSweepReversed.setter
	def IsSweepReversed(self, value: bool) -> bool:
		value = bool(value)
		self.Write('SOUR:LIST:DIR', AgilentN5183B.SWEEP_REVERSED if value else AgilentN5183B.SWEEP_NORMAL_DIRECTION)
		if self.IsSweepReversed != value:
			raise Exception("Error while setting sweep direction")
		return value

	@property
	@GetProperty(bool, 'LIST:RETR')
	def SweepReturnToFirstPoint(self, getMethodReturn) -> bool:
		return getMethodReturn
	@SweepReturnToFirstPoint.setter
	@SetProperty(bool, 'LIST:RETR')
	def SweepReturnToFirstPoint(self, value: bool) -> bool:
		return value

	@property
	@GetProperty(bool, 'SOUR:LFO:STAT')
	def IsLowFrequencyOutputEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsLowFrequencyOutputEnabled.setter
	@SetProperty(bool, 'SOUR:LFO:STAT')
	def IsLowFrequencyOutputEnabled(self, value: bool) -> bool:
		return value

	BANNED_SWEEP_OUT_SIGNAL = [
		OutSignal.LXI,
		OutSignal.Pulse,
		OutSignal.Trigger1In,
		OutSignal.Trigger2In,
		OutSignal.Disconnected
	]
	@property
	@GetProperty(OutSignal, 'ROUT:CONN:SOUT')
	def SweepOutSignal2(self, getMethodReturn) -> OutSignal:
		return getMethodReturn
	@property
	def SweepOutSignal(self) -> OutSignal:
		return OutSignal(self.Query('ROUT:CONN:SOUT'))
	@SweepOutSignal.setter
	def SweepOutSignal(self, value: OutSignal):
		value = OutSignal(value)
		if value in AgilentN5183B.BANNED_SWEEP_OUT_SIGNAL:
			raise Exception('This type of signal is not allowed for this connector')
		self.Write('ROUT:CONN:SOUT', str(value.value))
		if self.SweepOutSignal != value:
			raise Exception("Error while setting this connector out signal")

	BANNED_TRIGGER1_OUT_SIGNAL = [
		OutSignal.Sweep8757DCompatible,
		OutSignal.SweepStart,
		OutSignal.Trigger1In
	]
	@property
	def Trigger1OutSignal(self) -> OutSignal:
		return OutSignal(self.Query('ROUT:CONN:TRIGger1:OUTP'))
	@Trigger1OutSignal.setter
	def Trigger1OutSignal(self, value: OutSignal):
		value = OutSignal(value)
		if value in AgilentN5183B.BANNED_TRIGGER1_OUT_SIGNAL:
			raise Exception('This type of signal is not allowed for this connector')
		self.Write('ROUT:CONN:TRIGger1:OUTP', str(value.value))
		if self.Trigger1OutSignal != value:
			raise Exception("Error while setting this connector out signal")

	BANNED_TRIGGER2_OUT_SIGNAL = [
		OutSignal.Sweep8757DCompatible,
		OutSignal.SweepStart,
		OutSignal.Trigger2In
	]
	@property
	def Trigger2OutSignal(self) -> OutSignal:
		return OutSignal(self.Query('ROUT:CONN:TRIGger2:OUTP'))
	@Trigger2OutSignal.setter
	def Trigger2OutSignal(self, value: OutSignal):
		value = OutSignal(value)
		if value in AgilentN5183B.BANNED_TRIGGER2_OUT_SIGNAL:
			raise Exception('This type of signal is not allowed for this connector')
		self.Write('ROUT:CONN:TRIGger2:OUTP', str(value.value))
		if self.Trigger2OutSignal != value:
			raise Exception("Error while setting this connector out signal")

'''If the LF out port is connected to sweep out port to get a unique out trig port,
this "helping" static method set the sweep out connector to allow the LF out signal to pass through.'''
def SetLFOutPassThroughSweepOut(agilentN5183B: AgilentN5183B):
	agilentN5183B.SweepOutSignal = OutSignal.SourceSettled
from pyVirtualLab.VISAInstrument import Instrument
from pyVirtualLab.Helpers import GetProperty, SetProperty, roundScientificNumber

class Oscilloscope(Instrument):
	def __init__(self, address = None, timeout = Instrument.DEFAULT_VISA_TIMEOUT):
		super().__init__(address, timeout)

	def AutoScale(self):
		self.Write("AUT")

	#region TIME SCALE

	TIMESCALE_COMMAND:str = 'TIM:SCAL'
	@property
	@GetProperty(float, TIMESCALE_COMMAND)
	def TimeScale(self, getMethodReturn) -> float:
		return getMethodReturn
	@TimeScale.setter
	@SetProperty(float, TIMESCALE_COMMAND, rounding=lambda x : roundScientificNumber(x, 2))
	def TimeScale(self, value: float) -> float:
		pass

	@property
	@GetProperty(float, 'TIM:POS')
	def Delay(self, getMethodReturn) -> float:
		return getMethodReturn
	@Delay.setter
	@SetProperty(float, 'TIM:POS', rounding=lambda x : roundScientificNumber(x, 2))
	def Delay(self, value: float) -> float:
		pass

	#endregion
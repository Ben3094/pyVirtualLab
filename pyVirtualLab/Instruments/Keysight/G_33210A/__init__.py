from aenum import Enum

from pyVirtualLab.VISAInstrument import Instrument, Source
from pyVirtualLab.Helpers import GetProperty, SetProperty
from . import Functions

class AmplitudeUnit(Enum):
	PeakPeakVoltage = 'VPP'
	RMSVoltage = 'VRMS'
	dBm = 'DBM'

class G_33210A(Source):
	def __init__(self, address, timeout=Instrument.DEFAULT_VISA_TIMEOUT):
		super().__init__(address, timeout)

	OUTPUT_COMMAND:str = 'OUTP'
	@property
	@GetProperty(bool, OUTPUT_COMMAND)
	def IsEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(bool, OUTPUT_COMMAND)
	def IsEnabled(self, value:bool) -> bool:
		pass

	def __abort__(self):
		self.IsEnabled = False

	LOAD_COMMAND:str = 'OUTP:LOAD'
	@property
	@GetProperty(float, LOAD_COMMAND)
	def Load(self, getMethodReturn) -> float:
		return getMethodReturn
	@Load.setter
	@SetProperty(float, LOAD_COMMAND)
	def Load(self, value:float) -> float:
		pass

	FREQUENCY_COMMAND:str = 'FREQ'
	@property
	@GetProperty(float, FREQUENCY_COMMAND)
	def Frequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@Frequency.setter
	@SetProperty(float, FREQUENCY_COMMAND)
	def Frequency(self, value:float) -> float:
		pass

	AMPLITUDE_COMMAND:str = 'VOLT'
	@property
	@GetProperty(float, AMPLITUDE_COMMAND)
	def Amplitude(self, getMethodReturn) -> float:
		return getMethodReturn
	@Amplitude.setter
	@SetProperty(float, AMPLITUDE_COMMAND)
	def Amplitude(self, value:float) -> float:
		pass

	OFFSET_COMMAND:str = 'VOLT:OFFS'
	@property
	@GetProperty(float, OFFSET_COMMAND)
	def Offset(self, getMethodReturn) -> float:
		return getMethodReturn
	@Offset.setter
	@SetProperty(float, OFFSET_COMMAND)
	def Offset(self, value:float) -> float:
		pass

	LOW_LEVEL_COMMAND:str = 'VOLT:LOW'
	@property
	@GetProperty(float, LOW_LEVEL_COMMAND)
	def LowLevel(self, getMethodReturn) -> float:
		return getMethodReturn
	@LowLevel.setter
	@SetProperty(float, LOW_LEVEL_COMMAND)
	def LowLevel(self, value:float) -> float:
		pass

	HIGH_LEVEL_COMMAND:str = 'VOLT:HIGH'
	@property
	@GetProperty(float, HIGH_LEVEL_COMMAND)
	def HighLevel(self, getMethodReturn) -> float:
		return getMethodReturn
	@HighLevel.setter
	@SetProperty(float, HIGH_LEVEL_COMMAND)
	def HighLevel(self, value:float) -> float:
		pass

	AUTORANGE_COMMAND:str = 'VOLT:RANG:AUTO'
	@property
	@GetProperty(bool, AUTORANGE_COMMAND)
	def Autorange(self, getMethodReturn) -> bool:
		return getMethodReturn
	@Autorange.setter
	@SetProperty(bool, AUTORANGE_COMMAND)
	def Autorange(self, value:bool) -> bool:
		pass

	POLARITY_COMMAND:str = 'OUTP:POL'
	INVERTED_POLARITY:str = 'INV'
	NORMAL_POLARITY:str = 'NORM'
	@property
	def IsInverted(self) -> bool:
		return True if self.Query(G_33210A.POLARITY_COMMAND) == G_33210A.INVERTED_POLARITY else False
	@IsInverted.setter
	def IsInverted(self, value:bool) -> bool:
		value = bool(value)
		self.Write(G_33210A.POLARITY_COMMAND, G_33210A.INVERTED_POLARITY if value else G_33210A.NORMAL_POLARITY)
		if self.IsInverted != value:
			raise Exception('Error while setting inversion')
		return value

	ENABLE_SYNC_COMMAND:str = 'OUT:SYNC'
	@property
	@GetProperty(bool, ENABLE_SYNC_COMMAND)
	def IsSyncEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsSyncEnabled.setter
	@SetProperty(bool, ENABLE_SYNC_COMMAND)
	def IsSyncEnabled(self, value:bool) -> bool:
		pass

	AMPLITUDE_UNIT_COMMAND:str = 'VOLT:UNIT'
	@property
	@GetProperty(AmplitudeUnit, AMPLITUDE_UNIT_COMMAND)
	def Unit(self, getMethodReturn) -> AmplitudeUnit:
		return getMethodReturn
	@Unit.setter
	@SetProperty(AmplitudeUnit, AMPLITUDE_UNIT_COMMAND)
	def Unit(self, value:AmplitudeUnit) -> AmplitudeUnit:
		pass


	#region FUNCTION

	__function__ = None
	@property
	def Function(self) -> Functions.Function:
		reply:str = self.Query(Functions.FUNCTION_COMMAND)
		if self.__function__ is not Functions.FUNCTIONS_NAMES[reply]:
			if self.__function__:
				self.__function__.__parent__ = None # Unlink old trigger object
			self.__function__ = Functions.FUNCTIONS_NAMES[reply]()
		self.__function__.__parent__ = self
		return self.__function__
	@Function.setter
	def Function(self, value:Functions.Function) -> Functions.Function:
		self.Write(Functions.FUNCTION_COMMAND, value.NAME)
		self.__function__ = value
		currentFunction = self.Function
		if value == currentFunction:
			raise Exception("Error while setting the function")
		return currentFunction
	
	# endregion
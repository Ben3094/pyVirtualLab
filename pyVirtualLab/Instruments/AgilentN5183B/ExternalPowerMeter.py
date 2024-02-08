from ...VISAInstrument import Instrument, VirtualResource, InterfaceType, ETHERNET_DEVICE_NAME_ENTRY_NAME, ETHERNET_HOST_ADDRESS_ENTRY_NAME, ETHERNET_PORT_ENTRY_NAME

class ExternalPowerMeterResource(VirtualResource):
	def __init__(self, parentPowerMeter):
		self.__parent__ = parentPowerMeter
	
	def write(self, value: str) -> None:
		isPowerMeterDisplayed = self.__parent__.IsDisplayed
		isPassthroughEnabled = self.__parent__.IsPassthroughEnabled

		# Enable passthrough
		if isPowerMeterDisplayed:
			self.__parent__.IsDisplayed = False
		if not isPassthroughEnabled:
			self.__parent__.IsPassthroughEnabled = True

		self.__parent__.Parent.Write(f"SYST:PMET{self.__parent__.Index}:PASS", f"\"{value}\"")

		# Disable passthrough
		if not isPassthroughEnabled:
			self.__parent__.IsPassthroughEnabled = False
		if isPowerMeterDisplayed:
			self.__parent__.IsDisplayed = True
	
	def read(self) -> str:
		return self.__parent__.Parent.Read()
	
	def query(self, value: str) -> str:
		isPowerMeterDisplayed = self.__parent__.IsDisplayed
		isPassthroughEnabled = self.__parent__.IsPassthroughEnabled

		# Enable passthrough
		if isPowerMeterDisplayed:
			self.__parent__.IsDisplayed = False
		if not isPassthroughEnabled:
			self.__parent__.IsPassthroughEnabled = True

		value = self.__parent__.Parent.Query(f"SYST:PMET{self.__parent__.Index}:PASS", f"\"{value}\"")

		# Disable passthrough
		if not isPassthroughEnabled:
			self.__parent__.IsPassthroughEnabled = False
		if isPowerMeterDisplayed:
			self.__parent__.IsDisplayed = True

		return value
	
	@property
	def timeout(self) -> float:
		return float(self.__parent__.Parent.Query(f"SYST:PMET{self.__parent__.Index}:PASS:TIM"))
	@timeout.setter
	def timeout(self, value:float):
		value = float(value)
		self.__parent__.Parent.Write(f"SYST:PMET{self.__parent__.Index}:PASS:TIM", value)
		if self.timeout != value:
			raise Exception(f"Error while setting external power meter {self.__parent__.Index} timeout")

class ExternalPowerMeter(Instrument):
	def __init__(self, originalPowerMeter:Instrument, parentAgilentN5183B, externalPowerMeterIndex:int):
		super(ExternalPowerMeter, self).__init__()
		self.__parent__ = parentAgilentN5183B
		self.__index__ = int(externalPowerMeterIndex)
		self.Resource = ExternalPowerMeterResource(self)
		self.__originalPowerMeter__:Instrument = originalPowerMeter
		self.__originalPowerMeter__.Resource = self.Resource

	@property
	def Parent(self):
		return self.__parent__
	
	@property
	def Index(self) -> int:
		return self.__index__
	
	@property
	def PowerMeter(self) -> Instrument:
		return self.__originalPowerMeter__
	
	@property
	def IsPowerMeterCorrectionOnA(self) -> bool:
		return self.__parent__.__getPowerMeterCorrectionOnA__(self.__index__)
	@IsPowerMeterCorrectionOnA.setter
	def IsPowerMeterCorrectionOnA(self, value: bool) -> bool:
		return self.__parent__.__setPowerMeterCorrectionOnA__(self.__index__, value)
	
	@property
	def Power(self) -> float:
		return self.__parent__.__getPowerMeterMeasurement__(self.__index__)
	
	@property
	def Average(self) -> int:
		if self.__parent__.__getPowerMeterMeasurementAverageState__(self.__index__):
			return 0
		elif self.__parent__.__getPowerMeterMeasurementAutoAverageState__(self.__index__):
			return -1
		else:
			return self.__parent__.__getPowerMeterMeasurementAverageCount__(self.__index__)
	@Average.setter
	def Average(self, value: int) -> int:
		value = int(value)
		if value < -1:
			raise ValueError("Negative number (except -1 (automatic)) are not accepted")
		match value:
			case 0:
				self.__parent__.__setPowerMeterMeasurementAverageState__(self.__index__, False)
			case -1:
				self.__parent__.__setPowerMeterMeasurementAverageState__(self.__index__, True)
				self.__parent__.__setPowerMeterMeasurementAutoAverageState__(self.__index__, True)
			case _:
				self.__parent__.__setPowerMeterMeasurementAverageCount__(self.__index__, value)
				self.__parent__.__setPowerMeterMeasurementAverageState__(self.__index__, True)
				self.__parent__.__setPowerMeterMeasurementAutoAverageState__(self.__index__, False)
		return value
	
	@property
	def IsDisplayed(self) -> bool:
		return self.__parent__.__getPowerMeterMeasurementDisplayingState__(self.__index__)
	@IsDisplayed.setter
	def IsDisplayed(self, value: bool) -> bool:
		return self.__parent__.__setPowerMeterMeasurementDisplayingState__(self.__index__, value)
	
	@property
	def IsDecibelUnit(self) -> bool:
		return self.__parent__.__getPowerMeterDecibelMeasurementState__(self.__index__)
	@IsDecibelUnit.setter
	def IsDecibelUnit(self, value: bool) -> bool:
		return self.__parent__.__setPowerMeterDecibelMeasurementState__(self.__index__, value)
	
	@property
	def IsPassthroughEnabled(self) -> bool:
		return self.__parent__.__getPowerMeterPassthroughState__(self.__index__)
	@IsPassthroughEnabled.setter
	def IsPassthroughEnabled(self, value: bool) -> bool:
		return self.__parent__.__setPowerMeterPassthroughState__(self.__index__, value)
	
	def UseAsEqualizatingPowerMeter(self):
		match self.PowerMeter.InterfaceType:
			case InterfaceType.GPIB_VXI:
				self.Write(f"SOUR:CORR:PMET:COMM:TYPE", 'VXI11')
			case InterfaceType.Ethernet:
				self.Write(f"SOUR:CORR:PMET:COMM:TYPE", 'SOCK')
				self.Write(f"SOUR:CORR:PMET:COMM:LAN:DEV", self.PowerMeter.InterfaceProperties[ETHERNET_DEVICE_NAME_ENTRY_NAME])
				self.Write(f"SOUR:CORR:PMET:COMM:LAN:IP", self.PowerMeter.InterfaceProperties[ETHERNET_HOST_ADDRESS_ENTRY_NAME])
				self.Write(f"SOUR:CORR:PMET:COMM:LAN:PORT", self.PowerMeter.InterfaceProperties[ETHERNET_PORT_ENTRY_NAME] if ETHERNET_PORT_ENTRY_NAME in self.PowerMeter.InterfaceProperties else str(AgilentN5183B.DEFAULT_POWER_METER_PORT))

			case InterfaceType.USB:
				self.Write(f"SOUR:CORR:PMET:COMM:TYPE", 'USB')
			case _:
				raise Exception("Direct connection from Agilent N5183B to a power meter must use Ethernet, GPIB-VXI, and USB")
		
		
		self.Write('SOUR:CORR:PMET:CHAN', 'A' if self.IsPowerMeterCorrectionOnA else 'B')
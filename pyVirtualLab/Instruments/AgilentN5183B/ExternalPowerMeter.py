from ...VISAInstrument import Instrument, VirtualResource

class ExternalPowerMeter(Instrument):
	def __init__(self, powerMeter:Instrument, parentAgilentN5183B, externalPowerMeterIndex:int):
		self.__parent__ = parentAgilentN5183B
		self.__index__ = int(externalPowerMeterIndex)
		self.Resource = ExternalPowerMeterResource(self.__parent__, self.__index__)
		self.__powerMeter__:Instrument = powerMeter
		self.__powerMeter__.Resource = self.Resource

	@property
	def Parent(self):
		return self.__parent__
	
	@property
	def Index(self) -> int:
		return self.__index__
	
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

class ExternalPowerMeterResource(VirtualResource):
	def __init__(self, parentPowerMeter:ExternalPowerMeter):
		self.__parent__:ExternalPowerMeter = parentPowerMeter
	
	def write(self, value: str) -> None:
		isPowerMeterDisplayed = self.__parent__.IsDisplayed
		isPassthroughEnabled = self.__parent__.IsPassthroughEnabled

		# Enable passthrough
		if isPowerMeterDisplayed:
			self.__parent__.IsDisplayed = False
		if not isPassthroughEnabled:
			self.__parent__.IsPassthroughEnabled = True

		self.__parent__.Parent.Write(f"SYST:PMET{self.__parent__.Index}:PASS", f"<\"{value}\">")

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

		value = self.__parent__.Parent.Query(f"SYST:PMET{self.__parent__.Index}:PASS", f"<\"{value}\">")

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
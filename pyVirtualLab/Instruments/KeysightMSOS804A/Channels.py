from aenum import Enum

class ChannelUnit(Enum):
	Volt = 0
	Ampere = 1
	Watt = 2
	Unknown = 3

class Channel():
	TYPE_COMMAND_HEADER = 'CHAN'

	def __init__(self, parentKeysightMSOS804A, address):
		self.__parent__ = parentKeysightMSOS804A
		self.__address__ = address
		self.__commandAddress__ = f"{self.TYPE_COMMAND_HEADER}{self.__address__}"

	@property
	def Address(self) -> float:
		return self.__address__

	@property
	def IsEnabled(self) -> bool:
		return bool(int(self.__parent__.Query(f"{self.__commandAddress__}:DISP")))
	@IsEnabled.setter
	def IsEnabled(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:DISP {int(value)}")
		if self.IsEnabled != value:
			raise Exception(f"Error when en/dis-able {self.__commandAddress__}")
		return value

	def GetWaveform(self) -> dict[float, float]:
		self.__parent__.Write("WAV:SOUR", self.__commandAddress__)
		self.__parent__.Write("WAV:BYT LSBF")
		self.__parent__.Write("WAV:FORM WORD")
		yIncrement = float(self.__parent__.Query("WAV:YINC"))
		yOrigin = float(self.__parent__.Query("WAV:YOR"))
		xIncrement = float(self.__parent__.Query("WAV:XINC"))
		xOrigin = float(self.__parent__.Query("WAV:XOR"))
		savedTimeout = self.__parent__.VISATimeout
		self.__parent__.VISATimeout = 200000
		data = self.__parent__.__instr__.query_binary_values("WAV:DATA?", datatype='h', is_big_endian=False)
		data = [yIncrement * float(result) + yOrigin for result in data]
		abscissae = range(0, len(data))
		abscissae = [xIncrement * float(abscissa) + xOrigin for abscissa in abscissae]
		data = dict(zip(abscissae, data))
		self.__parent__.VISATimeout = savedTimeout
		return data
	
	@property
	def Scale(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:SCAL"))
	@Scale.setter
	def Scale(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:SCAL {value}")
		if self.Scale != value:
			raise Exception("Error while setting scale")
		return value
	
	@property
	def Offset(self) -> float:
		return float(self.__parent__.Query(f"{self.__commandAddress__}:OFFS"))
	@Offset.setter
	def Offset(self, value: float) -> float:
		value = float(value)
		self.__parent__.Write(f"{self.__commandAddress__}:OFFS {value}")
		if self.Offset != value:
			raise Exception("Error while setting offset")
		return value
	
	# Measurements
	def GetMaximum(self) -> float:
		return float(self.__parent__.Query(f"MEAS:VMAX", f"{self.__commandAddress__}"))
	def GetMinimum(self) -> float:
		return float(self.__parent__.Query(f"MEAS:VMIN", f"{self.__commandAddress__}"))
	def GetRange(self) -> float:
		return float(self.__parent__.Query(f"MEAS:VPP", f"{self.__commandAddress__}"))
	def GetFrequency(self) -> float:
		return float(self.__parent__.Query(f"MEAS:FREQ", f"{self.__commandAddress__}"))
	def GetPeriod(self) -> float:
		return float(self.__parent__.Query(f"MEAS:PER", f"{self.__commandAddress__}"))
	def GetRiseTime(self) -> float:
		return float(self.__parent__.Query(f"MEAS:RIS", f"{self.__commandAddress__}"))
	def GetFallTime(self) -> float:
		return float(self.__parent__.Query(f"MEAS:FALL", f"{self.__commandAddress__}"))
	
	# AC measurements
	OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT = 'DISP'
	OVER_1_CYCLE_MEASUREMENT_ARGUMENT = 'CYCL'
	def GetAverage(self, overOnly1Cycle = False) -> float:
		savedSendValidMeas = self.__parent__.SendValidMeasurements
		self.__parent__.SendValidMeasurements = True
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT,
	    		self.__commandAddress__]
		value = float(self.__parent__.Query('MEAS:VAV', ','.join(args)).split(',')[0])
		if not savedSendValidMeas:
			self.__parent__.SendValidMeasurements = False
		return value
	
	def GetArea(self, overOnly1Cycle = False) -> float:
		savedSendValidMeas = self.__parent__.SendValidMeasurements
		self.__parent__.SendValidMeasurements = True
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT,
	    		self.__commandAddress__]
		value = float(self.__parent__.Query('MEAS:AREA', ','.join(args)).split(',')[0])
		if not savedSendValidMeas:
			self.__parent__.SendValidMeasurements = False
		return value

	WITH_DC_COMPONENT_ARGUMENT = 'DC'
	WITHOUT_DC_COMPONENT_ARGUMENT = 'AC'
	def GetRMS(self, overOnly1Cycle = False, removeDCComponent = True) -> float:
		savedSendValidMeas = self.__parent__.SendValidMeasurements
		self.__parent__.SendValidMeasurements = True
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT,
	    		AnalogChannel.WITHOUT_DC_COMPONENT_ARGUMENT if removeDCComponent else AnalogChannel.WITH_DC_COMPONENT_ARGUMENT,
	    		self.__commandAddress__]
		value = float(self.__parent__.Query('MEAS:VRMS', ','.join(args)).split(',')[0])
		if not savedSendValidMeas:
			self.__parent__.SendValidMeasurements = False
		return value

class AnalogChannel(Channel):
	@property
	def Label(self) -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:LAB?")
	@Label.setter
	def Label(self, value: str) -> str:
		value = str(value)
		if value.isascii() & len(value) <= 16:
			self.__parent__.Write(f"{self.__commandAddress__}:LAB {value}")
		else:
			raise Exception("Label must be ASCII and less or equal 16 characters long")
		if self.Label != value:
			raise Exception("Error while setting label")
		return value

	@property
	def IsInverted(self) -> bool:
		return bool(self.__parent__.Query(f"{self.__commandAddress__}:INV"))
	@IsInverted.setter
	def IsInverted(self, value: bool):
		return self.__parent__.Write(f"{self.__commandAddress__}:INV {int(bool(value))}")
	
	@property
	def Unit(self) -> ChannelUnit:
		match self.__parent__.Query(f"{self.__commandAddress__}:UNIT"):
			case "VOLT":
				return ChannelUnit.Volt
			case "AMP":
				return ChannelUnit.Ampere
			case "WATT":
				return ChannelUnit.Watt
			case "UNKN":
				return ChannelUnit.Unknown
	@Unit.setter
	def Unit(self, value: ChannelUnit):
		match value:
			case ChannelUnit.Volt:
				self.__parent__.Write(f"{self.__commandAddress__}:UNIT VOLT")
			case ChannelUnit.Ampere:
				self.__parent__.Write(f"{self.__commandAddress__}:UNIT AMP")
			case ChannelUnit.Watt:
				self.__parent__.Write(f"{self.__commandAddress__}:UNIT WATT")
			case ChannelUnit.Unknown:
				self.__parent__.Write(f"{self.__commandAddress__}:UNIT UNKN")

class DigitalChannel(Channel):
	TYPE_COMMAND_HEADER = 'DIG'

class WaveformMemoryChannel(Channel):
	TYPE_COMMAND_HEADER = 'WMEM'
	def Save(self, channel:Channel):
		self.__parent__.Write(f"{self.__commandAddress__}:SAVE", channel.__commandAddress__)
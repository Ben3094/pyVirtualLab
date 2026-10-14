from aenum import Enum

class Source():
	TYPE_COMMAND_HEADER = None
	
	__commandAddress__:str = None

	def __init__(self):
		self.__commandAddress__ = self.TYPE_COMMAND_HEADER

	def __eq__(self, value):
		if hasattr(value, 'TYPE_COMMAND_HEADER'):
			return self.TYPE_COMMAND_HEADER == value.TYPE_COMMAND_HEADER
		else: return False

class AuxSource(Source):
	TYPE_COMMAND_HEADER = 'AUX'
	
class LineSource(Source):
	TYPE_COMMAND_HEADER = 'LINE'

class ChannelUnit(Enum):
	Volt = 0
	Ampere = 1
	Watt = 2
	Unknown = 3
class Channel(Source):
	TYPE_COMMAND_HEADER = 'CHAN'
	
	__parent__ = None
	__address__:str = None

	def __init__(self, parentKeysightMSOS804A, address):
		super().__init__()
		self.__parent__ = parentKeysightMSOS804A
		self.__address__ = address
		self.__commandAddress__ = f"{self.__commandAddress__}{self.__address__}"

	@property
	def Address(self) -> float:
		return self.__address__

	def Read(self) -> str:
		return self.__parent__.Read()
	def Write(self, command:str, arguments:str='') -> str:
		return self.__parent__.Write(f"{self.__commandAddress__}:{command}", arguments)
	def Query(self, command:str, arguments:str='') -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:{command}", arguments)

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
		savedTimeout = self.__parent__.Timeout
		self.__parent__.Timeout = 200000
		data = self.__parent__.__resource__.query_binary_values("WAV:DATA?", datatype='h', is_big_endian=False)
		data = [yIncrement * float(result) + yOrigin for result in data]
		abscissae = range(0, len(data))
		abscissae = [xIncrement * float(abscissa) + xOrigin for abscissa in abscissae]
		data = dict(zip(abscissae, data))
		self.__parent__.Timeout = savedTimeout
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
	MAX_MEASUREMENTS_DISPLAYED = 4
	def __queryMeasurement__(self, command, args, addToResultsList:bool) -> float:
		if addToResultsList:
			measurements = self.__parent__.GetMeasurements()
			if len(measurements) > Channel.MAX_MEASUREMENTS_DISPLAYED:
				raise Exception("No more measurement slots available")
			if (not ((command, args) in self.__parent__.__measurements__)):
				self.__parent__.Write(command, args)
				measurements = self.__parent__.GetMeasurements()
				self.__parent__.__measurements__[(command, args)] = measurements[0].Name
			return next(measurement for measurement in measurements if measurement.Name == self.__parent__.__measurements__[(command, args)]).Value
		else:
			return float(self.__parent__.Query(command, args))
	
	def GetFrequency(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:FREQ", f"{self.__commandAddress__}", addToResultsList)
	def GetPeriod(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:PER", f"{self.__commandAddress__}", addToResultsList)
	def GetPositiveWidth(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:PWID", f"{self.__commandAddress__}", addToResultsList)
	def GetNegativeWidth(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:NWID", f"{self.__commandAddress__}", addToResultsList)
	RISING_DUTY_CYCLE_MEASUREMENT_ARGUMENT = 'RIS'
	FALLING_DUTY_CYCLE_MEASUREMENT_ARGUMENT = 'FALL'
	def GetDutyCycle(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:NDUT", f"{self.__commandAddress__}", addToResultsList)
	
class VerticalMeasurePossibleChannel(Channel):
	def GetMaximum(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:VMAX", f"{self.__commandAddress__}", addToResultsList)
	def GetMinimum(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:VMIN", f"{self.__commandAddress__}", addToResultsList)
	def GetRange(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:VPP", f"{self.__commandAddress__}", addToResultsList)
	def GetRiseTime(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:RIS", f"{self.__commandAddress__}", addToResultsList)
	def GetFallTime(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:FALL", f"{self.__commandAddress__}", addToResultsList)
	def GetPeakToPeakAmplitude(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:VPP", f"{self.__commandAddress__}", addToResultsList)
	def GetBase(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:VBAS", f"{self.__commandAddress__}", addToResultsList)
	def GetTop(self, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:VTOP", f"{self.__commandAddress__}", addToResultsList)
	def GetMeasurementAt(self, time:float, addToResultsList:bool=False) -> float:
		return self.__queryMeasurement__("MEAS:VTIM", f"{float(time)},{self.__commandAddress__}", addToResultsList)
	
	# AC measurements
	OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT = 'DISP'
	OVER_1_CYCLE_MEASUREMENT_ARGUMENT = 'CYCL'
	def GetAverage(self, overOnly1Cycle:bool=False, addToResultsList:bool=False) -> float:
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT, self.__commandAddress__]
		value = self.__queryMeasurement__('MEAS:VAV', ','.join(args), addToResultsList)
		return value

	WITH_DC_COMPONENT_ARGUMENT = 'DC'
	WITHOUT_DC_COMPONENT_ARGUMENT = 'AC'
	def GetRMS(self, overOnly1Cycle:bool=False, removeDCComponent:bool=True, addToResultsList:bool=False) -> float:
		args = [AnalogChannel.OVER_1_CYCLE_MEASUREMENT_ARGUMENT if overOnly1Cycle else AnalogChannel.OVER_ALL_DISPLAYED_MEASUREMENTS_ARGUMENT, AnalogChannel.WITHOUT_DC_COMPONENT_ARGUMENT if removeDCComponent else AnalogChannel.WITH_DC_COMPONENT_ARGUMENT, self.__commandAddress__]
		value = self.__queryMeasurement__('MEAS:VRMS', ','.join(args), addToResultsList)
		return value

class AnalogChannel(VerticalMeasurePossibleChannel):
	AC_COUPLING_ARGUMENT:str = "AC"
	DC_COUPLING_ARGUMENT:str = "DC"
	@property
	def IsACCoupled(self) -> bool:
		return self.__parent__.Query(f"{self.__commandAddress__}:COUP") == AnalogChannel.AC_COUPLING_ARGUMENT
	@IsACCoupled.setter
	def IsACCoupled(self, value:bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"{self.__commandAddress__}:COUP {AnalogChannel.AC_COUPLING_ARGUMENT if value else AnalogChannel.DC_COUPLING_ARGUMENT}")
		if self.IsACCoupled != value:
			raise Exception(f"Error while setting channel {self.Address} coupling")
		return value

	@property
	def Label(self) -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:LAB")
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

	def AutoScale(self):
		self.__parent__.Write('AUT:VERT', self.__commandAddress__)
		self.__parent__.Wait()

	GET_RANGE_COMMAND:str = "RANG"
	@property
	def Range(self) -> float:
		return float(self.Write(AnalogChannel.GET_RANGE_COMMAND))
	@property
	def MinValue(self) -> float:
		return self.Offset - 4 * self.Scale
	@property
	def MaxValue(self) -> float:
		return self.Offset + 4 * self.Scale

class DigitalChannel(Channel):
	TYPE_COMMAND_HEADER = 'DIG'

class WaveformMemoryChannel(VerticalMeasurePossibleChannel):
	TYPE_COMMAND_HEADER = 'WMEM'
	def Save(self, channel:Channel, isDisplayed:bool=True):
		self.__parent__.Write(f"{self.__commandAddress__}:SAVE", channel.__commandAddress__)
		self.IsEnabled = isDisplayed
	def Clear(self):
		self.__parent__.Write(f"{self.__commandAddress__}:CLE")
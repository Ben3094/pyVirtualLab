from pyVirtualLab.VISAInstrument import Instrument, InterfaceType, ETHERNET_HOST_ADDRESS_ENTRY_NAME, ETHERNET_PORT_ENTRY_NAME, ETHERNET_DEVICE_NAME_ENTRY_NAME
from pyVirtualLab.Helpers import GetProperty, SetProperty
from aenum import Enum
from .Channels import Channel, AnalogChannel, WaveformMemoryChannel
from .Functions import Function, FUNCTIONS_NAMES
from .Measurements import Measurement, MeasurementType, StatisticMode, MeasurementState
import re

class TriggerState(Enum):
	auto = "AUTO"
	normal = "NORM"
	single = "SINGLE"
	stop = "STOP"

# If you use an ethernet connection, you must set LeCroy MAUI-based oscilloscope to use LXI.
class LeCroy2610N(Instrument):
	def __init__(self, address: str):
		super(LeCroy2610N, self).__init__(address)
		self.__analogChannels__ = dict()
		self.__waveformMemoryChannels__ = dict()
		self.__functions__ = dict()
		self.Timeout = 10000

	TIME_SCALE_COMMAND:str = 'TDIV'
	@property
	@GetProperty(float, TIME_SCALE_COMMAND)
	def TimeScale(self, getMethodReturn) -> float:
		return getMethodReturn
	@TimeScale.setter
	@SetProperty(float, TIME_SCALE_COMMAND, check=False)
	def TimeScale(self, value:float) -> float:
		pass

	DELAY_PARAMETER:str = 'TRDL'
	@property
	@GetProperty(float, DELAY_PARAMETER)
	def Delay(self, getMethodReturn) -> float:
		return getMethodReturn
	@Delay.setter
	@SetProperty(float, DELAY_PARAMETER, check=False)
	def Delay(self, value:float) -> float:
		pass

	HEADER_COMMAND:str = 'CHDR'
	@property
	@GetProperty(bool, HEADER_COMMAND)
	def ReturnHeader(self, getMethodReturn) -> bool:
		return getMethodReturn
	@ReturnHeader.setter
	@SetProperty(bool, HEADER_COMMAND, check=False)
	def ReturnHeader(self, value:bool) -> bool:
		pass
	
	CLEAR_ALL_PARAMETERS_COMMAND:str = 'PACL'
	CLEAR_PARAMETER_COMMAND:str = 'PADL'
	def DeleteMeasurement(self, index:list[int]|int):
		"""_summary_

		Args:
			index (int): Index of the measurement. If -1, clear all measurements.
		"""
		if index == -1:
			self.Write(self.CLEAR_ALL_PARAMETERS_COMMAND)
			return
		
		if not type(index) is list:
			index = [index]
		index = [int(i) for i in index]
		for i in index:
			self.Write(f"{self.CLEAR_PARAMETER_COMMAND} {i}")
		return

	TRIGGER_MODE_COMMAND:str = "TRMD"
	@property
	@GetProperty(TriggerState, TRIGGER_MODE_COMMAND)
	def TriggerMode(self, getMethodReturn) -> TriggerState:
		return getMethodReturn
	@TriggerMode.setter
	@SetProperty(TriggerState, TRIGGER_MODE_COMMAND)
	def TriggerMode(self, value:TriggerState) -> TriggerState:
		pass

	ANALOG_CHANNELS = 4
	@property
	def AnalogChannels(self) -> dict[int, AnalogChannel]:
		if len(self.__analogChannels__) < 1:
			for address in range(1, self.ANALOG_CHANNELS+1):
				self.__analogChannels__[address] = AnalogChannel(self, address)
		return self.__analogChannels__

	WAVEFORM_MEMORIES = 4
	@property
	def WaveformMemoryChannels(self) -> dict[int, WaveformMemoryChannel]:
		if len(self.__waveformMemoryChannels__) < 1:
			for address in range(1, self.WAVEFORM_MEMORIES+1):
				self.__waveformMemoryChannels__[address] = WaveformMemoryChannel(self, address)
		return self.__waveformMemoryChannels__

	FUNCTIONS = 16
	@property
	def Functions(self) -> dict[int, Function]:
		for address in range(1, self.FUNCTIONS+1):
			query = f"{Function.TYPE_COMMAND_HEADER}{address}"
			response = self.Query(query).lstrip(':').split()
			params = response[1].split(',')
			channelsInvolved = [channelInvolved for channelInvolved in params if channelInvolved.startswith(AnalogChannel.TYPE_COMMAND_HEADER) or channelInvolved.startswith(DigitalChannel.TYPE_COMMAND_HEADER) or channelInvolved.startswith(Function.TYPE_COMMAND_HEADER)]
			self.__functions__[address] = FUNCTIONS_NAMES[response[0]](self, address, channelsInvolved)
		return self.__functions__

	def GetMeasurementType(self, index:int) -> tuple[MeasurementType, Channel]:
		values = self.Query(Channel.SET_MEASUREMENT_COMMAND, str(index)).split(',')
		return (MeasurementType(values[1]), self.StringToChannel(values[2]))
	
	MEASURE_TIMEOUT = 30000
	GET_MEASUREMENT_COMMAND:str = 'PAVA'
	GET_MEASUREMENTS_STATISTIC_COMMAND:str = 'PAST'
	GET_MEASUREMENTS_STATISTIC_COMMAND_RESPONSE_PREFIX:int = 2
	def GetMeasurement(self, index:int, withStatistic:bool=False) -> Measurement:
		savedTimeout = self.Timeout
		self.Timeout = self.MEASURE_TIMEOUT
		#values = sub(MEASUREMENT_STATES_RECOGNITION_PATTERN, '\\1;', self.Query(self.GET_MEASUREMENTS_COMMAND)).split(';')
		values = self.Query(self.GET_MEASUREMENT_COMMAND, f"{Channel.CUSTOM_MEASUREMENT_PREFIX}{index}").split(',')
		self.Timeout = savedTimeout
		measurementDict:dict = {
			Measurement.MEASUREMENT_NAME_COLUMN_NAME: values[0],
			Measurement.MEASUREMENT_CURRENT_VALUE_COLUMN_NAME: values[1],
			Measurement.MEASUREMENT_STATE_COLUMN_NAME: MeasurementState(values[2])
		}
		if withStatistic:
			for statisticMode in StatisticMode:
				measurementDict[statisticMode.name] = self.Query(self.GET_MEASUREMENTS_STATISTIC_COMMAND, f"{Measurement.CUSTOM_MEASUREMENT_PREFIX},{statisticMode.value}").split(',')[self.GET_MEASUREMENTS_STATISTIC_COMMAND_RESPONSE_PREFIX + index - 1]
		return Measurement(measurementDict)
	
	MEASUREMENTS_MIN_INDEX:int = 1
	__measurementsMaxIndex__:int = None
	@property
	def MEASUREMENTS_MAX_INDEX(self) -> int:
		if self.__measurementsMaxIndex__ == None:
			self.__measurementsMaxIndex__ = len(self.Query(self.GET_MEASUREMENTS_STATISTIC_COMMAND, f"{Channel.CUSTOM_MEASUREMENT_PREFIX},{StatisticMode.Average.value}").split(',')[2:])
		return self.__measurementsMaxIndex__
	__measurementsCount__:int = None
	@property
	def MEASUREMENTS_COUNT(self) -> int:
		if self.__measurementsCount__ == None:
			self.__measurementsCount__ = self.MEASUREMENTS_MAX_INDEX - self.MEASUREMENTS_MIN_INDEX
		return self.__measurementsCount__
	
	@property
	def Measurements(self) -> dict[int, tuple[MeasurementType, Channel]]:
		def getMeasurementsTypes():
			for index in range(self.MEASUREMENTS_MIN_INDEX, self.MEASUREMENTS_MAX_INDEX):
				yield index, self.GetMeasurementType(index)
		return getMeasurementsTypes()

	def StringToChannel(self, value:str) -> Channel:
		match = re.match('([A-Z]+)(\d+)?', value)
		match match.groups(0)[0]:
			case AnalogChannel.TYPE_COMMAND_HEADER:
				return self.AnalogChannels[int(match.groups(0)[1])]

			case Function.TYPE_COMMAND_HEADER:
				return self.__functions__[int(match.groups(0)[1])]

			case WaveformMemoryChannel.TYPE_COMMAND_HEADER:
				return self.WaveformMemoryChannels[int(match.groups(0)[1])]
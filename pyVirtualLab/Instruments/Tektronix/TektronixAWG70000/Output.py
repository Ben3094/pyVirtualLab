from aenum import Enum
from pyVirtualLab.Helpers import GetProperty, SetProperty

class FrequencyFilter(Enum):
	LowPass = 'LPAS'
	BandPass = 'BPAS'
	# TODO: add OUTPut[n]:FILTer:BPASs:RANGe as intermediate value with MultiEnum

class OutputPath(Enum):
	Direct = 'DIR'
	AC = 'AC'
	DCAmplified = "DCA"

class Output():
	COMMAND_PREFIX:str = "OUTP"

	def __init__(self, parent, address):
		self.__parent__ = parent
		self.__address__ = address
		self.__commandAddress__ = f"{Output.COMMAND_PREFIX}{self.__address__}"

	def Read(self) -> str:
		return self.__parent__.Read()
	def Write(self, command:str, arguments:str='') -> str:
		return self.__parent__.Write(f"{self.__commandAddress__}:{command}", arguments)
	def Query(self, command:str, arguments:str='') -> str:
		return self.__parent__.Query(f"{self.__commandAddress__}:{command}", arguments)
	
	STATE_COMMNAD:str = 'STAT'
	@property
	@GetProperty(bool, STATE_COMMNAD)
	def IsEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(bool, STATE_COMMNAD)
	def IsEnabled(self, value:bool) -> bool:
		pass
	
	def __hasACOption__(self) -> bool:
		return 'AC' in self.__parent__.Options
	FILTER_COMMNAD:str = 'FILT'
	@property
	@GetProperty(FrequencyFilter, FILTER_COMMNAD, booleanStatePropertyName=__hasACOption__, offStateValue=None)
	def Filter(self, getMethodReturn) -> FrequencyFilter:
		return getMethodReturn
	@Filter.setter
	def Filter(self, value:FrequencyFilter) -> FrequencyFilter:
		if self.__hasACOption__():
			value = FrequencyFilter(value)
			self.Write(Output.FILTER_COMMNAD, value.value)
			if self.Filter != value:
				raise Exception(f"Error while setting output {self.__address__} filter")
			return value
		else:
			raise NotImplementedError(f"{self.__parent__.Id} has not the AC option")
		
	GENERIC_ATTENUATION_COMMAND:str = "ATT:"
	def __setAttenuation__(self, address:int, value:float):
		if self.__hasACOption__():
			value = float(value)
			address = f"A{address}" if address > 0 else "DAC"
			command = f"{Output.GENERIC_ATTENUATION_COMMAND}{address}"
			self.Write(command, value.value)
			if getattr(self, f"{address}Attenuation") != value:
				raise Exception(f"Error while setting output {self.__address__} {address} attenuation")
			return value
		else:
			raise NotImplementedError(f"{self.__parent__.Id} has not the AC option")
	DAC_ATTENUATION_COMMAND:str = "ATT:DAC"
	@property
	@GetProperty(float, DAC_ATTENUATION_COMMAND, booleanStatePropertyName=__hasACOption__, offStateValue=None)
	def DACAttenuation(self, getMethodReturn) -> float:
		return getMethodReturn
	@DACAttenuation.setter
	def DACAttenuation(self, value:float) -> float:
		self.__setAttenuation__(0, value)
	A1_ATTENUATION_COMMAND:str = "ATT:A1"
	@property
	@GetProperty(float, A1_ATTENUATION_COMMAND, booleanStatePropertyName=__hasACOption__, offStateValue=None)
	def A1Attenuation(self, getMethodReturn) -> float:
		return getMethodReturn
	@A1Attenuation.setter
	def A1Attenuation(self, value:float) -> float:
		self.__setAttenuation__(1, value)
	A2_ATTENUATION_COMMAND:str = "ATT:A2"
	@property
	@GetProperty(float, A2_ATTENUATION_COMMAND, booleanStatePropertyName=__hasACOption__, offStateValue=None)
	def A2Attenuation(self, getMethodReturn) -> float:
		return getMethodReturn
	@A2Attenuation.setter
	def A2Attenuation(self, value:float) -> float:
		self.__setAttenuation__(1, value)
	A3_ATTENUATION_COMMAND:str = "ATT:A3"
	@property
	@GetProperty(float, A3_ATTENUATION_COMMAND, booleanStatePropertyName=__hasACOption__, offStateValue=None)
	def A3Attenuation(self, getMethodReturn) -> float:
		return getMethodReturn
	@A3Attenuation.setter
	def A3Attenuation(self, value:float) -> float:
		self.__setAttenuation__(1, value)
	
	FILTER_COMMNAD:str = 'PATH'
	@property
	@GetProperty(FrequencyFilter, FILTER_COMMNAD, booleanStatePropertyName=__hasACOption__, offStateValue=None)
	def Filter(self, getMethodReturn) -> FrequencyFilter:
		return getMethodReturn
	@Filter.setter
	def Filter(self, value:FrequencyFilter) -> FrequencyFilter:
		if self.__hasACOption__():
			value = FrequencyFilter(value)
			self.Write(Output.FILTER_COMMNAD, value.value)
			if self.Filter != value:
				raise Exception(f"Error while setting output {self.__address__} filter")
			return value
		else:
			raise NotImplementedError(f"{self.__parent__.Id} has not the AC option")
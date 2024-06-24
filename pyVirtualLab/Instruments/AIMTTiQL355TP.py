from pyVirtualLab.VISAInstrument import VirtualInstrument, Source, GetProperty, SetProperty
from collections import namedtuple

Range = namedtuple("Range", "Index MaxVoltage MaxCurrent")
RANGES:dict[int, namedtuple] = {
	0: Range(0, 15, 5),
	1: Range(1, 35, 3),
	2: Range(2, 35, 0.5)
}

class Output(VirtualInstrument):
	__outputAddress__:int = None

	def __init__(self, parent, address):
		VirtualInstrument.__init__(self, parent)
		self.__outputAddress__ = address
	
	@property
	def OutputAddress(self) -> float:
		return self.__outputAddress__

	@property
	@GetProperty(float, 'V{__outputAddress__}')
	def Voltage(self, getMethodReturn) -> float:
		return getMethodReturn
	@Voltage.setter
	def Voltage(self, value: float):
		value = float(value)
		self.__applySuitedRange__(value, self.Current)
		self.Write(f"V{self.__outputAddress__}", str(value))
		if self.Voltage != value:
			raise Exception("Error while setting voltage")
		return value

	@property
	@GetProperty(float, 'OVP{__outputAddress__}')
	def OverVoltageProtection(self, getMethodReturn) -> float:
		return getMethodReturn
	@OverVoltageProtection.setter
	@SetProperty(float, 'OVP{__outputAddress__}')
	def OVP(self, value: float):
		pass

	@property
	@GetProperty(float, 'I{__outputAddress__}')
	def Current(self, getMethodReturn) -> float:
		return getMethodReturn
	@Current.setter
	def Current(self, value: float):
		value = float(value)
		self.__applySuitedRange__(self.Voltage, value)
		self.Write(f"I{self.__outputAddress__}", str(value))
		if self.Current != value:
			raise Exception("Error while setting current")
		return value

	@property
	@GetProperty(float, 'OCP{__outputAddress__}')
	def OverCurrentProtection(self, getMethodReturn) -> float:
		return getMethodReturn
	@OverCurrentProtection.setter
	@SetProperty(float, 'OCP{__outputAddress__}')
	def OverCurrentProtection(self, value: float):
		pass

	@property
	@GetProperty(float, 'DELTAV{__outputAddress__}')
	def VoltageStep(self, getMethodReturn) -> float:
		return getMethodReturn
	@VoltageStep.setter
	@SetProperty(float, 'DELTAV{__outputAddress__}')
	def VoltageStep(self, value: float):
		pass

	@property
	@GetProperty(float, 'DELTAI{__outputAddress__}')
	def CurrentStep(self, getMethodReturn) -> float:
		return getMethodReturn
	@CurrentStep.setter
	@SetProperty(float, 'DELTAI{__outputAddress__}')
	def CurrentStep(self, value: float):
		pass

	def IncrementVoltage(self):
		self.Write(f"INCV{self.__outputAddress__}")
	def DecrementVoltage(self):
		self.Write(f"DECV{self.__outputAddress__}")
	def IncrementCurrent(self):
		self.Write(f"INCI{self.__outputAddress__}")
	def DecrementCurrent(self):
		self.Write(f"DECI{self.__outputAddress__}")

	@property
	@GetProperty(bool, 'SENSE{__outputAddress__}')
	def IsRemoteSenseEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsRemoteSenseEnabled.setter
	@SetProperty(bool, 'SENSE{__outputAddress__}')
	def IsRemoteSenseEnabled(self, value: bool):
		pass

	@property
	@GetProperty(bool, 'OP{__outputAddress__}')
	def IsEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(bool, 'OP{__outputAddress__}')
	def IsEnabled(self, value: bool):
		pass
	
	@property
	def __range__(self):
		return RANGES[int(self.Query(f"RANGE{self.__outputAddress__}").lstrip('R').lstrip(f"{self.__outputAddress__}").lstrip())]
	@__range__.setter
	def __range__(self, value):
		self.Write(f"RANGE{self.__outputAddress__}", value.Index)
		if self.__range__ != value:
			raise Exception("Error while setting range value")
		return value
	def __applySuitedRange__(self, suitedVoltage:float, suitedCurrent:float):
		compatibleVoltageRanges = [range for range in list(RANGES.values()) if range.MaxVoltage > suitedVoltage]
		compatibleCurrentRanges = [range for range in list(RANGES.values()) if range.MaxCurrent > suitedCurrent]
		compatibleRanges = list(set(compatibleVoltageRanges).intersection(compatibleCurrentRanges))
		if not self.__range__ in compatibleRanges:
			self.__range__ = compatibleRanges[0]
	@property
	def VoltageRange(self) -> float:
		return self.__range__.MaxVoltage
	@VoltageRange.setter
	def VoltageRange(self, value:float) -> float:
		self.__range__ = [couple for couple in RANGES.values() if couple.MaxVoltage == value][0]
		return value
	@property
	def CurrentRange(self) -> float:
		return self.__range__.MaxCurrent
	@CurrentRange.setter
	def CurrentRange(self, value:float) -> float:
		self.__range__ = [couple for couple in RANGES.values() if couple.MaxCurrent == value][0]
		return value

	# @property
	# @GetProperty(int, 'LSR')
	# def LSR(self, getMethodReturn) -> int:
	# 	return getMethodReturn
	# @LSR.setter
	# @SetProperty(int, 'LSR')
	# def LSR(self, value: int):
	# 	pass

	# @property
	# @GetProperty(int, 'LSE')
	# def LSE(self, getMethodReturn) -> int:
	# 	return getMethodReturn
	# @LSE.setter
	# @SetProperty(int, 'LSE')
	# def LSE(self, value: int):
	# 	pass

	def SaveState(self, stateIndex:int):
		self.Write(f"SAV{self.__outputAddress__} {stateIndex}")
	def RecallState(self, stateIndex:int):
		self.Write(f"RCL{self.__outputAddress__} {stateIndex}")

	# @property
	# @GetProperty(int, 'CONFIG')
	# def CONFIG(self, getMethodReturn) -> int:
	# 	return getMethodReturn
	# @CONFIG.setter
	# @SetProperty(int, 'CONFIG')
	# def CONFIG(self, value: int):
	# 	pass

	# @property
	# @GetProperty(int, 'RATIO')
	# def RATIO(self, getMethodReturn) -> int:
	# 	return getMethodReturn
	# @RATIO.setter
	# @SetProperty(int, 'RATIO')
	# def RATIO(self, value: int):
	# 	pass

	# @property
	# @GetProperty(int, 'TRIPCONFIG')
	# def TRIPCONFIG(self, getMethodReturn) -> int:
	# 	return getMethodReturn
	# @TRIPCONFIG.setter
	# @SetProperty(int, 'TRIPCONFIG')
	# def TRIPCONFIG(self, value: int):
	# 	pass

class AIMTTiQL355TP(Source):
	OUTPUTS_START_INDEX:int = 1
	OUTPUTS_NUMBER:int = 2

	def __init__(self, address):
		super().__init__(address)
		self.__outputs__ = dict([(outputIndex, Output(self, outputIndex)) for outputIndex in range(AIMTTiQL355TP.OUTPUTS_START_INDEX, AIMTTiQL355TP.OUTPUTS_NUMBER + 1)])

	def SetAllState(self, state: bool):
		self.Write(f"OPALL {int(bool(state))}")

	def ClearTrippedState(self, value: int):
		self.Write('TRIPRST')

	@property
	@GetProperty(bool, 'MODE')
	def IsNotLinked(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsNotLinked.setter
	@SetProperty(bool, 'MODE')
	def IsNotLinked(self, value: bool):
		pass

	@property
	def Outputs(self) -> dict[int, Output]:
		return self.__outputs__
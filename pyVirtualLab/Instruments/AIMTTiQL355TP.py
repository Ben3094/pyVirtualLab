from pyVirtualLab.VISAInstrument import VirtualInstrument, Source, GetProperty, SetProperty

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
	@SetProperty(float, 'V{__outputAddress__}')
	def Voltage(self, value: float):
		pass

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
	@SetProperty(float, 'I{__outputAddress__}')
	def Current(self, value: float):
		pass

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
	@GetProperty(int, 'OP{__outputAddress__}')
	def IsEnabled(self, getMethodReturn) -> int:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(int, 'OP{__outputAddress__}')
	def IsEnabled(self, value: int):
		pass

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
	def Outputs(self) -> dict[int, Output]:
		return self.__outputs__
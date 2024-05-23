from enum import Enum
from typing import Any

class Condition(Enum):
	Unknown = -1
	Off = 0
	ConstantCurrentOperation = 1
	ConstantVoltageOperation = 2
	Faulty = 3

	@classmethod
	def _missing_(cls, value: object) -> Any:
		return cls.Unknown
	
class Output():
	def __init__(self, parentKeysightN6705C, address):
		self.__parent__ = parentKeysightN6705C
		self.__address__ = address
		self.__outputs__:dict[int, Output] = None

	@property
	def Address(self) -> int:
		return self.__address__
	
	@property
	def Conditions(self) -> Condition:
		return Condition(int(self.__parent__.Query(f"STAT:QUES:INST:ISUM{self.Address}:EVEN")))
	
	def ClearProtection(self):
		self.__parent__.Write(f"OUTP:PROT:CLE (@{self.Address})")

	@property
	def IsProtectionRaised(self, raiseException:bool = True):
		if self.Conditions == Condition.Faulty:
			if raiseException:
				raise Exception(f"Faulty output")
			else: 
				return True
		else:
			return False

	DEFAULT_DECIMAL_FORMAT = "{:2.6f}"
	def CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value:float) -> float:
		if value == None:
			return None
		else:
			return float(Output.DEFAULT_DECIMAL_FORMAT.format(value))
		
	@property
	def MaxVoltage(self) -> float:
		return float(self.__parent__.Query("SOUR:VOLT:PROT:LEV", f"(@{self.Address})"))
	@MaxVoltage.setter
	def MaxVoltage(self, value: float):
		value = float(value)
		self.__parent__.Write(f"SOUR:VOLT:PROT:LEV {str(value)},(@{self.Address})")
		if self.MaxVoltage != Output.CONVERT_TO_DEFAULT_DECIMAL_FORMAT(value):
			raise Exception("Error while setting the voltage protection value")

	@property
	def IsEnabled(self) -> bool:
		return bool(int(self.__parent__.Query("OUTP:STAT", f"(@{self.Address})")))
	@IsEnabled.setter
	def IsEnabled(self, value) -> bool:
		value = bool(value)
		self.__parent__.Write(f"OUTP:STAT {str(int(value))}", f",(@{self.Address})")
		newValue = self.IsEnabled
		if newValue != value:
			raise Exception("Error while en/dis-abling source")
		return newValue
	
	@property
	def Voltage(self) -> float:
		return float(self.__parent__.Query("SOUR:VOLT:LEV:IMM:AMPL", f"(@{self.Address})"))
	@Voltage.setter
	def Voltage(self, value: float):
		value = float(value)
		self.__parent__.Write(f"SOUR:VOLT:LEV:IMM:AMPL {str(value)},(@{self.Address})")
		currentSetVoltage = self.Voltage
		if currentSetVoltage != float(Output.DEFAULT_DECIMAL_FORMAT.format(value)):
			raise Exception("Error while setting the voltage")
		self.ClearProtection()
		self.IsProtectionRaised
		return currentSetVoltage
	
	@property
	def MaxCurrent(self) -> float:
		return float(self.__parent__.Query("SOUR:CURR:LEV:IMM:AMPL", f"(@{self.Address})"))
	@MaxCurrent.setter
	def MaxCurrent(self, value: float):
		value = float(value)
		self.__parent__.Write(f"SOUR:CURR:LEV:IMM:AMPL {str(value)},(@{self.Address})")
		currentSetCurrent = self.MaxCurrent
		if currentSetCurrent != float(Output.DEFAULT_DECIMAL_FORMAT.format(value)):
			raise Exception("Error while setting the over-current limit")
		self.ClearProtection()
		self.IsProtectionRaised
		return currentSetCurrent
	
	OVER_CURRENT_PROTECTION_ON_SETTING_CHANGE:str = 'SCH'
	OVER_CURRENT_PROTECTION_ALL_TIME:str = 'CCTR'
	@property
	def OverCurrentProtectionOnlyOnSettingsChange(self) -> bool:
		return self.__parent__.Query('SOUR:CURR:DEL:STAR', f"(@{self.Address})") == Output.OVER_CURRENT_PROTECTION_ON_SETTING_CHANGE
	@OverCurrentProtectionOnlyOnSettingsChange.setter
	def OverCurrentProtectionOnlyOnSettingsChange(self, value:bool) -> bool:
		value = Output.OVER_CURRENT_PROTECTION_ON_SETTING_CHANGE if value else Output.OVER_CURRENT_PROTECTION_ALL_TIME
		self.__parent__.Write(f"SOUR:CURR:DEL:STAR {value},(@{self.Address})")
		if self.OverCurrentProtectionOnlyOnSettingsChange != value:
			raise Exception("Error while setting over-current protection conditions")
		return value
		
	@property
	def IsOverCurrentProtectionEnabled(self) -> bool:
		return self.__parent__.Query('SOUR:CURR:PROT:STAT', f"(@{self.Address})") == 'ON'
	@IsOverCurrentProtectionEnabled.setter
	def IsOverCurrentProtectionEnabled(self, value: bool) -> bool:
		value = bool(value)
		self.__parent__.Write(f"SOUR:CURR:PROT:STAT {int(value)},(@{self.Address})")
		if self.IsOverCurrentProtectionEnabled != value:
			raise Exception("Error while setting over-current protection")
		return value
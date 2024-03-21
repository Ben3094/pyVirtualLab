from collections.abc import Iterator
from pyVirtualLab.VISAInstrument import Instrument, GetProperty, SetProperty
from aenum import Enum
from math import nan
from statistics import mean

class CalibrationFactorSetsDict(dict):
	__parentN191X__ = None
	def __init__(self, parentN191X):
		super().__init__()
		self.__parentN191X__ = parentN191X

	def __getKeys__(self) -> list[str]:
		return [key.split(',')[0] for key in self.__parentN191X__.Query("MEM:CAT:TABL").split(',"', 1)[1].split('","')]
	
	def __iter__(self) -> Iterator:
		return iter(self.__getKeys__())
	
	def __len__(self) -> int:
		return len(self.__getKeys__())
	
	def __contains__(self, _CalibrationFactorSetsDict__key: object) -> bool:
		return _CalibrationFactorSetsDict__key in self.__getKeys__()
	
	def __delitem__(self, _CalibrationFactorSetsDict__key) -> None:
		self.__parentN191X__.Write('MEM:CLE', f"\"{_CalibrationFactorSetsDict__key}\"")
	def __getitem__(self, _CalibrationFactorSetsDict__key) -> dict[float, float]:
		self.__parentN191X__.Write('MEM:TABL:SEL', f"\"{_CalibrationFactorSetsDict__key}\"")
		frequenciesTable = self.__parentN191X__.Query("MEM:TABL:FREQ").split(',')
		if frequenciesTable[0] != '':
			frequencies = [float(frequency) for frequency in frequenciesTable]
			gains = [float(gain) for gain in self.__parentN191X__.Query("MEM:TABL:GAIN").split(',')]
			return dict(zip(frequencies, gains))
		else:
			return dict()
	def __setitem__(self, _CalibrationFactorSetsDict__key, _CalibrationFactorSetsDict__value: dict[float, float]) -> None:
		if not _CalibrationFactorSetsDict__key in self:
			raise Exception("Calibration factor set does not exist")
		self.__parentN191X__.Write('MEM:TABL:SEL', f"\"{_CalibrationFactorSetsDict__key}\"")
		self.__parentN191X__.Write('MEM:TABL:FREQ', ','.join([str(key)+'hz' for key in _CalibrationFactorSetsDict__value.keys()]))
		self.__parentN191X__.Write('MEM:TABL:GAIN', ','.join([str(val) for val in [mean(list(_CalibrationFactorSetsDict__value.values()))] + list(_CalibrationFactorSetsDict__value.values())]))

	def __repr__(self) -> str:
		return str(["{0}: {1}".format(itemName, self[itemName]) for itemName in self])
class KeysightN191XSensor:
	__parentKeysightN191X__: Instrument = None
	__address__: int = None

	def __init__(self, parentKeysightN191X, address: int):
		self.__parentKeysightN191X__ = parentKeysightN191X
		self.__address__ = address

	def __isType__(self, type: str):
		return str(type(self))[0] == type[0]

	@property
	def CalibrationFactor(self) -> float:
		return float(self.__parentKeysightN191X__.Query(f"SENS{self.__address__}:CORR:GAIN1"))

	@property
	def Power(self) -> float:
		savedTimeout = self.__parentKeysightN191X__.Timeout
		self.__parentKeysightN191X__.Timeout = KeysightN191X.MEASURE_TIMEOUT
		measuredPower = float(self.__parentKeysightN191X__.Query(f"MEAS{self.__address__}"))
		self.__parentKeysightN191X__.Timeout = savedTimeout
		return measuredPower

	DEFAULT_FREQUENCY_FORMAT = "{:11.0f}"
	@property
	def Frequency(self) -> float:
		return float(self.__parentKeysightN191X__.Query(f"SENS{self.__address__}:FREQ"))
	@Frequency.setter
	def Frequency(self, value: float) -> float:
		self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:FREQ " + str(value))
		if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
			raise Exception("Error while setting the frequency")
		return self.Frequency

class SensorWithoutEEPROM(KeysightN191XSensor):
	def __init__(self, parentKeysightN191X, address: int):
		super().__init__(parentKeysightN191X, address)

	@property
	def AssociatedCalibrationFactorsSetName(self) -> str:
		name = self.__parentKeysightN191X__.Query(f"SENS{self.__address__}:CORR:CSET1:SEL")
		if name == '':
			return None
		else:
			return name
	@AssociatedCalibrationFactorsSetName.setter
	def AssociatedCalibrationFactorsSetName(self, value:str):
		if not value:
			self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:CORR:CSET1:STAT", '0')
		else:
			self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:CORR:CSET1:SEL", f"\"{value}\"")
			self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:CORR:CSET1:STAT", '1')

class ASensor(SensorWithoutEEPROM):
	def __init__(self, parentKeysightN1913A, address: int):
		super().__init__(parentKeysightN1913A, address)

class BSensor(SensorWithoutEEPROM):
	def __init__(self, parentKeysightN1913A, address: int):
		super().__init__(parentKeysightN1913A, address)

class DSensor(SensorWithoutEEPROM):
	def __init__(self, parentKeysightN1913A, address: int):
		super().__init__(parentKeysightN1913A, address)

class HSensor(SensorWithoutEEPROM):
	def __init__(self, parentKeysightN1913A, address: int):
		super().__init__(parentKeysightN1913A, address)

class SensorWithEEPROM(KeysightN191XSensor):
	def __init__(self, parentKeysightN191X, address: int):
		super().__init__(parentKeysightN191X, address)

	@property
	def IsAutoRangeEnabled(self) -> bool:
		return bool(int(self.__parentKeysightN191X__.Query(f"SENS{self.__address__}:POW:AC:RANG:AUTO")))
	@IsAutoRangeEnabled.setter
	def IsAutoRangeEnabled(self, value: bool):
		value = bool(value)
		self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:POW:AC:RANG:AUTO", str(int(value)))
		if self.IsAutoRangeEnabled != value:
			raise Exception("Error while setting auto range")

	@property
	def IsUpperRange(self) -> bool:
		return bool(int(self.__parentKeysightN191X__.Query(f"SENS{self.__address__}:POW:AC:RANG")))
	@IsUpperRange.setter
	def IsUpperRange(self, value: bool):
		if self.IsAutoRangeEnabled:
			raise Exception("Auto range is enabled")
		else:
			value = bool(value)
			self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:POW:AC:RANG", str(int(value)))
			if self.IsUpperRange != value:
				raise Exception("Error while setting range")

class U2000Sensor(SensorWithEEPROM):
	def __init__(self, parentKeysightN1913A, address: int):
		super().__init__(parentKeysightN1913A, address)

	# TODO: override __isType__

class ESensor(SensorWithEEPROM):
	def __init__(self, parentKeysightN1913A, address: int):
		super().__init__(parentKeysightN1913A, address)

	# TODO: override __isType__

class N8480Sensor(SensorWithEEPROM):
	def __init__(self, parentKeysightN1913A, address: int):
		super().__init__(parentKeysightN1913A, address)

	# TODO: override __isType__

class SensorType(Enum):
	A = ASensor
	B = BSensor
	D = DSensor
	H = HSensor
	U = U2000Sensor
	E = ESensor
	N = N8480Sensor

class KeysightN191X(Instrument):
	MEASURE_TIMEOUT = 40000

	def __init__(self, address):
		super(KeysightN191X, self).__init__(address)
		self.__sensors__ = dict()
		self.__calibrationFactorsSets__ = CalibrationFactorSetsDict(self)

	@property
	@GetProperty(float, 'CALC:LIM:LOW')
	def LowerPowerLimit(self, getMethodReturn) -> float:
		return getMethodReturn
	@LowerPowerLimit.setter
	@SetProperty(float, 'CALC:LIM:LOW')
	def LowerPowerLimit(self, value:float):
		pass
	@property
	@GetProperty(float, 'CALC:LIM:UPP')
	def UpperPowerLimit(self, getMethodReturn) -> float:
		return getMethodReturn
	@UpperPowerLimit.setter
	@SetProperty(float, 'CALC:LIM:UPP')
	def UpperPowerLimit(self, value:float):
		pass
	@property
	@GetProperty(bool, 'CALC:LIM:FAIL')
	def IsPowerLimitsTriggered(self, getMethodReturn) -> bool:
		return getMethodReturn

	MAX_SENSORS = 4
	@property
	def Sensors(self) -> dict[int, KeysightN191XSensor]:
		for address in range(1, KeysightN191X.MAX_SENSORS+1):
			try:
				type = self.Query(f"SERV:SENS{address}:TYPE")
				toUpdate = not address in self.__sensors__
				if not toUpdate:
					toUpdate = self.__sensors__[address].__isType__(type)
				if toUpdate:
					self.__sensors__[address] = SensorType[type[0]].value(self, address)
			except Exception:
				if address in self.__sensors__:
					del self.__sensors__[address]
		return self.__sensors__
	
	MAX_CALIBRATION_FACTORS_SETS = 20
	@property
	def CalibrationFactorsSets(self) -> CalibrationFactorSetsDict:
		return self.__calibrationFactorsSets__
	def RenameCalibrationFactorsSet(self, oldName, newName):
		self.Write('MEM:TABL:MOVE', f"\"{oldName}\",\"{newName}\"")
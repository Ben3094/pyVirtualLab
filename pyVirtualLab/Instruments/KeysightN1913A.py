from pyVirtualLab.VISAInstrument import Instrument
from aenum import Enum
from numpy import nan

class KeysightN1913ASensor:
    __parentKeysightN1913A__ = None
    __address__ = None

    def __init__(self, parentKeysightN1913A, address: int):
        self.__parentKeysightN1913A__ = parentKeysightN1913A
        self.__address__ = address

    def __isType__(self, type: str):
        return str(type(self))[0] == type[0]

    @property
    def CalibrationFactors(self) -> dict[float, float]:
        pass

    @property
    def Power(self) -> float:
        pass

    DEFAULT_FREQUENCY_FORMAT = "{:11.0f}"
    @property
    def Frequency(self) -> float:
        pass
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        pass

    @property
    def IsAutoRangeEnabled(self) -> bool:
        return bool(int(self.Query(f"SENS{self.__address__}:POW:AC:RANG:AUTO")))
    @IsAutoRangeEnabled.setter
    def IsAutoRangeEnabled(self, value: bool):
        value = bool(value)
        self.Write(f"SENS{self.__address__}:POW:AC:RANG:AUTO", str(int(value)))
        if self.IsAutoRangeEnabled != value:
            raise Exception("Error while setting auto range")

    @property
    def IsUpperRange(self) -> bool:
        return bool(int(self.Query(f"SENS{self.__address__}:POW:AC:RANG")))
    @IsUpperRange.setter
    def IsUpperRange(self, value: bool):
        if self.IsAutoRangeEnabled:
            raise Exception("Auto range is enabled")
        else:
            value = bool(value)
            self.Write(f"SENS{self.__address__}:POW:AC:RANG", str(int(value)))
            if self.IsUpperRange != value:
                raise Exception("Error while setting range")

class SensorWithoutEEPROM(KeysightN1913ASensor):
    def __init__(self, parentKeysightN1913A, address: int):
        super().__init__(parentKeysightN1913A, address)

    __calibrationFactors__ = dict()
    @property
    def CalibrationFactors(self) -> dict[float, float]:
        return self.__calibrationFactors__
    @CalibrationFactors.setter
    def CalibrationFactors(self, value: dict[float, float]) -> dict[float, float]:
        self.__calibrationFactors__ = value

    __frequency__ = nan
    @property
    def Frequency(self) -> float:
        return self.__frequency__
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        self.__frequency__ = value
        return self.Frequency

    @property
    def Power(self) -> float:
        closestFrequency, closestCalibrationFactor = min(self.CalibrationFactors, key=lambda x: abs(self.Frequency - x[0]))
        return float(self.Query(f"MEAS{self.__address__}")) * closestCalibrationFactor

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

class SensorWithEEPROM(KeysightN1913ASensor):
    def __init__(self, parentKeysightN1913A, address: int):
        super().__init__(parentKeysightN1913A, address)

    @property
    def CalibrationFactors(self) -> dict[float, float]:
        return self.__calibrationFactors__

    @property
    def Power(self) -> float:
        return float(self.Query(f"MEAS{self.__address__}"))

    @property
    def Frequency(self) -> float:
        return float(self.Query(f"SENS{self.__address__}:FREQ"))
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        self.Write(f"SENS{self.__address__}:FREQ " + str(value))
        if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
            raise Exception("Error while setting the frequency")
        return self.Frequency

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

class KeysightN1913A(Instrument):
    DEFAULT_TIMEOUT = 20000

    def __init__(self, address):
        super(KeysightN1913A, self).__init__(address, self.DEFAULT_TIMEOUT)

    __sensors__ = dict()
    MAX_SENSORS = 4
    @property
    def Sensors(self) -> dict[int, KeysightN1913ASensor]:
        for address in range(1, KeysightN1913A.MAX_SENSORS+1):
            try:
                type = self.Query(f"SERV:SENS{address}:TYPE")
                toUpdate = not self.__sensors__[address]
                if not toUpdate:
                   toUpdate = self.__sensors__[address].__isType__(type)
                if toUpdate:
                    self.__sensors__[address] = SensorType(type[0]).__init__(self, address)
            except Exception:
                if self.__sensors__[address]:
                    del self.__sensors__[address]
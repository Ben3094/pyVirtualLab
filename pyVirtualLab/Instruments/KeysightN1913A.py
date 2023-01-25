from pyVirtualLab.VISAInstrument import Instrument
from aenum import Enum
from math import nan

class KeysightN191XSensor:
    __parentKeysightN1913A__ = None
    __address__ = None

    def __init__(self, parentKeysightN191X, address: int):
        self.__parentKeysightN1913A__ = parentKeysightN191X
        self.__address__ = address

    def __isType__(self, type: str):
        return str(type(self))[0] == type[0]

    @property
    def CalibrationFactor(self) -> float:
        return float(self.__parentKeysightN1913A__.Query(f"CAL{self.__address__}:RCF"))

    @property
    def Power(self) -> float:
        pass
    def __measurePower__(self) -> float:
        savedTimeout = self.__parentKeysightN1913A__.VISATimeout
        self.__parentKeysightN1913A__.VISATimeout = KeysightN191X.MEASURE_TIMEOUT
        measuredPower = float(self.__parentKeysightN1913A__.Query(f"MEAS{self.__address__}"))
        self.__parentKeysightN1913A__.VISATimeout = savedTimeout
        return measuredPower

    DEFAULT_FREQUENCY_FORMAT = "{:11.0f}"
    @property
    def Frequency(self) -> float:
        pass
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        pass

class SensorWithoutEEPROM(KeysightN191XSensor):
    def __init__(self, parentKeysightN1913A, address: int):
        super().__init__(parentKeysightN1913A, address)
        self.CalibrationFactors = dict()

    __frequency__ = nan
    @property
    def Frequency(self) -> float:
        return self.__frequency__
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        self.__frequency__ = value
        return self.Frequency

    @KeysightN191XSensor.CalibrationFactor.setter
    def CalibrationFactor(self, value) -> float:
        value = float(value)
        self.__parentKeysightN1913A__.Write(f"CAL{self.__address__}:RCF", str(value))
        setValue = self.CalibrationFactor
        if value != setValue:
            raise Exception("Error while setting calibration factor")
        return self.CalibrationFactor

    @property
    def Power(self) -> float:
        self.CalibrationFactor = self.CalibrationFactors[min(self.CalibrationFactors.keys(), key=lambda k: abs(k-self.Frequency))]
        return self.__measurePower__()

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
    def __init__(self, parentKeysightN1913A, address: int):
        super().__init__(parentKeysightN1913A, address)

    @property
    def Power(self) -> float:
        return self.__measurePower__()

    @property
    def Frequency(self) -> float:
        return float(self.__parentKeysightN1913A__.Query(f"SENS{self.__address__}:FREQ"))
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        self.__parentKeysightN1913A__.Write(f"SENS{self.__address__}:FREQ " + str(value))
        if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
            raise Exception("Error while setting the frequency")
        return self.Frequency

    @property
    def IsAutoRangeEnabled(self) -> bool:
        return bool(int(self.__parentKeysightN1913A__.Query(f"SENS{self.__address__}:POW:AC:RANG:AUTO")))
    @IsAutoRangeEnabled.setter
    def IsAutoRangeEnabled(self, value: bool):
        value = bool(value)
        self.__parentKeysightN1913A__.Write(f"SENS{self.__address__}:POW:AC:RANG:AUTO", str(int(value)))
        if self.IsAutoRangeEnabled != value:
            raise Exception("Error while setting auto range")

    @property
    def IsUpperRange(self) -> bool:
        return bool(int(self.__parentKeysightN1913A__.Query(f"SENS{self.__address__}:POW:AC:RANG")))
    @IsUpperRange.setter
    def IsUpperRange(self, value: bool):
        if self.IsAutoRangeEnabled:
            raise Exception("Auto range is enabled")
        else:
            value = bool(value)
            self.__parentKeysightN1913A__.Write(f"SENS{self.__address__}:POW:AC:RANG", str(int(value)))
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
    SENSORS_DISCOVERY_TIMEOUT = 250
    MEASURE_TIMEOUT = 20000

    def __init__(self, address):
        super(KeysightN191X, self).__init__(address)
        self.__sensors__ = dict()

    __sensors__ = dict()
    MAX_SENSORS = 4
    @property
    def Sensors(self) -> dict[int, KeysightN191XSensor]:
        savedTimeout = self.VISATimeout
        self.VISATimeout = KeysightN191X.SENSORS_DISCOVERY_TIMEOUT
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
        self.VISATimeout = savedTimeout
        return self.__sensors__
from pyVirtualLab.VISAInstrument import Instrument
from aenum import Enum
from math import nan


class CalibrationFactorsSet:
    def __init__(self, parentKeysightN191X, name: str) -> None:
        self.__parentKeysightN191X__ = parentKeysightN191X
        self.__name__ = name

    @property
    def Address(self) -> int:
        return int(self.Query("MEM:STAT:DEF", f"\"{self.Name}\""))

    @property
    def Name(self) -> str:
        return self.__name__
    @Name.setter
    def Name(self, value: str) -> str:
        value = str(value)
        self.__parentKeysightN191X__.Write('MEM:TABL:MOVE', f"\"{self.Name}\",\"{value}\"")
        self.__name__ = value

    def Clear(self):
        self.__parentKeysightN191X__.Write("MEM:CLE", f"\"{self.Name}\"")

    @property
    def CalibrationFactors(self) -> dict[float, float]:
        self.__parentKeysightN191X__.Write("MEM:TABL:SEL", f"\"{self.Name}\"")
        frequencies = [float(frequency) for frequency in self.__parentKeysightN191X__.Query("MEM:TABL:FREQ").split(',')]
        gains = [float(gain) for gain in self.__parentKeysightN191X__.Query("MEM:TABL:GAIN").split(',')]
        return dict(zip(frequencies, gains))
    @CalibrationFactors.setter
    def CalibrationFactors(self, value: dict[float, float]) -> dict[float, float]:
        self.Clear()
        self.__parentKeysightN191X__.Write("MEM:TABL:SEL", f"\"{self.Name}\"")
        self.__parentKeysightN191X__.Write("MEM:TABL:FREQ", ','.join([str(key)+'hz' for key in value.keys()]))
        self.__parentKeysightN191X__.Write("MEM:TABL:GAIN", ','.join([str(val) for val in value.values()]))
        if value != self.CalibrationFactors:
            raise Exception(f"Error while setting \"{self.Name}\" calibration factors")

class KeysightN191XSensor:
    __parentKeysightN191X__ = None
    __address__ = None

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
        pass
    def __measurePower__(self) -> float:
        savedTimeout = self.__parentKeysightN191X__.VISATimeout
        self.__parentKeysightN191X__.VISATimeout = KeysightN191X.MEASURE_TIMEOUT
        measuredPower = float(self.__parentKeysightN191X__.Query(f"MEAS{self.__address__}"))
        self.__parentKeysightN191X__.VISATimeout = savedTimeout
        return measuredPower

    DEFAULT_FREQUENCY_FORMAT = "{:11.0f}"
    @property
    def Frequency(self) -> float:
        pass
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        pass

class SensorWithoutEEPROM(KeysightN191XSensor):
    def __init__(self, parentKeysightN191X, address: int):
        super().__init__(parentKeysightN191X, address)
        self.CalibrationFactors = dict()

    @property
    def AssociatedCalibrationFactorsSet(self) -> CalibrationFactorsSet:
        name = self.__parentKeysightN191X__.Query(f"SENS{self.__address__}:CORR:CSET1:SEL")
        if name == '':
            return None
        else:
            return self.__parentKeysightN191X__.CalibrationFactorsSets[name]
    @AssociatedCalibrationFactorsSet.setter
    def AssociatedCalibrationFactorsSet(self, calibrationFactorsSet: CalibrationFactorsSet=None):
        if calibrationFactorsSet == None:
            self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:CORR:CSET1:STAT", False)
        else:
            self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:CORR:CSET1:SEL", calibrationFactorsSet.Name)
            self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:CORR:CSET1:STAT", True)

    __frequency__ = nan
    @property
    def Frequency(self) -> float:
        if self.AssociatedCalibrationFactorsSet != None:
            self.__frequency__ = float(self.__parentKeysightN191X__.Query(f"SENS{self.__address__}:FREQ"))
        return self.__frequency__
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        if self.AssociatedCalibrationFactorsSet != None:
            self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:FREQ " + str(value))
            if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
                raise Exception("Error while setting the frequency")
        self.__frequency__ = value
        return self.Frequency

    @KeysightN191XSensor.CalibrationFactor.setter
    def CalibrationFactor(self, value) -> float:
        value = float(value)
        self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:CORR:GAIN1", str(value))
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
    def __init__(self, parentKeysightN191X, address: int):
        super().__init__(parentKeysightN191X, address)

    @property
    def Power(self) -> float:
        return self.__measurePower__()

    @property
    def Frequency(self) -> float:
        return float(self.__parentKeysightN191X__.Query(f"SENS{self.__address__}:FREQ"))
    @Frequency.setter
    def Frequency(self, value: float) -> float:
        self.__parentKeysightN191X__.Write(f"SENS{self.__address__}:FREQ " + str(value))
        if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
            raise Exception("Error while setting the frequency")
        return self.Frequency

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
    SENSORS_DISCOVERY_TIMEOUT = 250
    MEASURE_TIMEOUT = 20000

    def __init__(self, address):
        super(KeysightN191X, self).__init__(address)
        self.__sensors__ = dict()
        self.__calibrationFactorsSets__ = dict()

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

    MAX_CALIBRATION_FACTORS_SETS = 20
    @property
    def CalibrationFactorsSets(self) -> dict[str, CalibrationFactorsSet]:
        self.__calibrationFactorsSets__.clear()
        setsNames = self.Query("MEM:CAT:TABL").split('","')
        for setName in setsNames:
            if '"' in setName:
                setName = setName.split('"')[1]
            setName = setName.split(',')[0]
            set = CalibrationFactorsSet(self, setName)
            self.__calibrationFactorsSets__[set.Name] = set
        return self.__calibrationFactorsSets__
    @CalibrationFactorsSets.setter
    def CalibrationFactorsSets(self, value: dict[str, CalibrationFactorsSet]):
        if len(value) > KeysightN191X.MAX_CALIBRATION_FACTORS_SETS:
            raise Exception(f"More than {KeysightN191X.MAX_CALIBRATION_FACTORS_SETS} calibration factors sets")

        oldNames = [name for name in value if name in self.CalibrationFactorsSets]
        for alreadyPresentName in oldNames:
            oldVersion = self.CalibrationFactorsSets[alreadyPresentName]
            newVersion = value[alreadyPresentName]
            if oldVersion.CalibrationFactors != newVersion.CalibrationFactors:
                oldVersion.CalibrationFactors = newVersion.CalibrationFactors

        deletedNames = [name for name in self.CalibrationFactorsSets if name not in value]
        newNames = [name for name in value if name not in self.CalibrationFactorsSets]
        for deletedName in deletedNames:
            newName = newNames.pop()
            self.CalibrationFactorsSets[deletedName].Name = newName
            self.CalibrationFactorsSets[newName].CalibrationFactors = value[newName].CalibrationFactors
        for newName in newNames:
            self.Write('MEM:TABL:SEL', newName)
            self.CalibrationFactorsSets[newName].CalibrationFactors = value[newName].CalibrationFactors
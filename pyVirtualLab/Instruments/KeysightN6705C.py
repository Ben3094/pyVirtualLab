from enum import Flag, unique
from pyVirtualLab.VISAInstrument import Source

@unique
class Condition(Flag):
    OK = 0
    OverVoltage = 1
    OverCurrent = 2
    PowerFailure = 4
    PositivePowerLimitExceeded = 8
    OverTemperature = 16
    NegativePowerLimitExceeded = 32
    PositiveVoltageLimitExceeded = 64
    PositiveVoltageOrCurrentLimit = 128
    NegativeVoltageOrCurrentLimit = 256
    ExternalInhibit = 512
    Unregulated = 1024
    CoupledProtection = 2048
    DetectedOscillation = 4096


class Output():
    def __init__(self, parentKeysightN6705C, address):
        self.__parent__ = parentKeysightN6705C
        self.__address__ = address
        self.__model__ = str(self.__parent__.Query("SYST:CHAN:MOD", f"(@{self.Address})"))
        self.__options__ = str(self.__parent__.Query("SYST:CHAN:OPT", f"(@{self.Address})"))
        self.__serialNumber__ = str(self.__parent__.Query("SYST:CHAN:SER", f"(@{self.Address})"))

    @property
    def Address(self) -> int:
        return self.__address__

    @property
    def Model(self) -> str:
        return self.__model__

    @property
    def Options(self) -> str:
        return self.__options__

    @property
    def SerialNumber(self) -> str:
        return self.__serialNumber__

    @property
    def Conditions(self) -> Condition:
        return Condition(int(self.__parent__.Query("STAT:QUES:COND", f"(@{self.Address})")))

    DEFAULT_FORMAT = "{:2.6f}"
    @property
    def MaxVoltage(self) -> float:
        return float(self.__parent__.Query("SOUR:VOLT:PROT:LEV", f"(@{self.Address})"))
    @MaxVoltage.setter
    def MaxVoltage(self, value):
        value = float(value)
        self.__parent__.Write(f"SOUR:VOLT:PROT:LEV {str(value)},(@{self.Address})")
        self.__parent__.Write(f"SOUR:VOLT:PROT:STAT ON,(@{self.Address})")
        if self.MaxVoltage != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the voltage protection value")

    @property
    def Voltage(self) -> float:
        return float(self.__parent__.Query("SOUR:VOLT:LEV:IMM:AMPL", f"(@{self.Address})"))
    @Voltage.setter
    def Voltage(self, value):
        value = float(value)
        self.__parent__.Write(f"SOUR:VOLT:LEV:IMM:AMPL {str(value)},(@{self.Address})")
        if self.Voltage != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the voltage")
        self.__parent__.Write(f"OUTP:PROT:CLE (@{self.Address})")
        if self.Conditions == Condition.OverVoltage:
            raise Exception("Voltage set is superior or equal to maximum voltage")

    @property
    def MeasuredVoltage(self):
        return float(self.__parent__.Query('MEAS:SCAL:VOLT:DC', f"(@{self.Address})").lstrip('[').rstrip(']'))

    @property
    def MeasuredCurrent(self):
        return float(self.__parent__.Query('MEAS:SCAL:CURR:DC', f"(@{self.Address})").lstrip('[').rstrip(']'))

    @property
    def MaxCurrent(self) -> float:
        return float(self.__parent__.Query("SOUR:CURR:LEV:IMM:AMPL", f"(@{self.Address})"))
    @MaxCurrent.setter
    def MaxCurrent(self, value):
        value = float(value)
        self.__parent__.Write(f"SOUR:CURR:LEV:IMM:AMPL {str(value)},(@{self.Address})")
        if self.MaxCurrent != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the maximum current")
        self.__parent__.Write(f"SOUR:CURR:PROT:STAT ON,(@{self.Address})")
        self.__parent__.Write(f"OUTP:PROT:CLE (@{self.Address})")
        if self.Conditions == Condition.OverCurrent:
            raise Exception("Current set is superior or equal to maximum current")

    @property
    def IsEnabled(self) -> bool:
        return bool(int(self.__parent__.Query(":OUTP:STAT", f"(@{self.Address})")))
    @IsEnabled.setter
    def IsEnabled(self, value):
        value = bool(value)
        self.__parent__.Write(f"OUTP:STAT {str(int(value))}", f",(@{self.Address})")
        if self.IsEnabled != value:
            raise Exception("Error while en/dis-abling source")

class N6734B(Output):
    def __init__(self, parentKeysightN6705C, address):
        super(N6734B, self).__init__(parentKeysightN6705C, address)

class KeysightN6705C(Source):
    def __init__(self, address):
        super(KeysightN6705C, self).__init__(address)
        self.__outputs__ = None

    MAX_OUTPUTS = 4

    @property
    def Outputs(self):
        if self.__outputs__ == None:
            self.__outputs__ = dict()
            address = 0
            connectedOutputs = int(self.Query('SYST:CHAN:COUN'))
            while address <= KeysightN6705C.MAX_OUTPUTS and len(self.Outputs) < connectedOutputs:
                address += 1
                output = None
                try:
                    output = globals()[str(self.Query('SYST:CHAN:MOD', f"(@{address})")).replace('\n','')]
                except: pass
                if output == None:
                    output = Output
                self.Outputs[address] = output(self, address)
        return self.__outputs__
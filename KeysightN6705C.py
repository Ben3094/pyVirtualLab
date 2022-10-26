from enum import Flag, unique
from VISAInstrument import Source

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
        self._parent = parentKeysightN6705C
        self._address = address
        self._model = str(self._parent.Query(f"SYST:CHAN:MOD? (@{self.Address})"))
        self._options = str(self._parent.Query(f"SYST:CHAN:OPT? (@{self.Address})"))
        self._serialNumber = str(self._parent.Query(f"SYST:CHAN:SER? (@{self.Address})"))

    @property
    def Address(self) -> int:
        return self._address

    @property
    def Model(self) -> str:
        return self._model

    @property
    def Options(self) -> str:
        return self._options

    @property
    def SerialNumber(self) -> str:
        return self._serialNumber

    @property
    def Conditions(self) -> Condition:
        return Condition(int(self._parent.Query(f"STAT:QUES:COND? (@{self.Address})")))

    DEFAULT_FORMAT = "{:2.6f}"
    @property
    def MaxVoltage(self) -> float:
        return float(self._parent.Query(f"SOUR:VOLT:PROT:LEV? (@{self.Address})"))
    @MaxVoltage.setter
    def MaxVoltage(self, value):
        value = float(value)
        self._parent.Write(f"SOUR:VOLT:PROT:LEV {str(value)},(@{self.Address})")
        self._parent.Write(f"SOUR:VOLT:PROT:STAT ON,(@{self.Address})")
        if self.MaxVoltage != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the voltage protection value")

    @property
    def Voltage(self) -> float:
        return float(self._parent.Query(f"SOUR:VOLT:LEV:IMM:AMPL? (@{self.Address})"))
    @Voltage.setter
    def Voltage(self, value):
        value = float(value)
        self._parent.Write(f"SOUR:VOLT:LEV:IMM:AMPL {str(value)},(@{self.Address})")
        if self.Voltage != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the voltage")
        self._parent.Write(f"OUTP:PROT:CLE (@{self.Address})")
        if self.Conditions == Condition.OverVoltage:
            raise Exception("Voltage set is superior or equal to maximum voltage")

    @property
    def MaxCurrent(self) -> float:
        return float(self._parent.Query(f"SOUR:CURR:LEV:IMM:AMPL? (@{self.Address})"))
    @MaxCurrent.setter
    def MaxCurrent(self, value):
        value = float(value)
        self._parent.Write(f"SOUR:CURR:LEV:IMM:AMPL {str(value)},(@{self.Address})")
        if self.MaxCurrent != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the maximum current")
        self._parent.Write(f"SOUR:CURR:PROT:STAT ON,(@{self.Address})")
        self._parent.Write(f"OUTP:PROT:CLE (@{self.Address})")
        if self.Conditions == Condition.OverCurrent:
            raise Exception("Current set is superior or equal to maximum current")

    @property
    def IsEnabled(self) -> bool:
        return bool(int(self._parent.Query(f":OUTP:STAT? (@{self.Address})")))
    @IsEnabled.setter
    def IsEnabled(self, value):
        value = bool(value)
        self._parent.Write(f"OUTP:STAT {str(int(value))},(@{self.Address})")
        if self.IsEnabled != value:
            raise Exception("Error while en/dis-abling source")

class N6734B(Output):
    def __init__(self, parentKeysightN6705C, address):
        super(N6734B, self).__init__(parentKeysightN6705C, address)

class KeysightN6705C(Source):
    def __init__(self, address):
        super(KeysightN6705C, self).__init__(address)
        self.Outputs = list()
        self._indexOutputs()

    MAX_OUTPUTS = 4

    def _indexOutputs(self):
        address = 0
        connectedOutputs = int(self.Query('SYST:CHAN:COUN?'))
        while address <= KeysightN6705C.MAX_OUTPUTS and len(self.Outputs) < connectedOutputs:
            address += 1
            try:
                output = globals()[str(self.Query(f'SYST:CHAN:MOD? (@{address})')).replace('\n','')]
                if output == None:
                    output = Output
                self.Outputs.append(output(self, address))
            except: pass
from VISAInstrument import Source

class AgilentE3642A(Source):
    def __init__(self, address):
        super(AgilentE3642A, self).__init__(address)
        self.MaxVoltage = self.DEFAULT_MAX_VOLTAGE

    def _abort(self):
        self.IsEnabled = False

    DEFAULT_FORMAT = "{:2.6f}"
    DEFAULT_MAX_VOLTAGE = 8
    @property
    def MaxVoltage(self):
        return float(self._instr.query("SOUR:VOLT:PROT:LEV?"))
    @MaxVoltage.setter
    def MaxVoltage(self, value):
        self._instr.write("SOUR:VOLT:PROT:LEV " + str(value))
        if self.MaxVoltage != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the voltage protection value")

    @property
    def Voltage(self):
        return float(self._instr.query("SOUR:VOLT:LEV:IMM:AMPL?"))
    @Voltage.setter
    def Voltage(self, value):
        self._instr.write("SOUR:VOLT:LEV:IMM:AMPL " + str(value))
        if self.Voltage != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the voltage")
        self._instr.write("SOUR:VOLT:PROT:CLE")
        self._instr.write("SOUR:VOLT:PROT:CLE")
        if (bool(int(self._instr.query("SOUR:VOLT:PROT:TRIP?")))):
            raise Exception("Voltage set is superior or equal to maximum voltage")


    @property
    def Current(self):
        return float(self._instr.query("SOUR:CURR:LEV:IMM:AMPL?"))

    @property
    def IsEnabled(self):
        return bool(int(self._instr.query("OUTP:STAT?")))
    @IsEnabled.setter
    def IsEnabled(self, value):
        value = int(bool(value))
        self._instr.write("OUTP:STAT " + str(value))
        if self.IsEnabled != value:
            raise Exception("Error while en/dis-abling source")

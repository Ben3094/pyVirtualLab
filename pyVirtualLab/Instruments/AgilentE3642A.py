from pyVirtualLab.VISAInstrument import Source
import re as regex

class AgilentE3642A(Source):
    DEFAULT_TIMEOUT = 2000

    def __init__(self, address: str):
        super(AgilentE3642A, self).__init__(address, self.DEFAULT_TIMEOUT)

    def _abort(self):
        self.IsEnabled = False

    LOW_VOLTAGE_RANGE_HIGH_LIMIT = 8
    @property
    def HighVoltageRange(self) -> float:
        return float(regex.findall('P(\d+)V', self.Query("SOUR:VOLT:RANG"))[0]) > AgilentE3642A.LOW_VOLTAGE_RANGE_HIGH_LIMIT
    @HighVoltageRange.setter
    def HighVoltageRange(self, value: float):
        self.Write("SOUR:VOLT:RANG " + ('HIGH' if value else 'LOW'))
        if self.HighVoltageRange != value:
            raise Exception("Error while setting the voltage range")

    DEFAULT_FORMAT = "{:2.6f}"
    DEFAULT_MAX_VOLTAGE = 8
    @property
    def MaxVoltage(self) -> float:
        return float(self.Query("SOUR:VOLT:PROT:LEV"))
    @MaxVoltage.setter
    def MaxVoltage(self, value: float):
        self.Write(f"SOUR:VOLT:PROT:LEV {str(value)}")
        if self.MaxVoltage != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the voltage protection value")

    @property
    def Voltage(self) -> float:
        return float(self.Query("SOUR:VOLT:LEV:IMM:AMPL"))
    @Voltage.setter
    def Voltage(self, value: float):
        value = float(value)

        if not self.HighVoltageRange and value > AgilentE3642A.LOW_VOLTAGE_RANGE_HIGH_LIMIT:
            raise Exception('Increase the voltage range to high first')

        self.Write("SOUR:VOLT:LEV:IMM:AMPL " + str(value))
        if self.Voltage != float(self.DEFAULT_FORMAT.format(value)):
            raise Exception("Error while setting the voltage")
        self.Write("SOUR:VOLT:PROT:CLE")
        self.Write("SOUR:VOLT:PROT:CLE")
        if (bool(int(self.Query("SOUR:VOLT:PROT:TRIP")))):
            raise Exception("Voltage set is superior or equal to maximum voltage")
    
    @property
    def MeasuredVoltage(self) -> float:
        return float(self.Query('MEAS:SCAL:VOLT:DC'))

    @property
    def Current(self) -> float:
        return float(self.Query("SOUR:CURR:LEV:IMM:AMPL"))
    
    @property
    def MeasuredCurrent(self) -> float:
        return float(self.Query('MEAS:SCAL:CURR:DC'))

    @property
    def IsEnabled(self) -> bool:
        return bool(int(self.Query("OUTP:STAT")))
    @IsEnabled.setter
    def IsEnabled(self, value: bool):
        value = int(bool(value))
        self.Write("OUTP:STAT " + str(value))
        if self.IsEnabled != value:
            raise Exception("Error while en/dis-abling source")

from pyVirtualLab.VISAInstrument import Instrument

class KeysightN1913A(Instrument):
    DEFAULT_TIMEOUT = 20000

    def __init__(self, address):
        super(KeysightN1913A, self).__init__(address, self.DEFAULT_TIMEOUT)

    @property
    def Power(self) -> float:
        return float(self.Query("MEAS"))

    @property
    def IsAutoRangeEnabled(self) -> bool:
        return bool(int(self.Query('SENS:POW:AC:RANG:AUTO')))
    @IsAutoRangeEnabled.setter
    def IsAutoRangeEnabled(self, value: bool):
        value = bool(value)
        self.Write('SENS:POW:AC:RANG:AUTO', str(int(value)))
        if self.IsAutoRangeEnabled != value:
            raise Exception("Error while setting auto range")

    @property
    def IsUpperRange(self) -> bool:
        return bool(int(self.Query('SENS:POW:AC:RANG')))
    @IsUpperRange.setter
    def IsUpperRange(self, value: bool):
        if self.IsAutoRangeEnabled:
            raise Exception("Auto range is enabled")
        else:
            value = bool(value)
            self.Write('SENS:POW:AC:RANG', str(int(value)))
            if self.IsUpperRange != value:
                raise Exception("Error while setting range")

    DEFAULT_FREQUENCY_FORMAT = "{:11.0f}"
    @property
    def Frequency(self) -> float:
        return float(self.Query("SENS:FREQ"))
    @Frequency.setter
    def Frequency(self, value: float):
        self.Write("SENS:FREQ " + str(value))
        if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
            raise Exception("Error while setting the frequency")

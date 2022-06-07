from VISAInstrument import VISAInstrument

class KeysightN1913A(VISAInstrument):
    DEFAULT_TIMEOUT = 20000

    def __init__(self, address):
        super(KeysightN1913A, self).__init__(address)
        self._instr.timeout = self.DEFAULT_TIMEOUT

    @property
    def Power(self):
        return float(self._instr.query("MEAS?"))

    DEFAULT_FREQUENCY_FORMAT = "{:11.0f}"
    @property
    def Frequency(self):
        return float(self._instr.query("SENS:FREQ?"))
    @Frequency.setter
    def Frequency(self, value):
        self._instr.write("SENS:FREQ " + str(value))
        if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
            raise Exception("Error while setting the frequency")

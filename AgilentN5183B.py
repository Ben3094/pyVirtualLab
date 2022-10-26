import math
from VISAInstrument import Source

class AgilentN5183B(Source):
    def __init__(self, address):
        super(AgilentN5183B, self).__init__(address)
        self.MaxPower = self.DEFAULT_MAX_POWER

    def _abort(self):
        self.IsEnabled = False

    DEFAULT_POWER_FORMAT = "{:2.2f}"
    DEFAULT_MAX_POWER = 30
    @property
    def MaxPower(self):
        return float(self.Query("SOUR:POW:USER:MAX"))
    @MaxPower.setter
    def MaxPower(self, value):
        if value == +math.inf:
            self.Write("SOUR:POW:USER:ENAB OFF")
        else:
            self.Write("SOUR:POW:USER:MAX " + str(value))
            if self.MaxPower != float(self.DEFAULT_POWER_FORMAT.format(value)):
                raise Exception("Error while setting the power protection value")
            self.Write("SOUR:POW:USER:ENAB ON")
            if not bool(int(self.Query("SOUR:POW:USER:ENAB"))):
                raise Exception("Error while setting the power protection feature")

    @property
    def Power(self):
        return float(self.Query("SOUR:POW:LEV:IMM:AMPL"))
    @Power.setter
    def Power(self, value):
        self.Write("SOUR:POW:LEV:IMM:AMPL " + str(value))
        if self.Power != float(self.DEFAULT_POWER_FORMAT.format(value)):
            raise Exception("Error while setting the power")

    DEFAULT_FREQUENCY_FORMAT = "{:11.0f}"
    @property
    def Frequency(self):
        return float(self.Query("SOUR:FREQ:FIX"))
    @Frequency.setter
    def Frequency(self, value):
        self.Write("SOUR:FREQ:FIX " + str(value))
        if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
            raise Exception("Error while setting the frequency")

    @property
    def IsModulationEnabled(self):
        return bool(int(self.Query("OUTP:MOD:STAT")))
    @IsModulationEnabled.setter
    def IsModulationEnabled(self, value):
        value = int(bool(value))
        self.Write("OUTP:MOD:STAT " + str(value))
        if self.IsEnabled != value:
            raise Exception("Error while en/dis-abling source")

    @property
    def IsEnabled(self):
        return bool(int(self.Query("OUTP:STAT")))
    @IsEnabled.setter
    def IsEnabled(self, value):
        value = int(bool(value))
        self.Write("OUTP:STAT " + str(value))
        if self.IsEnabled != value:
            raise Exception("Error while en/dis-abling source")

    def LoadCorrection(self, frequencies, gains):
        frequencies = list(frequencies)
        gains = list(gains)
        frequenciesLength = len(frequencies)
        if (frequenciesLength != len(gains)):
            raise Exception('Arrays must be of the same length')
        self.Write("SOUR:CORR:FLAT:PRES")
        for index in range(0, frequenciesLength):
            self.Write("SOUR:CORR:FLAT:PAIR " + str(frequencies[index]) + ',' + str(gains[index]))

    def ClearCorrection(self):
        self.Write("SOUR:CORR:FLAT:LOAD TMP")
        self.Write("SOUR:CORR:FLAT:PRES")

    @property
    def IsCorrectionEnabled(self):
        return bool(int(self.Query("SOUR:CORR:STAT")))
    @IsCorrectionEnabled.setter
    def IsCorrectionEnabled(self, value):
        value = int(bool(value))
        self.Write("SOUR:CORR:STAT " + str(value))
        if self.IsCorrectionEnabled != value:
            raise Exception("Error while en/dis-abling flatness correction")
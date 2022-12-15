import math
from aenum import Enum
from pyVirtualLab.VISAInstrument import Source

class OutSignal(Enum):
    Sweep = 'SWE'
    SourceSettled = 'SETT'
    PulseVideo = 'PVID'
    PulseSync = 'PSYN'
    LXI = 'LXI'
    Pulse = 'PULS'
    Sweep8757DCompatible = 'SW8757'
    SweepStart = 'SRUN'
    Trigger1In = 'TRIG1'
    Trigger2In = 'TRIG2'
    SweepEnd = 'SFD'
    Disconnected = 'NONE'

class AgilentN5183B(Source):
    def __init__(self, address: str):
        super(AgilentN5183B, self).__init__(address, 20000)

    def _abort(self):
        self.IsEnabled = False

    DEFAULT_POWER_FORMAT = "{:2.2f}"
    DEFAULT_MAX_POWER = 30
    @property
    def MaxPower(self) -> float:
        return float(self.Query("SOUR:POW:USER:MAX"))
    @MaxPower.setter
    def MaxPower(self, value: float):
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
    def Power(self) -> float:
        return float(self.Query("SOUR:POW:LEV:IMM:AMPL"))
    @Power.setter
    def Power(self, value: float):
        self.Write("SOUR:POW:LEV:IMM:AMPL " + str(value))
        if self.Power != float(self.DEFAULT_POWER_FORMAT.format(value)):
            raise Exception("Error while setting the power")

    DEFAULT_FREQUENCY_FORMAT = "{:11.0f}"
    @property
    def Frequency(self) -> float:
        return float(self.Query("SOUR:FREQ:FIX"))
    @Frequency.setter
    def Frequency(self, value: float):
        self.Write("SOUR:FREQ:FIX " + str(value))
        if self.Frequency != float(self.DEFAULT_FREQUENCY_FORMAT.format(value)):
            raise Exception("Error while setting the frequency")

    @property
    def IsModulationEnabled(self) -> bool:
        return bool(int(self.Query("OUTP:MOD:STAT")))
    @IsModulationEnabled.setter
    def IsModulationEnabled(self, value: bool):
        value = int(bool(value))
        self.Write("OUTP:MOD:STAT " + str(value))
        if self.IsEnabled != value:
            raise Exception("Error while en/dis-abling source")

    @property
    def IsEnabled(self) -> bool:
        return bool(int(self.Query("OUTP:STAT")))
    @IsEnabled.setter
    def IsEnabled(self, value: bool):
        value = int(bool(value))
        self.Write("OUTP:STAT " + str(value))
        if self.IsEnabled != value:
            raise Exception("Error while en/dis-abling source")

    def LoadCorrection(self, frequencies: list, gains: list):
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
    def IsCorrectionEnabled(self) -> bool:
        return bool(int(self.Query('SOUR:CORR:STAT')))
    @IsCorrectionEnabled.setter
    def IsCorrectionEnabled(self, value: bool):
        value = int(bool(value))
        self.Write('SOUR:CORR:STAT', str(value))
        if self.IsCorrectionEnabled != value:
            raise Exception("Error while en/dis-abling flatness correction")

    @property
    def IsLowFrequencyOutputEnabled(self) -> bool:
        return bool(int(self.Query('SOUR:LFO:STAT')))
    @IsLowFrequencyOutputEnabled.setter
    def IsLowFrequencyOutputEnabled(self, value: bool):
        value = int(bool(value))
        self.Write('SOUR:LFO:STAT', str(value))
        if self.IsCorrectionEnabled != value:
            raise Exception("Error while en/dis-abling low frequency output")

    BANNED_SWEEP_OUT_SIGNAL = [
        OutSignal.LXI,
        OutSignal.Pulse,
        OutSignal.Trigger1In,
        OutSignal.Trigger2In,
        OutSignal.Disconnected
    ]
    @property
    def SweepOutSignal(self) -> OutSignal:
        return OutSignal(self.Query('ROUT:CONN:SOUT'))
    @SweepOutSignal.setter
    def SweepOutSignal(self, value: OutSignal):
        value = OutSignal(value)
        if value in AgilentN5183B.BANNED_SWEEP_OUT_SIGNAL:
            raise Exception('This type of signal is not allowed for this connector')
        self.Write('ROUT:CONN:SOUT', str(value.value))
        if self.SweepOutSignal != value:
            raise Exception("Error while setting this connector out signal")

    BANNED_TRIGGER1_OUT_SIGNAL = [
        OutSignal.Sweep8757DCompatible,
        OutSignal.SweepStart,
        OutSignal.Trigger1In
    ]
    @property
    def Tigger1OutSignal(self) -> OutSignal:
        return OutSignal(self.Query('ROUT:CONN:TRIGger1:OUTP'))
    @Tigger1OutSignal.setter
    def Tigger1OutSignal(self, value: OutSignal):
        value = OutSignal(value)
        if value in AgilentN5183B.BANNED_TRIGGER1_OUT_SIGNAL:
            raise Exception('This type of signal is not allowed for this connector')
        self.Write('ROUT:CONN:TRIGger1:OUTP', str(value.value))
        if self.Tigger1OutSignal != value:
            raise Exception("Error while setting this connector out signal")

    BANNED_TRIGGER2_OUT_SIGNAL = [
        OutSignal.Sweep8757DCompatible,
        OutSignal.SweepStart,
        OutSignal.Trigger2In
    ]
    @property
    def Tigger2OutSignal(self) -> OutSignal:
        return OutSignal(self.Query('ROUT:CONN:TRIGger2:OUTP'))
    @Tigger2OutSignal.setter
    def Tigger2OutSignal(self, value: OutSignal):
        value = OutSignal(value)
        if value in AgilentN5183B.BANNED_TRIGGER2_OUT_SIGNAL:
            raise Exception('This type of signal is not allowed for this connector')
        self.Write('ROUT:CONN:TRIGger2:OUTP', str(value.value))
        if self.Tigger2OutSignal != value:
            raise Exception("Error while setting this connector out signal")

'''If the LF out port is connected to sweep out port to get a unique out trig port,
this "helping" static method set the sweep out connector to allow the LF out signal to pass through.'''
def SetLFOutPassThroughSweepOut(agilentN5183B: AgilentN5183B):
    agilentN5183B.SweepOutSignal = OutSignal.SourceSettled
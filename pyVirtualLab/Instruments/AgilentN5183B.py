import math
from aenum import Enum
from numpy import log10, linspace, logspace
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

class TriggerSource(Enum):
    VISACommand = 'BUS'
    Immediate = 'IMM'
    Trigger1 = 'TRIG'
    Trigger2 = 'TRIG2'
    Pulse = 'PULS'
    PulseVideo = 'PVID'
    PulseSync = 'PSYN'
    TriggerKey = 'KEY'
    Timer = 'TIM'
    Off = 'MAN'

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

    @property
    def Frequency(self) -> float:
        return float(self.Query('SOUR:FREQ:FIX'))
    @Frequency.setter
    def Frequency(self, value: float):
        value = round(value, 2)
        self.Write('SOUR:FREQ:FIX', str(value))
        if self.Frequency != value:
            raise Exception("Error while setting the frequency")

    @property
    def FrequencyMultiplier(self) -> int:
        return int(self.Query('SOUR:FREQ:MULT'))
    @FrequencyMultiplier.setter
    def FrequencyMultiplier(self, value: int) -> int:
        value = int(value)
        self.Write('SOUR:FREQ:MULT', str(value))
        if self.FrequencyMultiplier != value:
            raise Exception("Error while setting the frequency multiplier")
        return value

    @property
    def IsModulationEnabled(self) -> bool:
        return bool(int(self.Query("OUTP:MOD:STAT")))
    @IsModulationEnabled.setter
    def IsModulationEnabled(self, value: bool):
        value = int(bool(value))
        self.Write("OUTP:MOD:STAT " + str(value))
        if self.IsModulationEnabled != value:
            raise Exception("Error while en/dis-abling modulation")

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
    def IsCorrectionEnabled(self, value: bool) -> bool:
        value = int(bool(value))
        self.Write('SOUR:CORR:STAT', str(value))
        if self.IsCorrectionEnabled != value:
            raise Exception("Error while en/dis-abling flatness correction")
        return value

    SWEEP_ON_MODE = 'LIST'
    SWEEP_OFF_MODE = 'FIX'
    @property
    def IsFrequencySweepEnabled(self) -> bool:
        return self.Query('SOUR:FREQ:MODE') == AgilentN5183B.SWEEP_ON_MODE
    @IsFrequencySweepEnabled.setter
    def IsFrequencySweepEnabled(self, value: bool) -> bool:
        value = bool(value)
        self.Write('SOUR:FREQ:MODE', AgilentN5183B.SWEEP_ON_MODE if value else AgilentN5183B.SWEEP_OFF_MODE)
        if self.IsFrequencySweepEnabled != value:
            raise Exception('Error while en/dis-abling frequency sweep')
        return value
    @property
    def IsPowerSweepEnabled(self) -> bool:
        return self.Query('SOUR:POW:MODE') == AgilentN5183B.SWEEP_ON_MODE
    @IsPowerSweepEnabled.setter
    def IsPowerSweepEnabled(self, value: bool) -> bool:
        value = bool(value)
        self.Write('SOUR:POW:MODE', AgilentN5183B.SWEEP_ON_MODE if value else AgilentN5183B.SWEEP_OFF_MODE)
        if self.IsPowerSweepEnabled != value:
            raise Exception('Error while en/dis-abling power sweep')
        return value

    LINEAR_SPACE_FORMAT_NAME = 'LIN'
    LOGARITHMIC_SPACE_FORMAT_NAME = 'LOG'
    LIST_SWEEP_TYPE = 'LIST'
    STEPS_SWEEP_TYPE = 'STEP'
    @property
    def SweepPoints(self) -> list[float, float]:
        isDwellTimeUnique = True
        if self.Query('SOUR:LIST:TYPE') == AgilentN5183B.STEPS_SWEEP_TYPE:
            frequencyStart = float(self.Query('SOUR:FREQ:STAR'))
            frequencyStop = float(self.Query('SOUR:FREQ:STOP'))
            points = int(self.Query('SOUR:SWE:POIN'))
            if self.Query('SOUR:SWE:SPAC') == AgilentN5183B.LOGARITHMIC_SPACE_FORMAT_NAME:
                frequencies = logspace(log10(frequencyStart), log10(frequencyStop), points)
            else:
                frequencies = linspace(frequencyStart, frequencyStop, points)
            frequencies = [round(frequency, 2) for frequency in frequencies]
            powerStart = float(self.Query('SOUR:POW:STAR'))
            powerStop = float(self.Query('SOUR:POW:STOP'))
            powers = linspace(powerStart, powerStop, points)
        else:
            frequencies = [float(freq) for freq in self.Query('SOUR:LIST:FREQ').split(',')]
            powers = [float(freq) for freq in self.Query('SOUR:LIST:POW').split(',')]
            isDwellTimeUnique = self.Query('SOUR:LIST:DWEL:TYPE') == AgilentN5183B.STEPS_SWEEP_TYPE
        
        if isDwellTimeUnique:
            dwellTimes = [float(self.Query('SOUR:SWE:DWEL'))] * len(frequencies)
        else:
            dwellTimes = [float(dwellTime) for dwellTime in self.Query('SOUR:LIST:DWEL').split(',')]
        
        return list(zip(frequencies, powers, dwellTimes))
    @SweepPoints.setter
    def SweepPoints(self, value: list[float, float, float]) -> list[float, float, float]:
        self.Write('SOUR:LIST:TYPE', 'LIST')
        self.Write('SOUR:LIST:TYPE:LIST:INIT:PRES')
        self.Write('SOUR:LIST:FREQ', ','.join([str(piece[0]) for piece in value]))
        self.Write('SOUR:LIST:POW', ','.join([str(piece[1]) for piece in value]))

        dwellTimes = [piece[2] for piece in value]
        uniqueDwellTimes = len(set(dwellTimes)) 
        if uniqueDwellTimes > 1:
            self.Write('SOUR:LIST:DWEL', ','.join([str(dwellTime) for dwellTime in dwellTimes]))
            self.Write('SOUR:LIST:DWEL:TYPE', AgilentN5183B.LIST_SWEEP_TYPE)
        else:
            self.Write('SOUR:SWE:DWEL', str(dwellTimes[0]))
            self.Write('SOUR:LIST:DWEL:TYPE', AgilentN5183B.STEPS_SWEEP_TYPE)
        return self.SweepPoints

    def SetSweepPointsByRanges(self, frequencyStart: float, frequencyStop: float, powerStart: float, powerStop: float, points: int, isFrequencyRangeLogarithmic: bool, dwellTime: float):
        self.Write('SOUR:LIST:TYPE', 'STEP')
        self.Write('SOUR:FREQ:STAR', str(frequencyStart))
        self.Write('SOUR:FREQ:STOP', str(frequencyStop))
        self.Write('SOUR:POW:STAR', str(powerStart))
        self.Write('SOUR:POW:STOP', str(powerStop))
        self.Write('SOUR:SWE:POIN', str(points))
        self.Write('SOUR:SWE:SPAC', AgilentN5183B.LOGARITHMIC_SPACE_FORMAT_NAME if isFrequencyRangeLogarithmic else AgilentN5183B.LINEAR_SPACE_FORMAT_NAME)
        self.Write('SOUR:SWE:DWEL', str(dwellTime))
    
    EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME = 'EXT'
    EXTERNAL_SWEEP_TRIGGER_SOURCES = [
        TriggerSource.Trigger1,
        TriggerSource.Trigger2,
        TriggerSource.Pulse
    ]
    INTERNAL_SWEEP_TRIGGER_SOURCE_NAME = 'INT'
    INTERNAL_SWEEP_TRIGGER_SOURCES = [
        TriggerSource.PulseSync,
        TriggerSource.PulseVideo
    ]
    @property
    def SweepTriggerSource(self) -> TriggerSource:
        value = self.Query('TRIG:SOUR')
        match value:
            case AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME:
                return TriggerSource(self.Query('TRIG:EXT:SOUR'))
            case AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCE_NAME:
                return TriggerSource(self.Query('TRIG:INT:SOUR'))
            case _:
                return TriggerSource(value)
    @SweepTriggerSource.setter
    def SweepTriggerSource(self, value: TriggerSource) -> TriggerSource:
        value = TriggerSource(value)
        if value in AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCES:
            self.Write('TRIG:EXT:SOUR', str(value.value))
            self.Write('TRIG:SOUR', AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME)
        elif value in AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCES:
            self.Write('TRIG:INT:SOUR', str(value.value))
            self.Write('TRIG:SOUR', AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCE_NAME)
        else:
            self.Write('TRIG:SOUR', str(value.value))
        if self.SweepTriggerSource != value:
            raise Exception("Error while setting sweep trigger source")
        return value
    @property
    def SweepPointTriggerSource(self) -> TriggerSource:
        value = self.Query('LIST:TRIG:SOUR')
        match value:
            case AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME:
                return TriggerSource(self.Query('LIST:TRIG:EXT:SOUR'))
            case AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCE_NAME:
                return TriggerSource(self.Query('LIST:TRIG:INT:SOUR'))
            case _:
                return TriggerSource(value)
    @SweepPointTriggerSource.setter
    def SweepPointTriggerSource(self, value: TriggerSource) -> TriggerSource:
        value = TriggerSource(value)
        if value in AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCES:
            self.Write('LIST:TRIG:EXT:SOUR', str(value.value))
            self.Write('LIST:TRIG:SOUR', AgilentN5183B.EXTERNAL_SWEEP_TRIGGER_SOURCE_NAME)
        elif value in AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCES:
            self.Write('LIST:TRIG:INT:SOUR', str(value.value))
            self.Write('LIST:TRIG:SOUR', AgilentN5183B.INTERNAL_SWEEP_TRIGGER_SOURCE_NAME)
        else:
            self.Write('LIST:TRIG:SOUR', str(value.value))
        if self.SweepPointTriggerSource != value:
            raise Exception("Error while setting sweep point trigger source")
        return value

    SWEEP_NORMAL_DIRECTION = 'DOWN'
    SWEEP_REVERSED = 'UP'
    @property
    def IsSweepReversed(self) -> bool:
        return self.Query('SOUR:LIST:DIR') == AgilentN5183B.SWEEP_REVERSED
    @IsSweepReversed.setter
    def IsSweepReversed(self, value: bool) -> bool:
        value = bool(value)
        self.Write('SOUR:LIST:DIR', AgilentN5183B.SWEEP_REVERSED if value else AgilentN5183B.SWEEP_NORMAL_DIRECTION)
        if self.IsSweepReversed != value:
            raise Exception("Error while setting sweep direction")
        return value

    @property
    def SweepReturnToFirstPoint(self) -> bool:
        return bool(int(self.Query('LIST:RETR')))
    @SweepReturnToFirstPoint.setter
    def SweepReturnToFirstPoint(self, value: bool) -> bool:
        value = bool(value)
        self.Write('LIST:RETR', str(int(value)))
        if value != self.SweepReturnToFirstPoint:
            raise Exception("Error while setting the return to first point")
        return value

    @property
    def IsLowFrequencyOutputEnabled(self) -> bool:
        return bool(int(self.Query('SOUR:LFO:STAT')))
    @IsLowFrequencyOutputEnabled.setter
    def IsLowFrequencyOutputEnabled(self, value: bool):
        value = int(bool(value))
        self.Write('SOUR:LFO:STAT', str(value))
        if self.IsLowFrequencyOutputEnabled != value:
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
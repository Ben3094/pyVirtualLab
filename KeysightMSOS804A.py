from enum import Enum, unique
from VISAInstrument import VISAInstrument

@unique
class RunState(Enum):
    Stop = 0
    Single = 1
    Run = 2
   
@unique
class AcquisitionState(Enum):
    Armed = 0
    Triggered = 1
    Done = 3

@unique
class ChannelUnit(Enum):
    Volt = 0
    Ampere = 1
    Watt = 2
    Unknown = 3

class Channel():
    def __init__(self, parentKeysightMSOS804A, address):
        self._parent = parentKeysightMSOS804A
        self._address = address

    @property
    def Address(self):
        return self._address

class AnalogChannel(Channel):
    @property
    def Label(self):
        return self._parent.Query(f"CHAN{self._address}:LAB?")
    @Label.setter
    def Label(self, value):
        value = str(value)
        if value.isascii() & len(value) <= 16:
            return self._parent.Write(f"CHAN{self._address}:LAB {value}")
        else:
            raise Exception("Label must be ASCII and less or equal 16 characters long")

    @property
    def IsEnabled(self):
        return bool(self._parent.Query(f"CHAN{self._address}:DISP?"))
    @IsEnabled.setter
    def IsEnabled(self, value):
        return self._parent.Query(f"CHAN{self._address}:DISP {int(bool(value))}")

    @property
    def IsInverted(self):
        return bool(self._parent.Query(f"CHAN{self._address}:INV"))
    @IsInverted.setter
    def IsInverted(self, value):
        return self._parent.Query(f"CHAN{self._address}:INV {int(bool(value))}")
    
    @property
    def Unit(self):
        match self._parent.Query(f"CHAN{self._address}:UNIT"):
            case "VOLT":
                return ChannelUnit.Volt
            case "AMP":
                return ChannelUnit.Ampere
            case "WATT":
                return ChannelUnit.Watt
            case "UNKN":
                return ChannelUnit.Unknown
    @Unit.setter
    def Unit(self, value):
        match value:
            case ChannelUnit.Volt:
                self._parent.Write(f"CHAN{self._address}:UNIT VOLT")
            case ChannelUnit.Ampere:
                self._parent.Write(f"CHAN{self._address}:UNIT AMP")
            case ChannelUnit.Watt:
                self._parent.Write(f"CHAN{self._address}:UNIT WATT")
            case ChannelUnit.Unknown:
                self._parent.Write(f"CHAN{self._address}:UNIT UNKN")
    
    # Measurements
    def GetMaximum(self):
        return float(self._parent.Query(f"MEAS:VMAX", f"CHAN{self._address}"))
    def GetMinimum(self):
        return float(self._parent.Query(f"MEAS:VMIN", f"CHAN{self._address}"))
    def GetAverage(self):
        return float(self._parent.Query(f"MEAS:VAV", f"DISP,CHAN{self._address}"))
    def GetRange(self):
        return float(self._parent.Query(f"MEAS:VPP", f"CHAN{self._address}"))
    def GetFrequency(self):
        return float(self._parent.Query(f"MEAS:FREQ", f"CHAN{self._address}"))
    def GetPeriod(self):
        return float(self._parent.Query(f"MEAS:PER", f"CHAN{self._address}"))
    def GetRiseTime(self):
        return float(self._parent.Query(f"MEAS:RIS", f"CHAN{self._address}"))
    def GetFallTime(self):
        return float(self._parent.Query(f"MEAS:FALL", f"CHAN{self._address}"))
    def GetFFTPeaksMagnitudes(self):
        return [float(peakMagnitude) for peakMagnitude in self._parent.Query(f"FUNC1:FFT:PEAK:MAGN").strip('"').split(',')]

class DigitalChannel(Channel):
    pass

class KeysightMSOS804A(VISAInstrument):
    def __init__(self, address):
        super(KeysightMSOS804A, self).__init__(address)
        self.Channels = list()
        self._indexChannels()

    def GetAnalogData(self):
        self.Write("WAV:BYT LSBF")
        self.Write("WAV:FORM WORD")
        yIncrement = float(self.Query("WAV:YINC"))
        yOrigin = float(self.Query("WAV:YOR"))
        return [yIncrement * float(result) + yOrigin for result in self._instr.query_binary_values("WAV:DATA?", datatype='h', is_big_endian=False)]
    
    @property
    def Average(self):
        if not bool(self.Query("ACQ:AVER")):
            return 1
        else:
            return int(self.Query("ACQ:AVER:COUN"))
    @Average.setter
    def Average(self, count):
        if count < 2:
            self.Write("ACQ:AVER OFF")
        else:
            self.Write("ACQ:AVER:COUN " + str(int(count)))
            self.Write("ACQ:AVER ON")

    @property
    def RunState(self):
        match str(self.Query("RST")):
            case 'RUN':
                return RunState.Run
            case 'STOP':
                return RunState.Stop
            case 'SING':
                return RunState.Single
    @RunState.setter
    def RunState(self, runState):
        match runState:
            case RunState.Run:
                self.Write("RUN")
            case RunState.Stop:
                self.Write("STOP")
            case RunState.Single:
                self.Write("SING")

    @property
    def AcquisitionState(self):
        match str(self.Query("AST")):
            case 'ARM':
                return AcquisitionState.Armed
            case 'TRIG' | 'ATRIG':
                return AcquisitionState.Triggered
            case 'ADONE':
                return AcquisitionState.Done

    def AutoScale(self):
        self.Write("AUT")

    def _indexChannels(self):
        # Add analog channels
        for address in range(1, 4+1):
            self.Channels.append(AnalogChannel(self, address))

        # Add digital channels
        for address in range(0, 16):
            self.Channels.append(DigitalChannel(self, address))
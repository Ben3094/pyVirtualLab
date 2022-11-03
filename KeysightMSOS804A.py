from enum import Enum, unique
from VISAInstrument import VISAInstrument
import re

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
    TYPE_COMMAND_HEADER = 'CHAN'

    def __init__(self, parentKeysightMSOS804A, address):
        self._parent = parentKeysightMSOS804A
        self._address = address
        self._commandAddress = f"{self.TYPE_COMMAND_HEADER}{self._address}"

    @property
    def Address(self) -> float:
        return self._address

class AnalogChannel(Channel):
    @property
    def Label(self):
        return self._parent.Query(f"{self._commandAddress}:LAB?")
    @Label.setter
    def Label(self, value):
        value = str(value)
        if value.isascii() & len(value) <= 16:
            return self._parent.Write(f"{self._commandAddress}:LAB {value}")
        else:
            raise Exception("Label must be ASCII and less or equal 16 characters long")

    @property
    def IsEnabled(self):
        return bool(self._parent.Query(f"{self._commandAddress}:DISP?"))
    @IsEnabled.setter
    def IsEnabled(self, value):
        return self._parent.Query(f"{self._commandAddress}:DISP {int(bool(value))}")

    @property
    def IsInverted(self):
        return bool(self._parent.Query(f"{self._commandAddress}:INV"))
    @IsInverted.setter
    def IsInverted(self, value):
        return self._parent.Query(f"{self._commandAddress}:INV {int(bool(value))}")
    
    @property
    def Unit(self):
        match self._parent.Query(f"{self._commandAddress}:UNIT"):
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
                self._parent.Write(f"{self._commandAddress}:UNIT VOLT")
            case ChannelUnit.Ampere:
                self._parent.Write(f"{self._commandAddress}:UNIT AMP")
            case ChannelUnit.Watt:
                self._parent.Write(f"{self._commandAddress}:UNIT WATT")
            case ChannelUnit.Unknown:
                self._parent.Write(f"{self._commandAddress}:UNIT UNKN")
    
    # Measurements
    def GetMaximum(self):
        return float(self._parent.Query(f"MEAS:VMAX", f"{self._commandAddress}"))
    def GetMinimum(self):
        return float(self._parent.Query(f"MEAS:VMIN", f"{self._commandAddress}"))
    def GetAverage(self):
        return float(self._parent.Query(f"MEAS:VAV", f"DISP,{self._commandAddress}"))
    def GetRange(self):
        return float(self._parent.Query(f"MEAS:VPP", f"{self._commandAddress}"))
    def GetFrequency(self):
        return float(self._parent.Query(f"MEAS:FREQ", f"{self._commandAddress}"))
    def GetPeriod(self):
        return float(self._parent.Query(f"MEAS:PER", f"{self._commandAddress}"))
    def GetRiseTime(self):
        return float(self._parent.Query(f"MEAS:RIS", f"{self._commandAddress}"))
    def GetFallTime(self):
        return float(self._parent.Query(f"MEAS:FALL", f"{self._commandAddress}"))

class DigitalChannel(Channel):
    TYPE_COMMAND_HEADER = 'DIG'

class Function(Channel):
    TYPE_COMMAND_HEADER = 'FUNC'
    NAME = None

    def __init__(self, parentKeysightMSOS804A, address, involvedChannels):
        super().__init__(parentKeysightMSOS804A, address)
        self._involvedChannels = involvedChannels

    def ChangeFunction(self, targetedFunction, targetedInvolvedChannels):
        self._parent.Write(f"{self._commandAddress}:{targetedFunction.NAME} {','.join([targetedInvolvedChannel._commandAddress for targetedInvolvedChannel in targetedInvolvedChannels])}")

class AddFunction(Function):
	NAME = 'ADD'
class AverageFunction(Function):
	NAME = 'AVER'
class CommonModeFunction(Function):
	NAME = 'COMM'
class DifferentiateFunction(Function):
	NAME = 'DIFF'
class DivideFunction(Function):
	NAME = 'DIV'
class FFTMagnitudeFunction(Function):
    NAME = 'FFTM'

    @property
    def PeaksAnnotations(self) -> bool:
        return bool(self._parent.Query(f"{self._commandAddress}:FFT:PEAK:STAT"))
    @PeaksAnnotations.setter
    def PeaksAnnotations(self, value):
        self._parent.Write(f"{self._commandAddress}:FFT:PEAK:STAT", str(int(bool(value))))

    def GetFFTPeaks(self) -> dict:
        savedPeaksAnnotations = self.PeaksAnnotations
        self.PeaksAnnotations = True
            
        magnitudes = [float(peakMagnitude) for peakMagnitude in self._parent.Query(f"{self._commandAddress}:FFT:PEAK:MAGN").strip('"').split(',')]
        frequencies = [float(peakFrequency) for peakFrequency in self._parent.Query(f"{self._commandAddress}:FFT:PEAK:FREQ").strip('"').split(',')]
        
        self.PeaksAnnotations = savedPeaksAnnotations

        return dict(zip(frequencies, magnitudes))
        
class FFTPhaseFunction(Function):
    NAME = 'FFTP'
class HighPassFunction(Function):
	NAME = 'HIGH'
class IntegrateFunction(Function):
	NAME = 'INT'
class InvertFunction(Function):
	NAME = 'INV'
class LowPassFunction(Function):
	NAME = 'LOW'
class MagnifyFunction(Function):
	NAME = 'MAGN'
class MaximumFunction(Function):
	NAME = 'MAX'
class MinimumFunction(Function):
	NAME = 'MIN'
class MultiplyFunction(Function):
	NAME = 'MULT'
class SmoothFunction(Function):
	NAME = 'SMO'
class SubtractFunction(Function):
	NAME = 'SUB'
class VersusFunction(Function):
	NAME = 'VERS'

FUNCTIONS_NAMES = dict([(subclass.NAME, subclass) for subclass in Function.__subclasses__()])

class KeysightMSOS804A(VISAInstrument):
    def __init__(self, address):
        super(KeysightMSOS804A, self).__init__(address)

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

    @property
    def ReturnHeader(self) -> bool:
        return bool(int(self.Query('SYST:HEAD')))
    @ReturnHeader.setter
    def ReturnHeader(self, value):
        self.Write('SYST:HEAD', str(int(bool(value))))

    ANALOG_CHANNELS = 4
    DIGITAL_CHANNELS = 16
    @property
    def Channels(self):
        result = list()

        # Add analog channels
        for address in range(1, self.ANALOG_CHANNELS+1):
            result.append(AnalogChannel(self, address))

        # Add digital channels
        for address in range(0, self.DIGITAL_CHANNELS):
            result.append(DigitalChannel(self, address))

        return result

    FUNCTIONS = 16
    @property
    def Functions(self):
        result = list()
        savedReturnHeader = self.ReturnHeader
        self.ReturnHeader = True

        for address in range(1, self.FUNCTIONS+1):
            query = f"{Function.TYPE_COMMAND_HEADER}{address}"
            response = self.Query(query).lstrip(':').split()
            result.append(FUNCTIONS_NAMES[response[0]](self, address, list([self.StringToChannel(channelString) for channelString in response[1].split(',')])))

        self.ReturnHeader = savedReturnHeader
        return result

    def StringToChannel(self, value) -> Channel:
        match = re.match('([A-Z]+)(\d+)', value)
        match match.groups(0)[0]:
            case AnalogChannel.TYPE_COMMAND_HEADER:
                return next((channel for channel in self.Channels if channel.Address == int(match.groups(0)[1]) and isinstance(channel, AnalogChannel)), None)

            case DigitalChannel.TYPE_COMMAND_HEADER:
                return next((channel for channel in self.Channels if channel.Address == int(match.groups(0)[1]) and isinstance(channel, DigitalChannel)), None)

            case Function.TYPE_COMMAND_HEADER:
                return next((channel for channel in self.Channels if channel.Address == int(match.groups(0)[1])), None)

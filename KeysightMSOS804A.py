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
        self.__parent__ = parentKeysightMSOS804A
        self.__address__ = address
        self.__commandAddress__ = f"{self.TYPE_COMMAND_HEADER}{self.__address__}"

    @property
    def Address(self) -> float:
        return self.__address__

class AnalogChannel(Channel):
    @property
    def Label(self):
        return self.__parent__.Query(f"{self.__commandAddress__}:LAB?")
    @Label.setter
    def Label(self, value):
        value = str(value)
        if value.isascii() & len(value) <= 16:
            return self.__parent__.Write(f"{self.__commandAddress__}:LAB {value}")
        else:
            raise Exception("Label must be ASCII and less or equal 16 characters long")

    @property
    def IsEnabled(self) -> bool:
        return bool(self.__parent__.Query(f"{self.__commandAddress__}:DISP?"))
    @IsEnabled.setter
    def IsEnabled(self, value):
        return self.__parent__.Write(f"{self.__commandAddress__}:DISP {int(bool(value))}")

    @property
    def IsInverted(self) -> bool:
        return bool(self.__parent__.Query(f"{self.__commandAddress__}:INV"))
    @IsInverted.setter
    def IsInverted(self, value):
        return self.__parent__.Write(f"{self.__commandAddress__}:INV {int(bool(value))}")
    
    @property
    def Unit(self) -> ChannelUnit:
        match self.__parent__.Query(f"{self.__commandAddress__}:UNIT"):
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
                self.__parent__.Write(f"{self.__commandAddress__}:UNIT VOLT")
            case ChannelUnit.Ampere:
                self.__parent__.Write(f"{self.__commandAddress__}:UNIT AMP")
            case ChannelUnit.Watt:
                self.__parent__.Write(f"{self.__commandAddress__}:UNIT WATT")
            case ChannelUnit.Unknown:
                self.__parent__.Write(f"{self.__commandAddress__}:UNIT UNKN")
    
    # Measurements
    def GetMaximum(self) -> float:
        return float(self.__parent__.Query(f"MEAS:VMAX", f"{self.__commandAddress__}"))
    def GetMinimum(self) -> float:
        return float(self.__parent__.Query(f"MEAS:VMIN", f"{self.__commandAddress__}"))
    def GetAverage(self) -> float:
        return float(self.__parent__.Query(f"MEAS:VAV", f"DISP,{self.__commandAddress__}"))
    def GetRange(self) -> float:
        return float(self.__parent__.Query(f"MEAS:VPP", f"{self.__commandAddress__}"))
    def GetFrequency(self) -> float:
        return float(self.__parent__.Query(f"MEAS:FREQ", f"{self.__commandAddress__}"))
    def GetPeriod(self) -> float:
        return float(self.__parent__.Query(f"MEAS:PER", f"{self.__commandAddress__}"))
    def GetRiseTime(self) -> float:
        return float(self.__parent__.Query(f"MEAS:RIS", f"{self.__commandAddress__}"))
    def GetFallTime(self) -> float:
        return float(self.__parent__.Query(f"MEAS:FALL", f"{self.__commandAddress__}"))

class DigitalChannel(Channel):
    TYPE_COMMAND_HEADER = 'DIG'

class Function(Channel):
    TYPE_COMMAND_HEADER = 'FUNC'
    NAME = None

    def __init__(self, parentKeysightMSOS804A, address, involvedChannels):
        super().__init__(parentKeysightMSOS804A, address)
        self._involvedChannels = involvedChannels

    @property
    def IsEnabled(self) -> bool:
        return bool(self.__parent__.Query(f"{self.__commandAddress__}:DISP?"))
    @IsEnabled.setter
    def IsEnabled(self, value):
        return self.__parent__.Write(f"{self.__commandAddress__}:DISP {int(bool(value))}")

    def ChangeFunction(self, targetedFunction, targetedInvolvedChannels: list):
        self.__parent__.Write(f"{self.__commandAddress__}:{targetedFunction.NAME} {','.join([targetedInvolvedChannel._commandAddress for targetedInvolvedChannel in targetedInvolvedChannels])}")

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
        return bool(self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:STAT"))
    @PeaksAnnotations.setter
    def PeaksAnnotations(self, value):
        self.__parent__.Write(f"{self.__commandAddress__}:FFT:PEAK:STAT", str(int(bool(value))))

    def GetFFTPeaks(self) -> dict:
        savedPeaksAnnotations = self.PeaksAnnotations
        self.PeaksAnnotations = True
            
        magnitudes = [float(peakMagnitude) for peakMagnitude in self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:MAGN").strip('"').split(',')]
        frequencies = [float(peakFrequency) for peakFrequency in self.__parent__.Query(f"{self.__commandAddress__}:FFT:PEAK:FREQ").strip('"').split(',')]
        
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
    def __init__(self, address:int):
        super(KeysightMSOS804A, self).__init__(address)

    def GetAnalogData(self):
        self.Write("WAV:BYT LSBF")
        self.Write("WAV:FORM WORD")
        yIncrement = float(self.Query("WAV:YINC"))
        yOrigin = float(self.Query("WAV:YOR"))
        return [yIncrement * float(result) + yOrigin for result in self._instr.query_binary_values("WAV:DATA?", datatype='h', is_big_endian=False)]
    
    @property
    def Average(self) -> int:
        if not bool(self.Query("ACQ:AVER")):
            return 1
        else:
            return int(self.Query("ACQ:AVER:COUN"))
    @Average.setter
    def Average(self, count:int):
        if count < 2:
            self.Write("ACQ:AVER OFF")
        else:
            self.Write("ACQ:AVER:COUN " + str(int(count)))
            self.Write("ACQ:AVER ON")

    @property
    def RunState(self) -> RunState:
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
    def AcquisitionState(self) -> AcquisitionState:
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
    @property
    def AnalogChannels(self) -> dict:
        result = dict()
        for address in range(1, self.ANALOG_CHANNELS+1):
            result[address] = AnalogChannel(self, address)
        return result

    DIGITAL_CHANNELS = 16
    @property
    def DigitalChannels(self) -> dict:
        result = dict()
        for address in range(0, self.DIGITAL_CHANNELS):
            result[address] = DigitalChannel(self, address)
        return result

    FUNCTIONS = 16
    @property
    def Functions(self) -> dict:
        result = dict()
        savedReturnHeader = self.ReturnHeader
        self.ReturnHeader = True

        for address in range(1, self.FUNCTIONS+1):
            query = f"{Function.TYPE_COMMAND_HEADER}{address}"
            response = self.Query(query).lstrip(':').split()
            result[address] = FUNCTIONS_NAMES[response[0]](self, address, list([self.StringToChannel(channelString) for channelString in response[1].split(',')]))

        self.ReturnHeader = savedReturnHeader
        return result

    def StringToChannel(self, value) -> Channel:
        match = re.match('([A-Z]+)(\d+)', value)
        match match.groups(0)[0]:
            case AnalogChannel.TYPE_COMMAND_HEADER:
                return self.AnalogChannels[int(match.groups(0)[1])]

            case DigitalChannel.TYPE_COMMAND_HEADER:
                return self.DigitalChannels[int(match.groups(0)[1])]

            case Function.TYPE_COMMAND_HEADER:
                return next((channel for channel in self.Channels if channel.Address == int(match.groups(0)[1])), None)

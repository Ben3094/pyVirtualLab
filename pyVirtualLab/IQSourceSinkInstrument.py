from pyVirtualLab.VISAInstrument import Instrument

class IQSinkInstrument(Instrument):
    def InitIQSink(self, sampleRate:float):
        pass

    def SendIQSample(self, sample:complex):
        pass

class IQSourceInstrument(Instrument):
    def InitIQSource(self, sampleRate:float):
        pass

    def GetIQSample(self) -> complex:
        pass
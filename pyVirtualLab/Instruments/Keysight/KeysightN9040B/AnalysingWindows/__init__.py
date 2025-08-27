from ..AnalysingWindow import AnalysingWindow
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES

class NR5GAnalyse(AnalysingWindow):
	MODE_NAME:str = "NR5G"

class VSA89601Analyse(AnalysingWindow):
	MODE_NAME:str = "VSA89601"

class AnalogDemodulationAnalyse(AnalysingWindow):
	MODE_NAME:str = "ADEMOD"

class AvionicsAnalyse(AnalysingWindow):
	MODE_NAME:str = "AVIONIC"

class BluetoothAnalyse(AnalysingWindow):
	MODE_NAME:str = "BT"

class ChannelQuality_GroupDelayAnalyse(AnalysingWindow):
	MODE_NAME:str = "CQM"

class EMIReceiverAnalyse(AnalysingWindow):
	MODE_NAME:str = "EMI"

class GSM_EDGE_EDGEEvoAnalyse(AnalysingWindow):
	MODE_NAME:str = "EDGEGSM"

class BasicIQAnalyse(AnalysingWindow):
	MODE_NAME:str = "BASIC"

class LTEFDD_LTEAFDDAnalyse(AnalysingWindow):
	MODE_NAME:str = "LTEAFDD"

class LTETDD_LTEATDDAnalyse(AnalysingWindow):
	MODE_NAME:str = "LTEATDD"

class MeasuringReceiverAnalyse(AnalysingWindow):
	MODE_NAME:str = "MRECEIVE"

class MSRAnalyse(AnalysingWindow):
	MODE_NAME:str = "MSR"

class NoiseFigureAnalyse(AnalysingWindow):
	MODE_NAME:str = "NFIG"

class PhaseNoiseAnalyse(AnalysingWindow):
	MODE_NAME:str = "PNOISE"

class PowerAmplifierAnalyse(AnalysingWindow):
	MODE_NAME:str = "PA"

class PulseAnalyse(AnalysingWindow):
	MODE_NAME:str = "PULSEX"

class RadioTestAnalyse(AnalysingWindow):
	MODE_NAME:str = "RTS"

class RealTimeSpectrumAnalyzerAnalyse(AnalysingWindow):
	MODE_NAME:str = "RTSA"

class RemoteLanguageCompatibilityAnalyse(AnalysingWindow):
	MODE_NAME:str = "RLC"

class SCPILanguageCompatibilityAnalyse(AnalysingWindow):
	MODE_NAME:str = "SCPILC"

class SequenceAnalyse(AnalysingWindow):
	MODE_NAME:str = "SEQAN"

class ShortRangeCommunicationsAnalyse(AnalysingWindow):
	MODE_NAME:str = "SRCOMMS"

class VectorModulationAnalyse(AnalysingWindow):
	MODE_NAME:str = "VMA"

class WCDMAWithHSPAPlusAnalyse(AnalysingWindow):
	MODE_NAME:str = "WCDMA"

class WLANAnalyse(AnalysingWindow):
	MODE_NAME:str = "WLAN"

from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
package_dir = Path(__file__).resolve().parent
for (_, module_name, _) in iter_modules([package_dir]):
	module = import_module(f"{__name__}.{module_name}")
	for attribute_name in dir(module):
		attribute = getattr(module, attribute_name)
		if isclass(attribute) and attribute != AnalysingWindow and issubclass(attribute, AnalysingWindow):
			globals()[attribute_name] = attribute

ANALYSING_WINDOWS_NAMES = dict([(subclass.MODE_NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(AnalysingWindow)])
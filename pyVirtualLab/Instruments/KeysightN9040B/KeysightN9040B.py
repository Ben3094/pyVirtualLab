from pyVirtualLab.VISAInstrument import Instrument
from pyVirtualLab.Helpers import GetProperty, SetProperty
from .AnalysingWindows import AnalysingWindow, ANALYSING_WINDOWS_NAMES
from .AnalysingWindows.SpectrumAnalyse import SpectrumAnalyse
from re import match
from enum import Enum, unique

@unique
class CalibrationAlignementMode(Enum):
	Automatic = 'ON'
	Light = 'LIGH'
	Partial = 'PART'
	Disabled = "OFF"

@unique
class InputPort(Enum):
	RFPort = 'RF'
	ExternalMixerPort = 'EMIX'
	IQPort = "AIQ"

@unique
class MixerPath(Enum):
	Normal = 'NORM'
	DualConversion = 'DUAL'
	AuxiliaryEquipment = 'AUX'

@unique
class MixerSignalIdentificationMode(Enum):
	Disabled = 'OFF'
	Suppress = 'ISUP'
	Shift = 'ISH'

class KeysightN9040B(Instrument):
	def __init__(self, address):
		super(KeysightN9040B, self).__init__(address)

	RESET_COMMAND:str = 'SYST:DEF'
	def Reset(self):
		self.Write(KeysightN9040B.RESET_COMMAND)

	#TODO: Get available modes and revision and option for each (using SYST:APPL:CAT:REV)
	__availableModes__:list[type] = None
	@property
	def AvailableModes(self) -> list[type]:
		if self.__availableModes__ == None:
			self.__availableModes__ = self.__getAvailableModes__()
		return self.__availableModes__
	AVAILABLE_MODES_COMMAND:str = 'INST:CAT'
	def __getAvailableModes__(self) -> list[type]:
		availableModes:list[type] = [SpectrumAnalyse]
		answers = self.Query(KeysightN9040B.AVAILABLE_MODES_COMMAND).split(',')
		answers = [match("\\s?((?:(?:[A-Z])|\\d)+) \\d+", answer)[1] for answer in answers]
		answers.remove(SpectrumAnalyse.MODE_NAME)
		for answer in answers:
			availableModes.append(ANALYSING_WINDOWS_NAMES[answer])
		return availableModes
	
	SEQUENCER_COMMAND = 'SYST:SEQ'
	@property
	@GetProperty(bool, SEQUENCER_COMMAND)
	def IsSequencerEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsSequencerEnabled.setter
	@SetProperty(bool, SEQUENCER_COMMAND)
	def IsSequencerEnabled(self, value:bool) -> bool:
		pass

	__analysingWindows__:list[AnalysingWindow] = list()
	LIST_ANALYSING_WINDOWS_NAMES_COMMAND:str = 'INST:SCR:CAT'
	@property
	def AnalysingWindowsNames(self) -> list[str]:
		return self.Query(KeysightN9040B.LIST_ANALYSING_WINDOWS_NAMES_COMMAND).split(',')
	@property
	def AnalysingWindows(self) -> list[AnalysingWindow]:
		savedFocusedAnalysingWindowName:str = self.FocusedAnalysingWindowName
		names = self.AnalysingWindowsNames
		analysingWindowsBuffer = self.__analysingWindows__.copy()
		for name in names:
			analysingWindow = [analysingWindow for analysingWindow in analysingWindowsBuffer if analysingWindow.Name == name]
			self.FocusedAnalysingWindowName = name
			mode = self.Query(AnalysingWindow.MODE_COMMAND)
			if len(analysingWindow) > 0: # Just update
				analysingWindow = analysingWindow[0]
				analysingWindowsBuffer.remove(analysingWindow)
				if analysingWindow.MODE_NAME != mode:
					analysingWindow.Delete()
					ANALYSING_WINDOWS_NAMES[mode](self, isAddedLocaly=False)
			else: # Add
				ANALYSING_WINDOWS_NAMES[mode](self, isAddedLocaly=False)
		[remainingAnalysingWindow.Delete() for remainingAnalysingWindow in analysingWindowsBuffer] # Delete
		self.FocusedAnalysingWindowName = savedFocusedAnalysingWindowName
		return self.__analysingWindows__
	
	FOCUSED_ANALYSING_WINDOW_COMMAND:str = 'INST:SCR:SEL'
	@property
	@GetProperty(str, FOCUSED_ANALYSING_WINDOW_COMMAND)
	def FocusedAnalysingWindowName(self, getMethodReturn):
		return getMethodReturn
	@FocusedAnalysingWindowName.setter
	@SetProperty(str, FOCUSED_ANALYSING_WINDOW_COMMAND)
	def FocusedAnalysingWindowName(self, value:str) -> str:
		pass

	MULTISCREEN_COMMAND:str = 'INST:SCR:MULT'
	@property
	@GetProperty(bool, MULTISCREEN_COMMAND)
	def IsMultiscreenEnabled(self, getMethodReturn):
		return getMethodReturn
	@IsMultiscreenEnabled.setter
	@SetProperty(bool, MULTISCREEN_COMMAND)
	def IsMultiscreenEnabled(self, value:bool) -> bool:
		pass

	MODE_REVISION_COMMAND:str = 'SYST:APPL:REV'
	@property
	@GetProperty(str, MODE_REVISION_COMMAND)
	def Revision(self, getMethodReturn) -> str:
		return getMethodReturn
	
	MODE_OPTIONS_COMMAND:str = 'SYST:APPL:OPT'
	@property
	@GetProperty(str, MODE_OPTIONS_COMMAND)
	def Options(self, getMethodReturn) -> list[str]:
		return str(getMethodReturn).split(',')
	
	CALIBRATION_ALIGNEMENT_MODE_COMMAND:str = 'CAL:AUTO'
	@property
	@GetProperty(CalibrationAlignementMode, CALIBRATION_ALIGNEMENT_MODE_COMMAND)
	def CalibrationAlignementModeSet(self, getMethodReturn):
		return getMethodReturn
	@CalibrationAlignementModeSet.setter
	@SetProperty(bool, CALIBRATION_ALIGNEMENT_MODE_COMMAND)
	def CalibrationAlignementModeSet(self, value:CalibrationAlignementMode) -> CalibrationAlignementMode:
		pass
	
	INPUT_COMMAND:str = 'SENS:FEED'
	@property
	@GetProperty(InputPort, INPUT_COMMAND)
	def Input(self, getMethodReturn):
		return getMethodReturn
	@Input.setter
	def Input(self, value:InputPort) -> InputPort:
		value = InputPort(value)
		match value:
			case InputPort.ExternalMixerPort:
				if not 'EXM' in self.Options:
					raise Exception("External mixer option is not present")
			case InputPort.IQPort:
				if not 'BBA' in self.Options:
					raise Exception("IQ input option is not present")
		self.Write(KeysightN9040B.INPUT_COMMAND, value.value)
		if self.Input != value:
			raise Exception("Exception while setting the input port")
		return value
	
	RF_COUPLING_COMMAND:str = "INP:COUP"
	AC_RF_COUPLING_ARGUMENT:str = 'AC'
	DC_RF_COUPLING_ARGUMENT:str = 'DC'
	@property
	def IsDCCoupled(self) -> bool:
		return self.Query(KeysightN9040B.RF_COUPLING_COMMAND) == KeysightN9040B.DC_RF_COUPLING_ARGUMENT
	@IsDCCoupled.setter
	def IsDCCoupled(self, value:bool) -> bool:
		value = bool(value)
		self.Write(KeysightN9040B.RF_COUPLING_COMMAND, KeysightN9040B.DC_RF_COUPLING_ARGUMENT if value else KeysightN9040B.AC_RF_COUPLING_ARGUMENT)
		if self.IsDCCoupled != value:
			raise Exception("Error while setting RF coupling")
		return value
	
	IMPEDANCE_CORRECTION_COMMAND:str = 'SENS:CORR:IMP:INP:MAGN'
	_50_OHMS_IMPEDANCE_CORRECTION_ARGUMENT:str = '50'
	_75_OHMS_IMPEDANCE_CORRECTION_ARGUMENT:str = '75'
	@property
	def IsInput75OhmsCorrected(self) -> bool:
		return self.Query(KeysightN9040B.RF_COUPLING_COMMAND) == KeysightN9040B._75_OHMS_IMPEDANCE_CORRECTION_ARGUMENT
	@IsInput75OhmsCorrected.setter
	def IsInput75OhmsCorrected(self, value:bool) -> bool:
		value = bool(value)
		self.Write(KeysightN9040B.RF_COUPLING_COMMAND, KeysightN9040B._75_OHMS_IMPEDANCE_CORRECTION_ARGUMENT if value else KeysightN9040B._50_OHMS_IMPEDANCE_CORRECTION_ARGUMENT)
		if self.IsInput75OhmsCorrected != value:
			raise Exception("Error while setting RF coupling")
		return value
	
	REFRESH_USB_MIXER_CONNECTION_COMMAND:str = 'MIX:BAND USB'
	def RefreshUSBMixerConnection(self):
		self.Write(KeysightN9040B.REFRESH_USB_MIXER_CONNECTION_COMMAND)
		self.Wait(timeout=10)

	MIXER_PATH_COMMAND:str = 'SENS:MIX:MPAT'
	@property
	@GetProperty(MixerPath, MIXER_PATH_COMMAND)
	def MixerPathSet(self, getMethodReturn):
		return getMethodReturn
	@MixerPathSet.setter
	@SetProperty(MixerPath, MIXER_PATH_COMMAND)
	def MixerPathSet(self, value:MixerPath) -> MixerPath:
		pass

	MIXER_AUX_PATH_IF_FREQUENCY_COMMAND:str = 'SENS:MIX:UIFF'
	@property
	@GetProperty(float, MIXER_AUX_PATH_IF_FREQUENCY_COMMAND)
	def MixerAuxPathIFFrequency(self, getMethodReturn):
		return getMethodReturn
	@MixerAuxPathIFFrequency.setter
	@SetProperty(float, MIXER_AUX_PATH_IF_FREQUENCY_COMMAND)
	def MixerAuxPathIFFrequency(self, value:float) -> float:
		pass

	MIXER_SIGNAL_IDENTIFICATION_COMMAND:str = 'SENS:SID:STAT'
	MIXER_SIGNAL_IDENTIFICATION_MODE_COMMAND:str = 'SENS:SID:MODE'
	@property
	def MixerSignalIdentificationHandling(self) -> MixerSignalIdentificationMode:
		if self.Query(KeysightN9040B.MIXER_SIGNAL_IDENTIFICATION_COMMAND) == MixerSignalIdentificationMode.Disabled.value:
			return MixerSignalIdentificationMode.Disabled
		elif self.Query(KeysightN9040B.MIXER_SIGNAL_IDENTIFICATION_MODE_COMMAND) == MixerSignalIdentificationMode.Suppress:
			return MixerSignalIdentificationMode.Suppress
		else:
			return MixerSignalIdentificationMode.Shift
	@MixerSignalIdentificationHandling.setter
	def MixerSignalIdentificationHandling(self, value:MixerSignalIdentificationMode) -> MixerSignalIdentificationMode:
		value = MixerSignalIdentificationMode(value)
		enable = value != MixerSignalIdentificationMode.Disabled
		self.Write(KeysightN9040B.MIXER_SIGNAL_IDENTIFICATION_COMMAND, int(enable))
		if enable:
			self.Write(KeysightN9040B.MIXER_SIGNAL_IDENTIFICATION_MODE_COMMAND, value.value)
		if self.MixerSignalIdentificationHandling != value:
			raise Exception("Error while setting the mixer signal identification handling")
		return value
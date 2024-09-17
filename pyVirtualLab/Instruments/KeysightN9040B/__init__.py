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

@unique
class DataFormat(Enum):
	ASCII = 'ASC,8'
	Integer = 'INT,32'
	Real32 = 'REAL,32'
	Real64 = 'REAL,64'

import pyvisa
import aenum
import enum
import re

def GetProperty(dataType: type, visaGetCommand: str):
	__converter__ = None

	if dataType is float:
		__converter__ = lambda x: float(x)
	elif dataType is int:
		__converter__ = lambda x: int(x)
	elif dataType is bool:
		__converter__ = lambda x: bool(int(x))
	elif dataType is str:
		__converter__ = lambda x: x
	elif issubclass(dataType, aenum.Enum):
		__converter__ = lambda x: dataType(x)
	elif issubclass(dataType, enum.Enum):
		__converter__ = lambda x: dataType(x)
	else:
		raise Exception("No available converter")

	def decorator(func):
		def wrapper(*args, **kwargs):
			kwargs['getMethodReturn'] = __converter__(args[0].Query(visaGetCommand))
			return func(*args, **kwargs)
		return wrapper
	return decorator

def SetProperty(dataType: type, visaSetCommand: str):
	__converter__ = None

	if dataType is float:
		__converter__ = lambda x: str(float(x))
	elif dataType is int:
		__converter__ = lambda x: str(int(x))
	elif dataType is bool:
		__converter__ = lambda x: str(int(bool(x)))
	elif dataType is str:
		__converter__ = lambda x: str(x)
	elif issubclass(dataType, aenum.Enum):
		__converter__ = lambda x: str(dataType(x).value)
	elif issubclass(dataType, enum.Enum):
		__converter__ = lambda x: str(dataType(x).value)
	else:
		raise Exception("No available converter")

	def decorator(func):
		def wrapper(*args, **kwargs):
			args[0].Write(visaSetCommand, __converter__(args[1]))
			if getattr(args[0], func.__name__) != args[1]:
				raise Exception(f"Error while setting \"{func.__name__}\"")
			return func(*args, **kwargs)
		return wrapper
	return decorator

# See IVI foundation VXI plug&play System Alliance VPP-9: Instrument Vendor Abbreviations
class VendorAbbreviation(aenum.Enum):
	AQ = "Acqiris"
	AC = "Applicos BV"
	AV = "Advantest Corporation"
	AF = "Aeroflex Laboratories"
	AG = "Agilent Technologies"
	AI = "AIM GmbH"
	AX = "AMETRIX Instruments"
	AM = "AMP Incorporated"
	AN = "Analogic, Corp."
	AD = "Ando Electric Company Limited"
	AU = "Anritsu Company"
	AT = "Astronics Test Systems Inc."
	AO = "AOIP Instrumentation"
	AS = "ASCOR Incorporated"
	AP = "Audio Precision, Inc"
	BB = "B&B Technologies"
	BA = "BAE Systems"
	BK = "Bruel & Kjaer"
	BU = "Bustec Production Ltd."
	CA = "CAL-AV Labs, Inc."
	CI = "Cambridge Instruments"
	CH = "C&H Technologies, Inc."
	CE = "Chyng Hong Electronic Co., Ltd"
	CM = "CMC Labs"
	CC = "Compressor Controls Corporation"
	CY = "CYTEC Corporation"
	DP = "Directed Perceptions Inc."
	DS = "DSP Technology Inc."
	EA = "EA Elektro-Automatik GmbH"
	EI = "EIP Microwave, Inc."
	EX = "EXFO Inc."
	FL = "Fluke Company Inc."
	FO = "fos4X GmbH"
	GR = "GenRad"
	GT = "Giga-tronics, Inc."
	GN = "gnubi communications, Inc."
	HP = "Hewlett-Packard Company"
	HH = "Hoecherl & Hackl GmbH"
	UN = "Holding “Informtest”"
	IS = "Intepro Systems"
	DV = "IBEKO POWER AB"
	IF = "IFR"
	IT = "Instrumental Systems Corporation"
	IE = "Instrumentation Engineering, Inc."
	IC = "Integrated Control Systems"
	KE = "Keithley Instruments"
	KP = "Kepco, Inc."
	KT = "Keysight Technologies"
	KI = "Kikusui Inc."
	LC = "LeCroy"
	LP = "LitePoint Corporation"
	MP = "MAC Panel Company"
	MT = "ManTech Test Systems"
	MI = "Marconi Instruments"
	MS = "Microscan"
	ML = "MIT Lincoln Laboratory"
	NI = "National Instruments Corp."
	NT = "NEUTRIK AG"
	ND = "Newland Design + Associates, Inc."
	NH = "NH Research"
	NA = "North Atlantic Instruments"
	PW = "Pacific MindWorks, Inc."
	PE = "PesMatrix Inc."
	PM = "Phase Metrics"
	PI = "Pickering Interfaces"
	PC = "Picotest"
	PT = "Power-Tek Inc."
	RI = "Racal Instruments, Inc."
	RQ = "Raditeq"
	RA = "Radisys Corp."
	RS = "Rohde & Schwarz GmbH"
	SL = "Schlumberger Technologies"
	SC = "Scicom"
	SR = "Scientific Research Corporation"
	# AU = "Serendipity Systems, Inc."
	SI = "SignalCraft Technologies Inc."
	ST = "Sony/Tektronix Corporation"
	SS = "Spectrum Signal Processing, Inc."
	SP = "Spitzenberger & Spies GmbH"
	TA = "Talon Instruments"
	TK = "Tektronix, Inc."
	TE = "Teradyne"
	TS = "Test & Measurement Systems Inc."
	RF = "ThinkRF Corporation"
	# AT = "Thurlby Thandar Instruments Limited Transmagnetics, Inc."
	TM = "Transmagnetics, Inc."
	TP = "TSE Plazotta"
	TT = "TTI Testron, Inc."
	US = "Universal Switching Corporation"
	VE = "Vencon Technologies Inc."
	XR = "Versatile Power"
	VP = "Virginia Panel, Corp."
	VT = "VXI Technology, Inc."
	VA = "VXIbus Associates, Inc."
	WT = "Wavetek Corp."
	WG = "Wandel & Goltermann"
	WZ = "Welzek"
	YK = "Yokogawa Electric Corporation"
	ZT = "ZTEC"

# See IVI fundation SCPI Volume 1: Syntax and Style
class Instrument:
	DEFAULT_VISA_TIMEOUT = 2000

	Id:str = None
	Vendor:str = None
	Model:str = None
	Firmware:str = None

	def __init__(self, address: str, visaTimeout:int=DEFAULT_VISA_TIMEOUT):
		self.__rm__ = pyvisa.ResourceManager('@py')
		self.__address__ = address
		self.__isConnected__ = False
		self.__visaTimeout__ = visaTimeout

	@property
	def Address(self) -> str:
		return self.__address__
	@Address.setter
	def Address(self, value: str) -> str:
		if value != self.Address:
			self.__address__ = str(value)
			if self.IsConnected:
				self.Disconnect()
				self.Connect()
		return self.__address__

	@property
	def VISATimeout(self) -> int:
		return self.__visaTimeout__
	@VISATimeout.setter
	def VISATimeout(self, value: int):
		if value != self.__visaTimeout__:
			self.__visaTimeout__ = int(value)
			if self.IsConnected:
				self.Disconnect()
				self.Connect()

	@property
	def IsConnected(self) -> bool:
		return self.__isConnected__
		
	def Connect(self) -> bool:
		self.__isConnected__ = True
		try:
			self.__instr__ = self.__rm__.open_resource(self.Address)
			self.__instr__.timeout = self.VISATimeout
			self.Id = self.__updateId__()
			self.Vendor = self.__updateVendor__()
			self.Model, self.Firmware = self.__updateModelAndFirmware__
		except Exception as e:
			self.__isConnected__ = False
			raise e
		return self.__isConnected__

	def Disconnect(self) -> bool:
		self.__instr__.close()
		self.__isConnected__ = False
		return self.__isConnected__
			
	def Write(self, command: str, args:str=''):
		if self.IsConnected:
			return self.__instr__.write(command + ((' ' + args) if args != '' else ''))
		else:
			raise Exception("The instrument is not connected")

	def Query(self, command: str, args:str=''):
		if self.IsConnected:
			return str(self.__instr__.query(command + '?' + ((' ' + args) if args != '' else ''))).strip('\n').strip('\r').strip('"').lstrip(':').removeprefix(command).strip()
		else:
			raise Exception("The instrument is not connected")

	def Read(self) -> str:
		if self.IsConnected:
			return str(self.__instr__.read()).strip('\n')
		else:
			raise Exception("The instrument is not connected")

	def __updateId__(self) -> str:
		if self.IsConnected:
			return self.__instr__.query('*IDN?')
		else:
			raise Exception("The instrument is not connected")
	
	def __updateVendor__(self, check=False) -> str:
		rematch:re.Match = None
		for vendorAbbreviation in VendorAbbreviation:
			for value in vendorAbbreviation.values:
				rematch = re.match(value, self.Id)
				if rematch:
					if rematch.pos == 0:
						break
		if rematch:
			return rematch.match
		else:
			if check:
				raise Exception("Unknown manufacturer")
			return self.Id.split(',')[0]
		
	def __updateModelAndFirmware__(self):
		modelAndFirmware = self.Id.removeprefix(self.Vendor).rstrip().rstrip('\n').split(',', 2)
		return modelAndFirmware[1], modelAndFirmware[2]

	def SelfTest(self):
		if self.IsConnected:
			if not bool(int(self.__instr__.query('*TST?'))):
				raise Exception('Error in the self test')
		else:
			raise Exception("The instrument is not connected")
	
	def Reset(self):
		if self.IsConnected:
			self.__instr__.write('*RST')
		else:
			raise Exception("The instrument is not connected")

class Source(Instrument):
	def _abort(self):
		self.Reset()

	def __init__(self, address, visaTimeout=Instrument.DEFAULT_VISA_TIMEOUT):
		Instrument.__init__(self, address, visaTimeout)
		self.Abort = self._abort
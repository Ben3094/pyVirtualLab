import pyvisa
import aenum
import enum
import re
from pyvisa import ResourceManager
from pyvisa.resources import Resource
from time import time, sleep
from abc import abstractmethod

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

class VirtualResource:
	def __init__(self):
		pass

	@abstractmethod
	def write(self, value:str) -> None:
		pass
	@abstractmethod
	def read(self) -> str:
		pass
	@abstractmethod
	def query(self, value:str) -> str:
		pass

	@property
	@abstractmethod
	def timeout(self) -> float:
		pass
	@timeout.setter
	@abstractmethod
	def timeout(self, value:float):
		pass

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

ADDRESS_GRAMMAR_SEPARATOR:str = "::"

class InterfaceType(aenum.Enum):
	VXI = 'VXI'
	GPIB_VXI = 'GPIB-VXI'
	GPIB = 'GPIB'
	Serial = 'ASRL' # Means "Asynchronous SeRiaL"
	Ethernet = 'TCPIP'
	USB = 'USB'
	PXI = 'PXI'

class RessourceType(aenum.Enum):
	Instrument = 'INSTR'
	MemoryAccess = 'MEMACC'
	GPIBBus = 'INTFC'
	Backplane = 'BACKPLANE' # Hosts one or several VXI or PXI instruments
	Servant = 'SERVANT'

DEFAULT_RESOURCE_MANAGER = pyvisa.ResourceManager('@py')

class Instrument:
	DEFAULT_VISA_TIMEOUT = 2000

	Id:str = None
	Vendor:str = None
	Model:str = None
	Firmware:str = None
	InterfaceType = None

	def __init__(self, address: str, visaTimeout:int=DEFAULT_VISA_TIMEOUT):
		self.__address__ = address
		self.__isConnected__ = False
		self.__visaTimeout__ = visaTimeout
		self.__resource__:Resource|VirtualResource = None

	@property
	def Resource(self):
		return self.__resource__
	@Resource.setter
	def Resource(self, value):
		isConnected = self.IsConnected
		if isConnected:
			self.Disconnect()
		self.__resource__ = value
		if isConnected:
			self.Connect()

	# See "VPP-4.3: The VISA Library" at 4.3.1.1 section
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
	def ConnectionType(self) -> InterfaceType:
		return 

	@property
	def timeout(self) -> int:
		return self.__visaTimeout__
	@timeout.setter
	def timeout(self, value: int):
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
			if self.__resource__ is VirtualResource:
				self.__resource__ = self.__resource__
			else:
				self.__resource__ = DEFAULT_RESOURCE_MANAGER.open_resource(self.Address)
			self.__resource__.timeout = self.timeout
			self.Id = self.__updateId__()
			self.Vendor = self.__updateVendor__()
			self.Model, self.Firmware = self.__updateModelAndFirmware__()
			self.InterfaceType = self.__updateInterfaceType__() 
		except Exception as e:
			self.__isConnected__ = False
			raise e
		return self.__isConnected__

	def Disconnect(self) -> bool:
		self.__resource__.close()
		self.__isConnected__ = False
		return self.__isConnected__
	def close(self) -> None:
		self.Disconnect()
			
	# See IVI fundation SCPI Volume 1: Syntax and Style
	def write(self, command: str, args:str=''):
		if self.IsConnected:
			return self.__resource__.write(command + ((' ' + args) if args != '' else ''))
		else:
			raise Exception("The instrument is not connected")

	def query(self, command: str, args:str=''):
		if self.IsConnected:
			return str(self.__resource__.query(command + '?' + ((' ' + args) if args != '' else ''))).strip('\n').strip('\r').strip('"').lstrip(':').removeprefix(command).strip()
		else:
			raise Exception("The instrument is not connected")

	def read(self) -> str:
		if self.IsConnected:
			return str(self.__resource__.read()).strip('\n')
		else:
			raise Exception("The instrument is not connected")

	def __updateId__(self) -> str:
		if self.IsConnected:
			return self.__resource__.query('*IDN?')
		else:
			raise Exception("The instrument is not connected")
	
	def __updateVendor__(self, check=False) -> VendorAbbreviation or str:
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
	
	def __updateInterfaceType__(self, check=False) -> InterfaceType or str:
		rematch:re.Match = None
		for interfaceType in InterfaceType:
			for value in interfaceType.values:
				rematch = re.match(value, self.Id)
				if rematch:
					if rematch.pos == 0:
						break
		if rematch:
			return rematch.match
		else:
			if check:
				raise Exception("Unknown instrument type")
			return self.Id.split(',')[0]
		
	def __updateModelAndFirmware__(self):
		modelAndFirmware = self.Id.removeprefix(self.Vendor).rstrip().rstrip('\n').split(',', 2)
		return modelAndFirmware[1], modelAndFirmware[2]
	
	def Wait(self, delay:float=0.01, timeout:float=5):
		startTime:float = time()
		stopTime = startTime+timeout
		while (time() < stopTime) & (self.query('*OPC') != '1'):
			sleep(delay)

	def SelfTest(self):
		if self.IsConnected:
			if not bool(int(self.__resource__.query('*TST?'))):
				raise Exception('Error in the self test')
		else:
			raise Exception("The instrument is not connected")
	
	def Reset(self):
		if self.IsConnected:
			self.__resource__.write('*RST')
		else:
			raise Exception("The instrument is not connected")

class Source(Instrument):
	def __abort__(self):
		self.Reset()

	def __init__(self, address, visaTimeout=Instrument.DEFAULT_VISA_TIMEOUT):
		Instrument.__init__(self, address, visaTimeout)
		self.Abort = self.__abort__

def RECURSIVE_SUBCLASSES(type:type) -> list[type]:
	currentLevelSubclasses = type.__subclasses__()
	deeperLevelSubclasses:list = list()
	for currentLevelSubclass in currentLevelSubclasses:
		deeperLevelSubclasses = deeperLevelSubclasses + RECURSIVE_SUBCLASSES(currentLevelSubclass)
	return currentLevelSubclasses + deeperLevelSubclasses
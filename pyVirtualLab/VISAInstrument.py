from aenum import Enum, MultiValueEnum
from re import match, Match
from pyvisa import ResourceManager
from pyvisa.resources import Resource
from pyvisa_py.protocols.rpc import RPCUnpackError
from time import time, sleep
from threading import Thread
from queue import Queue
from logging import error

def GetProperty(dataType:type, visaGetCommand:str):
	__converter__ = None

	if dataType is float:
		__converter__ = lambda x: float(x)
	elif dataType is int:
		__converter__ = lambda x: int(x)
	elif dataType is bool:
		__converter__ = lambda x: bool(int(x))
	elif dataType is str:
		__converter__ = lambda x: x
	else:
		__converter__ = lambda x: dataType(x)

	def decorator(func):
		def wrapper(*args, **kwargs):
			command = visaGetCommand.format(**args[0].__dict__)
			kwargs['getMethodReturn'] = __converter__(args[0].Query(command))
			return func(*args, **kwargs)
		return wrapper
	return decorator

def SetProperty(dataType:type, visaSetCommand:str):
	__converter__ = None

	if dataType is float:
		__converter__ = lambda x: str(float(x))
	elif dataType is int:
		__converter__ = lambda x: str(int(x))
	elif dataType is bool:
		__converter__ = lambda x: str(int(bool(x)))
	elif dataType is str:
		__converter__ = lambda x: str(x)
	elif issubclass(dataType, Enum):
		__converter__ = lambda x: str(dataType(x).value)
	elif issubclass(dataType, MultiValueEnum):
		__converter__ = lambda x: str(dataType(x).value)
	else:
		__converter__ = lambda x: x.__repr__

	def decorator(func):
		def wrapper(*args, **kwargs):
			command = visaSetCommand.format(**args[0].__dict__)
			args[0].Write(command, __converter__(args[1]))
			if getattr(args[0], func.__name__) != args[1]:
				raise Exception(f"Error while setting \"{func.__name__}\"")
			return func(*args, **kwargs)
		return wrapper
	return decorator

class VirtualResource(Resource):
	__resource__:Resource=None

	def __init__(self, resource:Resource):
		self.__resource__ = resource

	def write(self, value:str) -> None:
		self.__resource__.write(value)
	def read(self) -> str:
		return self.__resource__.write()
	def query(self, value:str) -> str:
		return self.__resource__.query(value)

	@property
	def timeout(self) -> float:
		return self.__resource__.timeout
	@timeout.setter
	def timeout(self, value:float):
		self.__resource__.timeout = value

	@property
	def stb(self) -> int:
		return int(self.__resource__.query('*STB?'))

	def open(self) -> None:
		error("Connection opening cannot be asked from a virtual resource")
	def close(self) -> None:
		error("Connection closing cannot be asked from a virtual resource")

# See IVI foundation VXI plug&play System Alliance VPP-9: Instrument Vendor Abbreviations
class VendorAbbreviation(MultiValueEnum):
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
	AU1 = "Anritsu Company"
	AT1 = "Astronics Test Systems Inc."
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
	AU2 = "Serendipity Systems, Inc."
	SI = "SignalCraft Technologies Inc."
	ST = "Sony/Tektronix Corporation"
	SS = "Spectrum Signal Processing, Inc."
	SP = "Spitzenberger & Spies GmbH"
	TA = "Talon Instruments"
	TK = "Tektronix, Inc."
	TE = "Teradyne"
	TS = "Test & Measurement Systems Inc."
	RF = "ThinkRF Corporation"
	AT2 = "Thurlby Thandar Instruments Limited Transmagnetics, Inc.", "THURLBY THANDAR"
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
def PARSE_VENDOR(intrumentId:str, check=False) -> VendorAbbreviation | str:
	rematch:Match = None
	vendorID = intrumentId.split(',')[0].lower()
	for vendorAbbreviation in VendorAbbreviation:
		for value in vendorAbbreviation.values:
			rematch = vendorID == value.lower()
			if rematch:
				return vendorAbbreviation
	if check:
		raise Exception("Unknown manufacturer")
	return vendorID
		
def PARSE_MODEL_AND_FIRMWARE(instrumentId: str, instrumentVendor: str):
	modelAndFirmware = instrumentId.removeprefix(instrumentVendor).rstrip().rstrip('\n').split(',', 2)
	return modelAndFirmware[1].strip(), modelAndFirmware[2].strip()

ADDRESS_GRAMMAR_SEPARATOR:str = "::"

INTERFACE_TYPE_ENTRY_NAME:str = "Interface type"
class InterfaceType(Enum):
	VXI = 'VXI'
	GPIB_VXI = 'GPIB-VXI'
	GPIB = 'GPIB'
	Serial = 'ASRL' # Means "Asynchronous SeRiaL"
	Ethernet = 'TCPIP'
	USB = 'USB'
	PXI = 'PXI'
INTERFACE_BOARD_ENTRY_NAME:str = "Interface board"
PXI_BUS_ENTRY_NAME:str = "PXI bus"
PXI_INTERFACE_ENTRY_NAME:str = "PXI interface"
def PARSE_INTERFACE_TYPE(value: str) -> tuple[InterfaceType, int]:
	rematch:Match = None
	for interfaceType in InterfaceType:
		for interfaceTypeString in interfaceType.values:
			rematch = match(f"{interfaceTypeString}(\\d*)", value)
			if rematch:
				return (interfaceType, int(rematch[1]) if rematch[1] != '' else None)
	return (None, None)
VXI_LOGICAL_ADDRESS_ENTRY_NAME:str = "Logical address"
GPIB_ADDRESS_ENTRY_NAME:str = "GPIB address"
GPIB_SECONDARY_ADDRESS_ENTRY_NAME:str = "GPIB secondary address"
ETHERNET_DEVICE_NAME_ENTRY_NAME:str = "Device name"
ETHERNET_HOST_ADDRESS_ENTRY_NAME:str = "Host address"
ETHERNET_PORT_ENTRY_NAME:str = "Port"
USB_MANUFACTURER_ID_ENTRY_NAME:str = "Manufacturer ID"
USB_MODEL_CODE_ENTRY_NAME:str = "Model code"
USB_SERIAL_NUMBER_ENTRY_NAME:str = "Serial number"
USB_INTERFACE_NUMBER_ENTRY_NAME:str = "Interface number"
PXI_CHASSIS_NUMBER_ENTRY_NAME:str = "Chassis number"

class ResourceType(Enum):
	Instrument = 'INSTR'
	MemoryAccess = 'MEMACC'
	GPIBBus = 'INTFC'
	Backplane = 'BACKPLANE' # Hosts one or several VXI or PXI instruments
	Servant = 'SERVANT'
	Socket = 'SOCKET'
def PARSE_RESOURCE_TYPE(value) -> ResourceType:
	rematch:Match = None
	for resourceType in ResourceType:
		for resourceTypeString in resourceType.values:
			rematch = match(resourceTypeString, value)
			if rematch:
				return resourceType
	return None
def PARSE_ADDRESS(value:str) -> tuple[InterfaceType, dict[str, object], ResourceType]:
	interfaceProperties:dict[str, object] = dict()
	value = value.split(ADDRESS_GRAMMAR_SEPARATOR)

	interfaceType, interfaceIndex = PARSE_INTERFACE_TYPE(value[0])
	try:
		resourceType = PARSE_RESOURCE_TYPE(value[-1])
		del value[-1]
	except Exception:
		resourceType = ResourceType.Instrument

	match interfaceType:
		case InterfaceType.VXI:
			interfaceProperties[INTERFACE_BOARD_ENTRY_NAME] = interfaceIndex
			match resourceType:
				case ResourceType.MemoryAccess|ResourceType.Servant:
					pass
				case ResourceType.Backplane|ResourceType.Instrument:
					interfaceProperties[VXI_LOGICAL_ADDRESS_ENTRY_NAME] = value[1]
				case _:
					raise Exception("Resource type is not suitable for a VXI interface")
		case InterfaceType.GPIB_VXI:
			interfaceProperties[INTERFACE_BOARD_ENTRY_NAME] = interfaceIndex
			match resourceType:
				case ResourceType.MemoryAccess:
					pass
				case ResourceType.Backplane|ResourceType.Instrument:
					interfaceProperties[VXI_LOGICAL_ADDRESS_ENTRY_NAME] = value[1]
				case _:
					raise Exception("Resource type is not suitable for a GPIB-VXI interface")

		case InterfaceType.GPIB:
			interfaceProperties[INTERFACE_BOARD_ENTRY_NAME] = interfaceIndex
			match resourceType:
				case ResourceType.GPIBBus|ResourceType.Servant:
					pass
				case ResourceType.Instrument:
					interfaceProperties[GPIB_ADDRESS_ENTRY_NAME] = value[1]
					interfaceProperties[GPIB_SECONDARY_ADDRESS_ENTRY_NAME] = value[2]
		case InterfaceType.Serial:
			interfaceProperties[INTERFACE_BOARD_ENTRY_NAME] = interfaceIndex

		case InterfaceType.Ethernet:
			interfaceProperties[INTERFACE_BOARD_ENTRY_NAME] = interfaceIndex
			if resourceType == ResourceType.Servant:
				interfaceProperties[ETHERNET_DEVICE_NAME_ENTRY_NAME] = value[1]
			else:
				interfaceProperties[ETHERNET_HOST_ADDRESS_ENTRY_NAME] = value[1]
				if resourceType == ResourceType.Socket:
					interfaceProperties[ETHERNET_PORT_ENTRY_NAME] = int(value[2])
				else:
					interfaceProperties[ETHERNET_DEVICE_NAME_ENTRY_NAME] = value[2]
					if len(value) > 3:
						interfaceProperties[ETHERNET_PORT_ENTRY_NAME] = int(value[3])	

		case InterfaceType.USB:
			interfaceProperties[INTERFACE_BOARD_ENTRY_NAME] = interfaceIndex
			interfaceProperties[USB_MANUFACTURER_ID_ENTRY_NAME] = value[1]
			interfaceProperties[USB_MODEL_CODE_ENTRY_NAME] = value[2]
			interfaceProperties[USB_SERIAL_NUMBER_ENTRY_NAME] = value[3]
			if len(value) > 4:
				interfaceProperties[USB_INTERFACE_NUMBER_ENTRY_NAME] = value[4]
		case InterfaceType.PXI:
			match resourceType:
				case ResourceType.Backplane:
					interfaceProperties[INTERFACE_BOARD_ENTRY_NAME] = interfaceIndex
					interfaceProperties[PXI_CHASSIS_NUMBER_ENTRY_NAME] = value[1]
				case ResourceType.MemoryAccess:
					interfaceProperties[INTERFACE_BOARD_ENTRY_NAME] = interfaceIndex
				case ResourceType.Instrument:
					raise NotImplementedError()

	return interfaceType, interfaceProperties, resourceType

try:
	DEFAULT_RESOURCE_MANAGER = ResourceManager()
except Exception:
	DEFAULT_RESOURCE_MANAGER = ResourceManager('@py')

class Instrument:
	DEFAULT_VISA_TIMEOUT = 2000

	Id:str = None
	Vendor:str = None
	Model:str = None
	Firmware:str = None

	def __init__(self, address: str=None, timeout: int=DEFAULT_VISA_TIMEOUT):
		self.__address__: str = None
		self.__timeout__: int = None
		self.__resource__: Resource|VirtualResource = None
		self.__interfaceType__: InterfaceType = None
		self.__interfaceProperties__: dict[str, object] = dict()
		self.__resourceType__: ResourceType = None

		self.Address = address
		self.Timeout = timeout

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
			self.__interfaceType__, self.__interfaceProperties__, self.__resourceType__ = PARSE_ADDRESS(value)
			if self.IsConnected:
				self.Disconnect()
				self.Connect()
		return self.__address__
	
	@property
	def InterfaceType(self):
		return self.__interfaceType__
	@property
	def InterfaceProperties(self) -> dict[str, object]:
		return self.__interfaceProperties__
	@property
	def ResourceType(self):
		return self.__resourceType__

	@property
	def Timeout(self) -> int:
		return self.__resource__.timeout
	@Timeout.setter
	def Timeout(self, value: int):
		if value != self.__timeout__:
			self.__timeout__ = int(value)
			if self.IsConnected:
				self.Disconnect()
				self.Connect()

	def __getConnectionStatus__(self, outValue: Queue):
		try:
			self.__resource__.query('*STB?')
			outValue.put(True)
		except RPCUnpackError:
			outValue.put(True)
		except Exception as e:
			outValue.put(False)
	STB_QUERY_TIMEOUT:float = 3
	@property
	def IsConnected(self) -> bool:
		outValue = Queue()
		thread = Thread(target=self.__getConnectionStatus__, args=[outValue], name=f"Is {str(self)} connected")
		thread.start()
		thread.join(timeout=Instrument.STB_QUERY_TIMEOUT)
		if not thread.is_alive():
			return outValue.get()
		else:
			return False
		
	def Connect(self) -> bool:
		try:
			if not issubclass(type(self.__resource__), VirtualResource):
				self.__resource__ = DEFAULT_RESOURCE_MANAGER.open_resource(self.Address, timeout=self.__timeout__)
			self.Id = self.__updateId__()
			self.Vendor = PARSE_VENDOR(self.Id)
			self.Model, self.Firmware = PARSE_MODEL_AND_FIRMWARE(self.Id, self.Vendor.values[0] if issubclass(type(self.Vendor), VendorAbbreviation) else self.Vendor)
		except Exception as e:
			raise e
		return self.IsConnected

	def Disconnect(self) -> bool:
		self.__resource__.close()
		return self.IsConnected
	def close(self) -> None:
		self.Disconnect()
			
	# See IVI fundation SCPI Volume 1: Syntax and Style
	def Write(self, command: str, args:str=''):
		args = str(args)
		if self.IsConnected:
			return self.__resource__.write(command + ((' ' + args) if args != '' else ''))
		else:
			raise Exception("The instrument is not connected")

	def Query(self, command: str, args:str=''):
		args = str(args)
		if self.IsConnected:
			return str(self.__resource__.query(command + '?' + ((' ' + args) if args != '' else ''))).strip('\n').strip('\r').strip('"').lstrip(':').removeprefix(command).strip()
		else:
			raise Exception("The instrument is not connected")

	def Read(self) -> str:
		if self.IsConnected:
			return str(self.__resource__.read()).strip('\n')
		else:
			raise Exception("The instrument is not connected")

	def __updateId__(self) -> str:
		if self.IsConnected:
			return self.__resource__.query('*IDN?')
		else:
			raise Exception("The instrument is not connected")
	
	def Wait(self, delay:float=0.01, timeout:float=5):
		startTime:float = time()
		stopTime = startTime+timeout
		while (time() < stopTime) & (self.Query('*OPC') != '1'):
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
		
	def __repr__(self) -> str:
		if self.Vendor:
			return self.Vendor.values[0] if issubclass(type(self.Vendor), VendorAbbreviation) else self.Vendor + self.Model
		else:
			return str(self.Address)

class Source(Instrument):
	def __abort__(self):
		self.Reset()

	def __init__(self, address, timeout=Instrument.DEFAULT_VISA_TIMEOUT):
		Instrument.__init__(self, address, timeout)
		self.Abort = self.__abort__

def RECURSIVE_SUBCLASSES(type:type) -> list[type]:
	currentLevelSubclasses = type.__subclasses__()
	deeperLevelSubclasses:list = list()
	for currentLevelSubclass in currentLevelSubclasses:
		deeperLevelSubclasses = deeperLevelSubclasses + RECURSIVE_SUBCLASSES(currentLevelSubclass)
	return currentLevelSubclasses + deeperLevelSubclasses

class VirtualInstrument(Instrument):
	__instrument__:Instrument=None

	Id:str = None
	Vendor:str = None
	Model:str = None
	Firmware:str = None

	def __init__(self, instrument:Instrument):
		Instrument.__init__(self)
		self.__instrument__ = instrument
		self.__interfaceType__: InterfaceType = None
		self.__interfaceProperties__: dict[str, object] = dict()
		self.__resourceType__: ResourceType = None

	@property
	def Resource(self):
		return self.__instrument__.__resource__
	@Resource.setter
	def Resource(self, value):
		error("Impossible to set ressource within a virtual instrument")

	@property
	def Address(self) -> str:
		return self.__instrument__.__address__
	@Address.setter
	def Address(self, value: str) -> str:
		pass
	
	@property
	def InterfaceType(self):
		return self.__instrument__.__interfaceType__
	@property
	def InterfaceProperties(self) -> dict[str, object]:
		return self.__instrument__.__interfaceProperties__
	@property
	def ResourceType(self):
		return self.__instrument__.__resourceType__

	@property
	def Timeout(self) -> int:
		return self.__instrument__.__resource__.timeout
	@Timeout.setter
	def Timeout(self, value: int):
		pass

	@property
	def IsConnected(self) -> bool:
		return self.__instrument__.IsConnected
	def Connect(self) -> bool:
		error("Impossible to change connection status within a virtual instrument")
	def Disconnect(self) -> bool:
		error("Impossible to change connection status within a virtual instrument")
	def close(self) -> None:
		self.Disconnect()
	
	def Write(self, command: str, args:str=''):
		return self.__instrument__.Write(command, args)
	def Query(self, command: str, args:str=''):
		return self.__instrument__.Query(command, args)
	def Read(self) -> str:
		return self.__instrument__.Read()
	
	def Wait(self, delay:float=0.01, timeout:float=5):
		self.__instrument__.Wait(delay, timeout)
	def SelfTest(self):
		self.__instrument__.SelfTest()
	def Reset(self):
		self.__instrument__.Reset()
		
	def __repr__(self) -> str:
		if self.Vendor:
			return self.Vendor.values[0] if issubclass(type(self.Vendor), VendorAbbreviation) else self.Vendor + self.Model
		else:
			return str(self.Address)
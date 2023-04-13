import pyvisa
import aenum
import enum

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

class Instrument:
	DEFAULT_VISA_TIMEOUT = 2000

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
			self.Id
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

	def Id(self) -> str:
		if self.IsConnected:
			return self.__instr__.query('*IDN?')
		else:
			raise Exception("The instrument is not connected")

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
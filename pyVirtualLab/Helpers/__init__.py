def RECURSIVE_SUBCLASSES(type:type) -> list[type]:
	currentLevelSubclasses = type.__subclasses__()
	deeperLevelSubclasses:list = list()
	for currentLevelSubclass in currentLevelSubclasses:
		deeperLevelSubclasses = deeperLevelSubclasses + RECURSIVE_SUBCLASSES(currentLevelSubclass)
	return currentLevelSubclasses + deeperLevelSubclasses

from aenum import Enum, MultiValueEnum
from collections import namedtuple
from typing import Callable

Converter = namedtuple("Converter", ['Get', 'Set'])
ConvertersRegistry:dict[type, Converter] = {
	float: Converter(Get=lambda x: float(x), Set=lambda x: str(float(x))),
	int: Converter(Get=lambda x: int(x), Set=lambda x: str(int(x))),
	bool: Converter(Get=lambda x: bool(int(x)), Set=lambda x: str(int(bool(x)))),
	str: Converter(Get=lambda x: str(x).lstrip('\"').rstrip('\"'), Set=lambda x: f"\"{str(x)}\"")
}

def GetProperty(dataType:type, visaGetCommand:str, converter:Converter=None, booleanStatePropertyName:str=None, offStateValue=None):
	if converter == None:
		if dataType in ConvertersRegistry:
			converter = ConvertersRegistry[dataType].Get
		else:
			converter = lambda x: dataType(x)

	def decorator(func):
		def wrapper(*args, **kwargs):
			if (booleanStatePropertyName != None) and (not getattr(args[0], booleanStatePropertyName)):
					kwargs['getMethodReturn'] = offStateValue
			else:
				command = visaGetCommand.format(**args[0].__dict__)
				kwargs['getMethodReturn'] = converter(args[0].Query(command))
			return func(*args, **kwargs)
		return wrapper
	return decorator

def SetProperty(dataType:type, visaSetCommand:str, check:bool=True, converter:Converter=None, rounding:Callable=lambda x: x, booleanStatePropertyName:str=None, offStateValue=None):
	if converter == None:
		if dataType in ConvertersRegistry:
			converter = ConvertersRegistry[dataType].Set
		elif issubclass(dataType, Enum):
			converter = lambda x: str(dataType(x).value)
		elif issubclass(dataType, MultiValueEnum):
			converter = lambda x: str(dataType(x).value)
		else:
			converter = lambda x: x.__repr__

	def decorator(func):
		def wrapper(*args, **kwargs):
			state = True
			value = rounding(args[1])
			if booleanStatePropertyName != None:
				state = value != offStateValue
				setattr(args[0], booleanStatePropertyName, state)
			if state:
				command = visaSetCommand.format(**args[0].__dict__)
				args[0].Write(command, converter(value))
			if check:
				if getattr(args[0], func.__name__) != value:
					raise Exception(f"Error while setting \"{func.__name__}\"")
			return func(*args, **kwargs)
		return wrapper
	return decorator

LOG_FORMAT_ARGUMENT:str = 'LOG'
LINEAR_FORMAT_ARGUMENT:str = 'LIN'
boolToLogLinStringConverter = lambda x: LOG_FORMAT_ARGUMENT if x else LINEAR_FORMAT_ARGUMENT
logLinStringToBoolConverter = lambda x: x == LOG_FORMAT_ARGUMENT

from math import floor, log10
@staticmethod
def roundScientificNumber(number:float, decimalToKeep:int):
	if number == 0:
		return number
	power = floor(log10(abs(number)))
	return round(round(number * pow(10, -power), decimalToKeep) * pow(10, power), 21)
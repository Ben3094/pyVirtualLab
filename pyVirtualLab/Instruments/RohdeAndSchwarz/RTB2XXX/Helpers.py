from aenum import Enum

class DataFormat(Enum):
	ASCII = 'ASC,0'
	FloatingPoint32Bits = 'REAL,32'
	UnsignedInteger8Bits = 'UINT,8'
	UnsignedInteger16Bits = 'UINT,16'
	UnsignedInteger32its = 'UINT,32'
	CSV = 'CSV,0'
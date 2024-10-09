from pyVirtualLab.VISAInstrument import Source
from pyVirtualLab.Instruments.KeysightE363XXX.Outputs import *

OUTPUTS_NUMBER:int = 3
OUTPUTS_START_INDEX:int = 1
OUTPUTS_INDEXES:range = range(OUTPUTS_START_INDEX, OUTPUTS_START_INDEX + OUTPUTS_NUMBER)

class KeysightE363XXX(Source):
	def __init__(self, address):
		super(KeysightE363XXX, self).__init__(address)
		self.__outputs__:dict[int, Output] = None
	
	@property
	def Outputs(self) -> Output:
		if self.__outputs__ == None:
			self.__outputs__ = dict()
			for index in OUTPUTS_INDEXES:
				self.__outputs__[index] = Output(self, index)

		return self.__outputs__
	
	def SetOutputsState(self, outputs:list[Output], enabled:bool):
		self.Write('OUTP:STAT', f"{str(int(enabled))}, (@{','.join([str(output) for output in outputs])})")
	
	def __abort__(self):
		self.SetOutputsState(self.Outputs, False)
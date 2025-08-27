from pyVirtualLab.VISAInstrument import Source
from pyVirtualLab.Helpers import GetProperty, SetProperty
from .Output import Output

class TektronixAWG70000(Source):
	def __init__(self, address: str):
		super(TektronixAWG70000, self).__init__(address)
	
	STATE_COMMNAD:str = 'OUTP:STAT'
	@property
	@GetProperty(bool, STATE_COMMNAD)
	def IsEnabled(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsEnabled.setter
	@SetProperty(bool, STATE_COMMNAD)
	def IsEnabled(self, value:bool) -> bool:
		pass
	def __abort__(self):
		self.IsEnabled = False
		
	MAX_OUTPUTS:int = 4

	__outputs__:dict[int, Output] = None
	@property
	def Outputs(self) -> dict[int, Output]:
		if self.__outputs__ == None:
			self.__outputs__ = dict()
			address = 0
			while address <= TektronixAWG70000.MAX_OUTPUTS:
				address += 1
				try:
					self.Query(f"{Output.COMMAND_PREFIX}{address}:{Output.STATE_COMMNAD}")
					self.__outputs__[address] = Output(self, address)
				except:
					break
		return self.__outputs__
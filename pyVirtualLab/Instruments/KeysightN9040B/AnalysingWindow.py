from pyVirtualLab.Helpers import GetProperty, SetProperty

class AnalysingWindow:
	MODE_COMMAND:str = 'INST:SEL'
	MODE_NAME:str = None
	
	__parent__ = None
	@property
	def Parent(self):
		return self.__parent__
	
	__name__:str = None

	CREATE_ANALYSING_WINDOW_COMMAND:str = 'INST:SCR:CRE'
	def __init__(self, parent, isAddedLocaly:bool=True):
		self.__parent__ = parent
		if isAddedLocaly:
			self.__parent__.Write(AnalysingWindow.CREATE_ANALYSING_WINDOW_COMMAND)
		self.__name__ = self.__parent__.FocusedAnalysingWindowName
		self.Write(AnalysingWindow.MODE_COMMAND, self.MODE_NAME)
		self.__parent__.__analysingWindows__.append(self)
	
	def Read(self) -> str:
		self.__parent__.FocusedAnalysingWindowName = self.Name
		return self.__parent__.Read()
	def Write(self, command:str, arguments:str) -> str:
		self.__parent__.FocusedAnalysingWindowName = self.Name
		return self.__parent__.Write(command, arguments)
	def Query(self, command:str, arguments:str='') -> str:
		self.__parent__.FocusedAnalysingWindowName = self.Name
		return self.__parent__.Query(command, arguments)
	
	RENAME_COMMAND:str = 'INST:SCR:REN'
	__name__:str = None
	
	@property
	def Name(self) -> str:
		return self.__name__
	@Name.setter
	def Name(self, value) -> str:
		value = str(value)
		self.Write(AnalysingWindow.RENAME_COMMAND, value)
		if value != self.__parent__.FocusedAnalysingWindowName:
			raise Exception("Error while renaming")
		return value
	
	@property
	def IsFocused(self) -> bool:
		return self.__parent__.FocusedAnalysingWindowName == self.Name
	
	DELETE_COMMAND:str = 'INST:SCR:DEL'
	def Delete(self):
		self.__parent__.__analysingWindows__.remove(self)
		self.Write(AnalysingWindow.DELETE_COMMAND)
	def __del__(self):
		self.Delete()
	
	DELETE_OTHERS_COMMAND:str = 'INST:SCR:DEL:ALL'
	def DeleteOthers(self):
		self.Write(AnalysingWindow.DELETE_OTHERS_COMMAND)

	FULLSCREEN_COMMAND:str = 'DISP:FSCR'
	@property
	@GetProperty(bool, FULLSCREEN_COMMAND)
	def IsFullscreen(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsFullscreen.setter
	@SetProperty(bool, FULLSCREEN_COMMAND)
	def IsFullscreen(self, value) -> bool:
		pass
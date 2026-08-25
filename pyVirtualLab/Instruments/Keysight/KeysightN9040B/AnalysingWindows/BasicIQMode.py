from ..AnalysingWindow import AnalysingWindow
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES, GetProperty, SetProperty, logLinStringToBoolConverter, boolToLogLinStringConverter
from .. import PowerUnit, Path, Average, DataFormat
from aenum import Enum

class BasicIQView:
	VIEW_NAME:str = None
	
	__parent__ = None
	@property
	def Parent(self):
		return self.__parent__

	VIEW_COMMAND = 'DISP:VIEW'
	def __init__(self, parent):
		self.__parent__ = parent
		self.__parent__.Write(BasicIQView.VIEW_COMMAND, self.VIEW_NAME)
		self.__parent__.__view__ = self
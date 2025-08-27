from ..AnalysingWindow import AnalysingWindow
from pyVirtualLab.Helpers import RECURSIVE_SUBCLASSES, GetProperty, SetProperty, logLinStringToBoolConverter, boolToLogLinStringConverter
from .. import PowerUnit, Path, Average, DataFormat

class SpectrumAnalyseView:
	VIEW_NAME:str = None
	
	__parent__ = None
	@property
	def Parent(self):
		return self.__parent__

	VIEW_COMMAND = 'DISP:VIEW'
	def __init__(self, parent):
		self.__parent__ = parent
		self.__parent__.Write(SpectrumAnalyseView.VIEW_COMMAND, self.VIEW_NAME)
		self.__parent__.__view__ = self

class NormalView(SpectrumAnalyseView):
	VIEW_NAME:str = 'NORM'

class SpectrogramView(SpectrumAnalyseView):
	VIEW_NAME:str = 'SPEC'
	
	DURATION_COMMAND:str = 'TRAC:DISP:VIEW:SPEC:TIME'
	@property
	@GetProperty(float, DURATION_COMMAND)
	def Duration(self, getMethodReturn) -> float:
		return getMethodReturn
	@Duration.setter
	@SetProperty(float, DURATION_COMMAND)
	def Duration(self) -> float:
		pass
	
	DISPLAYED_TRACE_POSITION_COMMAND:str = 'TRAC:DISP:VIEW:SPEC:TIME'
	@property
	@GetProperty(int, DISPLAYED_TRACE_POSITION_COMMAND)
	def DisplayedTracePosition(self, getMethodReturn) -> int:
		return getMethodReturn
	@DisplayedTracePosition.setter
	@SetProperty(int, DISPLAYED_TRACE_POSITION_COMMAND)
	def DisplayedTracePosition(self) -> int:
		pass

	MARKER_ON_DISPLAYED_TRACE_COMMAND:str = 'TRAC:DISP:VIEW:SPEC:COUPLE'
	@property
	@GetProperty(bool, MARKER_ON_DISPLAYED_TRACE_COMMAND)
	def MarkerOnDisplayedTrace(self, getMethodReturn) -> bool:
		return getMethodReturn
	@MarkerOnDisplayedTrace.setter
	@SetProperty(bool, MARKER_ON_DISPLAYED_TRACE_COMMAND)
	def MarkerOnDisplayedTrace(self) -> bool:
		pass

class TraceZoomView(SpectrumAnalyseView):
	VIEW_NAME:str = 'TZO'

	CENTER_FREQUENCY_COMMAND:str = 'SENS:FREQ:TZO:CENT'
	@property
	@GetProperty(float, CENTER_FREQUENCY_COMMAND)
	def CenterFrequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@CenterFrequency.setter
	@SetProperty(float, CENTER_FREQUENCY_COMMAND)
	def CenterFrequency(self, value:float) -> float:
		pass

	SPAN_COMMAND:str = 'SENS:FREQ:TZO:SPAN'
	@property
	@GetProperty(float, SPAN_COMMAND)
	def Span(self, getMethodReturn) -> float:
		return getMethodReturn
	@Span.setter
	@SetProperty(float, SPAN_COMMAND)
	def Span(self, value:float) -> float:
		pass

class ZoneSpanView(SpectrumAnalyseView):
	VIEW_NAME:str = 'ZSP'

	CENTER_FREQUENCY_COMMAND:str = 'SENS:FREQ:ZSP:CENT'
	@property
	@GetProperty(float, CENTER_FREQUENCY_COMMAND)
	def CenterFrequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@CenterFrequency.setter
	@SetProperty(float, CENTER_FREQUENCY_COMMAND)
	def CenterFrequency(self, value:float) -> float:
		pass

	SPAN_COMMAND:str = 'SENS:FREQ:ZSP:SPAN'
	@property
	@GetProperty(float, SPAN_COMMAND)
	def Span(self, getMethodReturn) -> float:
		return getMethodReturn
	@Span.setter
	@SetProperty(float, SPAN_COMMAND)
	def Span(self, value:float) -> float:
		pass

class SpectrumAnalyse(AnalysingWindow):
	MODE_NAME:str = "SA"

	REFERENCE_LEVEL_COMMAND:str = 'DISP:WIND:TRAC:Y:SCAL:RLEV'
	@property
	@GetProperty(float, REFERENCE_LEVEL_COMMAND)
	def ReferenceLevel(self, getMethodReturn) -> float:
		return getMethodReturn
	@ReferenceLevel.setter
	@SetProperty(float, REFERENCE_LEVEL_COMMAND)
	def ReferenceLevel(self, value:float) -> float:
		pass

	SCALE_COMMAND:str = 'DISP:WIND:TRAC:Y:SCAL:PDIV'
	@property
	@GetProperty(float, SCALE_COMMAND)
	def Scale(self, getMethodReturn) -> float:
		return getMethodReturn
	@Scale.setter
	@SetProperty(float, SCALE_COMMAND)
	def Scale(self, value:float) -> float:
		pass

	VERTICAL_LOG_FORMAT_COMMAND:str = 'DISP:WIND:TRAC:Y:SCAL:SPAC'
	VERTICAL_LOG_FORMAT_ARGUMENT:str = 'LOG'
	VERTICAL_LINEAR_FORMAT_ARGUMENT:str = 'LIN'
	@property
	@GetProperty(bool, VERTICAL_LOG_FORMAT_COMMAND, converter = logLinStringToBoolConverter)
	def IsVerticalAxisLogFormat(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsVerticalAxisLogFormat.setter
	@SetProperty(bool, VERTICAL_LOG_FORMAT_COMMAND, converter = boolToLogLinStringConverter)
	def IsVerticalAxisLogFormat(self, value:bool) -> bool:
		pass

	VERTICAL_UNIT_COMMAND:str = 'UNIT:POW'
	@property
	@GetProperty(PowerUnit, VERTICAL_UNIT_COMMAND)
	def VerticalUnit(self, getMethodReturn) -> PowerUnit:
		return getMethodReturn
	@VerticalUnit.setter
	@SetProperty(PowerUnit, VERTICAL_UNIT_COMMAND)
	def VerticalUnit(self, value:PowerUnit) -> PowerUnit:
		pass

	OFFSET_STATE_COMMAND:str = 'DISP:WIND:TRAC:Y:RLEV:OFFS:STAT'
	@property
	@GetProperty(bool, OFFSET_STATE_COMMAND)
	def __offsetState__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__offsetState__.setter
	@SetProperty(bool, OFFSET_STATE_COMMAND)
	def __offsetState__(self, value:bool) -> bool:
		pass
	OFFSET_COMMAND:str = 'DISP:WIND:TRAC:Y:RLEV:OFFS'
	@property
	@GetProperty(float, OFFSET_COMMAND, booleanStatePropertyName='__offsetState__', offStateValue=0)
	def Offset(self, getMethodReturn) -> float:
		return getMethodReturn
	@Offset.setter
	@SetProperty(float, OFFSET_COMMAND, booleanStatePropertyName='__offsetState__', offStateValue=0)
	def Offset(self, value:float) -> float:
		pass

	MECHANIC_ATTENUATION_STATE_COMMAND:str = 'SENS:POW:RF:ATT:AUTO'
	@property
	@GetProperty(bool, MECHANIC_ATTENUATION_STATE_COMMAND)
	def __mechanicAttenuationState__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__mechanicAttenuationState__.setter
	@SetProperty(bool, MECHANIC_ATTENUATION_STATE_COMMAND)
	def __mechanicAttenuationState__(self, value:bool) -> bool:
		pass
	MECHANIC_ATTENUATION_COMMAND:str = 'SENS:POW:RF:ATT'
	@property
	@GetProperty(float, MECHANIC_ATTENUATION_COMMAND, booleanStatePropertyName='__mechanicAttenuationState__', offStateValue=0)
	def MechanicAttenuation(self, getMethodReturn) -> float:
		return getMethodReturn
	@MechanicAttenuation.setter
	@SetProperty(float, MECHANIC_ATTENUATION_COMMAND, booleanStatePropertyName='__mechanicAttenuationState__', offStateValue=0)
	def MechanicAttenuation(self, value:float) -> float:
		pass

	ADJUST_PRESELECTOR_FILTER_COMMAND:str = 'SENS:POW:RF:PCEN'
	def AdjustPreselectorFilter(self):
		self.Write(SpectrumAnalyse.ADJUST_PRESELECTOR_FILTER_COMMAND)
	
	PRESELECTOR_FILTER_FREQUENCY_COMMAND:str = 'SENS:POW:RF:PADJ'
	@property
	@GetProperty(float, PRESELECTOR_FILTER_FREQUENCY_COMMAND)
	def PreselectorFilterFrequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@PreselectorFilterFrequency.setter
	@SetProperty(float, PRESELECTOR_FILTER_FREQUENCY_COMMAND)
	def PreselectorFilterFrequency(self, value:float) -> float:
		pass

	PATH_COMMAND:str = 'SENS:POW:RF:MW:PATH'
	@property
	@GetProperty(Path, PATH_COMMAND)
	def SignalPath(self, getMethodReturn) -> Path:
		return getMethodReturn
	@SignalPath.setter
	@SetProperty(Path, PATH_COMMAND)
	def SignalPath(self, value:Path) -> Path:
		pass

	AUTO_RESOLUTION_BANDWIDTH_COMMAND:str = 'SENS:BWID:RES:AUTO'
	@property
	@GetProperty(bool, AUTO_RESOLUTION_BANDWIDTH_COMMAND)
	def __autoResolutionBandwidth__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__autoResolutionBandwidth__.setter
	@SetProperty(bool, AUTO_RESOLUTION_BANDWIDTH_COMMAND)
	def __autoResolutionBandwidth__(self, value:bool) -> bool:
		pass
	RESOLUTION_BANDWIDTH_COMMAND:str = 'SENS:BWID:RES'
	@property
	@GetProperty(float, RESOLUTION_BANDWIDTH_COMMAND, booleanStatePropertyName='__autoResolutionBandwidth__', offStateValue=None)
	def ResolutionBandwidth(self, getMethodReturn) -> float:
		return getMethodReturn
	@ResolutionBandwidth.setter
	@SetProperty(float, RESOLUTION_BANDWIDTH_COMMAND, rounding=lambda x: round(x, 0), booleanStatePropertyName='__autoResolutionBandwidth__', offStateValue=None)
	def ResolutionBandwidth(self, value:float) -> float:
		pass

	AUTO_VIDEO_BANDWIDTH_COMMAND:str = 'SENS:BWID:VID:AUTO'
	@property
	@GetProperty(bool, AUTO_VIDEO_BANDWIDTH_COMMAND)
	def __autoVideoBandwidth__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__autoVideoBandwidth__.setter
	@SetProperty(bool, AUTO_VIDEO_BANDWIDTH_COMMAND)
	def __autoVideoBandwidth__(self, value:bool) -> bool:
		pass
	VIDEO_BANDWIDTH_COMMAND:str = 'SENS:BWID:VID'
	@property
	@GetProperty(float, VIDEO_BANDWIDTH_COMMAND, booleanStatePropertyName='__autoVideoBandwidth__', offStateValue=None)
	def VideoBandwidth(self, getMethodReturn) -> float:
		return getMethodReturn
	@VideoBandwidth.setter
	@SetProperty(float, VIDEO_BANDWIDTH_COMMAND, rounding=lambda x: round(x, 0), booleanStatePropertyName='__autoVideoBandwidth__', offStateValue=None)
	def VideoBandwidth(self, value:float) -> float:
		pass

	AUTO_VIDEO_BANDWIDTH_RATIO_COMMAND:str = 'SENS:BWID:VID:RAT:AUTO'
	@property
	@GetProperty(bool, AUTO_VIDEO_BANDWIDTH_RATIO_COMMAND)
	def __autoVideoBandwidthRatio__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__autoVideoBandwidthRatio__.setter
	@SetProperty(bool, AUTO_VIDEO_BANDWIDTH_RATIO_COMMAND)
	def __autoVideoBandwidthRatio__(self, value:bool) -> bool:
		pass
	VIDEO_BANDWIDTH_RATIO_COMMAND:str = 'SENS:BWID:VID:RAT'
	@property
	@GetProperty(float, VIDEO_BANDWIDTH_RATIO_COMMAND, booleanStatePropertyName='__autoVideoBandwidthRatio__', offStateValue=None)
	def VideoBandwidthRatio(self, getMethodReturn) -> float:
		return getMethodReturn
	@VideoBandwidthRatio.setter
	@SetProperty(float, VIDEO_BANDWIDTH_RATIO_COMMAND, rounding=lambda x: round(x, 5), booleanStatePropertyName='__autoVideoBandwidthRatio__', offStateValue=None)
	def VideoBandwidthRatio(self, value:float) -> float:
		pass

	# TODO: Add ratio to span and filter types

	CENTER_FREQUENCY_COMMAND:str = 'SENS:FREQ:CENT'
	@property
	@GetProperty(float, CENTER_FREQUENCY_COMMAND)
	def CenterFrequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@CenterFrequency.setter
	@SetProperty(float, CENTER_FREQUENCY_COMMAND)
	def CenterFrequency(self, value:float) -> float:
		pass

	SPAN_COMMAND:str = 'SENS:FREQ:SPAN'
	@property
	@GetProperty(float, SPAN_COMMAND)
	def Span(self, getMethodReturn) -> float:
		return getMethodReturn
	@Span.setter
	@SetProperty(float, SPAN_COMMAND)
	def Span(self, value:float) -> float:
		pass

	FULL_SPAN_COMMAND:str = 'SENS:FREQ:SPAN:FULL'
	def FullSpan(self):
		self.Write(SpectrumAnalyse.FULL_SPAN_COMMAND)

	START_FREQUENCY_COMMAND:str = 'SENS:FREQ:STAR'
	@property
	@GetProperty(float, START_FREQUENCY_COMMAND)
	def StartFrequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@StartFrequency.setter
	@SetProperty(float, START_FREQUENCY_COMMAND)
	def StartFrequency(self, value:float) -> float:
		pass

	STOP_FREQUENCY_COMMAND:str = 'SENS:FREQ:STOP'
	@property
	@GetProperty(float, STOP_FREQUENCY_COMMAND)
	def StopFrequency(self, getMethodReturn) -> float:
		return getMethodReturn
	@StopFrequency.setter
	@SetProperty(float, STOP_FREQUENCY_COMMAND)
	def StopFrequency(self, value:float) -> float:
		pass
	
	CONTINUOUS_SWEEP_COMMAND:str = 'INIT:CONT'
	@property
	@GetProperty(bool, CONTINUOUS_SWEEP_COMMAND)
	def IsAcquisitionRunning(self, getMethodReturn) -> bool:
		return getMethodReturn
	@IsAcquisitionRunning.setter
	@SetProperty(bool, CONTINUOUS_SWEEP_COMMAND)
	def IsAcquisitionRunning(self, value:bool) -> bool:
		pass
	
	AVERAGE_NUMBER_COMMAND:str = 'SENS:AVER:COUN'
	@property
	@GetProperty(int, AVERAGE_NUMBER_COMMAND)
	def AverageNumber(self, getMethodReturn) -> float:
		return getMethodReturn
	@AverageNumber.setter
	@SetProperty(int, AVERAGE_NUMBER_COMMAND)
	def AverageNumber(self, value:int) -> int:
		pass

	AUTO_AVERAGE_TYPE_COMMAND:str = 'SENS:AVER:TYPE:AUTO'
	@property
	@GetProperty(bool, AUTO_AVERAGE_TYPE_COMMAND)
	def __autoAverageType__(self, getMethodReturn) -> bool:
		return getMethodReturn
	@__autoAverageType__.setter
	@SetProperty(bool, AUTO_AVERAGE_TYPE_COMMAND)
	def __autoAverageType__(self, value:bool) -> bool:
		pass
	AVERAGE_TYPE_COMMAND:str = 'SENS:AVER:TYPE'
	@property
	@GetProperty(Average, AVERAGE_TYPE_COMMAND, booleanStatePropertyName='__autoAverageType__', offStateValue=None)
	def AverageType(self, getMethodReturn) -> Average:
		return getMethodReturn
	@AverageType.setter
	@SetProperty(Average, AVERAGE_TYPE_COMMAND, booleanStatePropertyName='__autoAverageType__', offStateValue=None)
	def AverageType(self, value:Average) -> Average:
		pass

	GET_SPECTRUM_COMMAND:str = 'FETC:SAN'
	def GetSpectrum(self) -> dict[float, float]:
		dataFormatSavedState = self.__parent__.__dataFormat__
		self.__parent__.__dataFormat__ = DataFormat.ASCII
		data = self.Query(SpectrumAnalyse.GET_SPECTRUM_COMMAND)
		data = data.split(',')
		data = dict(zip(data[::2], data[1::2]))
		self.__parent__.__dataFormat__ = dataFormatSavedState
		return data
	
	MARKER_X_POSITION_COMMAND_FORMAT:str = 'CALC:MARK{markerIndex}:X'
	@property
	def MarkerFrequency(self, markerIndex:int=None) -> float:
		value = self.Query(SpectrumAnalyse.MARKER_X_POSITION_COMMAND_FORMAT.format(markerIndex = markerIndex if markerIndex else ''))
		return float(value)
	MARKER_Y_POSITION_COMMAND_FORMAT:str = 'CALC:MARK{markerIndex}:Y'
	@property
	def MarkerAmplitude(self, markerIndex:int=None) -> float:
		value = self.Query(SpectrumAnalyse.MARKER_Y_POSITION_COMMAND_FORMAT.format(markerIndex = markerIndex if markerIndex else ''))
		return float(value)
	@property
	def MarkerPosition(self, markerIndex:int=None) -> list[float, float]:
		return [self.MarkerFrequency, self.MarkerAmplitude] # TODO: Add support for other markers
	
	MAX_PEAK_SEARCH_COMMAND_FORMAT:str = 'CALC:MARK{markerIndex}:MAX'
	@property
	def MaxPeakSearch(self, markerIndex:int=None) -> list[float, float]:
		self.Write(SpectrumAnalyse.MAX_PEAK_SEARCH_COMMAND_FORMAT.format(markerIndex = markerIndex if markerIndex else ''))
		return self.MarkerPosition
	
	CONTINUOUS_PEAK_SEARCH_COMMAND:str = 'CALC:MARK{markerIndex}:CPS'
	@property
	def ContinuousPeakSearch(self, markerIndex:int=None) -> bool:
		value = self.Query(SpectrumAnalyse.CONTINUOUS_PEAK_SEARCH_COMMAND.format(markerIndex = markerIndex if markerIndex else ''))
		return bool(int(value))
	@ContinuousPeakSearch.setter
	def SetContinuousPeakSearch(self, value:bool, markerIndex:int=None) -> bool:
		value = bool(value)
		self.Write(SpectrumAnalyse.CONTINUOUS_PEAK_SEARCH_COMMAND.format(markerIndex = markerIndex if markerIndex else ''), str(int(value)))
		if self.ContinuousPeakSearch != value:
			raise Exception('Error while setting continuous peak search')
		return value

	__viewRegistry__:SpectrumAnalyseView = None
	@property
	def View(self) -> SpectrumAnalyseView:
		savedFocusedAnalysingWindowName:str = self.__parent__.FocusedAnalysingWindowName
		self.__parent__.FocusedAnalysingWindowName = self.Name
		viewName = self.Query(SpectrumAnalyseView.VIEW_COMMAND)
		if viewName != (self.__viewRegistry__.VIEW_NAME if self.__viewRegistry__ != None else None): # Incoming update
			self.__viewRegistry__ = VIEW_NAMES[viewName]
		self.__parent__.FocusedAnalysingWindowName = savedFocusedAnalysingWindowName
		return self.__viewRegistry__
	@View.setter
	def View(self, value:SpectrumAnalyseView) -> SpectrumAnalyseView:
		if not (value is SpectrumAnalyseView):
			raise TypeError()
		return self.__viewRegistry__

VIEW_NAMES = dict([(subclass.VIEW_NAME, subclass) for subclass in RECURSIVE_SUBCLASSES(SpectrumAnalyseView)])
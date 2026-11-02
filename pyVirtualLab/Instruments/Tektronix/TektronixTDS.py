import pyVirtualLab.Instruments.Oscilloscope as base

class Channel(base.Channel):
	TYPE_COMMAND_HEADER:str = 'CH'

	@property
	def Unit(self) -> str:
		return self.Query("YUN")

	STATE_COMMAND_FORMAT:str = 'SEL:{0}'
	@property
	def IsEnabled(self) -> bool:
		return bool(int(self.__parent__.Query(self.STATE_COMMAND_FORMAT.format(self.__commandAddress__))))
	@IsEnabled.setter
	def IsEnabled(self, value:bool) -> bool:
		value = bool(value)
		self.__parent__.Write(self.STATE_COMMAND_FORMAT.format(self.__commandAddress__), str(int(value)))
		if self.IsEnabled != value:
			raise Exception(f"Failed to set channel {self.__commandAddress__} state to {value}. Current state: {self.IsEnabled}")
		return self.IsEnabled
	
	OFFSET_COMMAND:str = 'POS'
	@property
	def Offset(self) -> float:
		return float(self.Query(self.OFFSET_COMMAND)) * self.Scale
	@Offset.setter
	def Offset(self, value:float) -> float:
		value = float(value)
		value = value/self.Scale
		self.Write(self.OFFSET_COMMAND, str(value))
		if self.Offset != value:
			raise Exception(f"Failed to set channel {self.__commandAddress__} offset to {value}. Current offset: {self.Offset}")
		return value

	def GetWaveform(self):
		self.__parent__.Write(f"DAT:ENC RIB") # Binary format with LSB and signed values
		self.__parent__.Write(f"DAT:SOU {self.__commandAddress__}")
		data = self.__parent__.__resource__.query_binary_values("CURV?", datatype='h', is_big_endian=True)
		yIncrement = float(self.__parent__.Query("WFMP:YMU"))
		yOffset = float(self.__parent__.Query("WFMP:YOF"))
		yZero = float(self.__parent__.Query("WFMP:YZE"))
		xIncrement = float(self.__parent__.Query("WFMP:XIN"))
		xOrigin = float(self.__parent__.Query("WFMP:XZE"))
		data = [(yIncrement * (float(result) - yOffset)) + yZero for result in data]
		abscissae = range(0, len(data))
		abscissae = [xIncrement * float(abscissa) + xOrigin for abscissa in abscissae]
		data = dict(zip(abscissae, data))
		return data

from matplotlib.pyplot import figure, savefig
from matplotlib.patches import Arrow
from io import BytesIO
from numpy import arange
class TektronixTDS(base.Oscilloscope):
	DELAY_COMMAND:str = 'HOR:POS'
	TIMESCALE_COMMAND:str = 'HOR:SCA'
	
	def __init__(self, address):
		super(TektronixTDS, self).__init__(address)

	def GetScreenshot(self) -> BytesIO:
		fig = figure()
		mainAxis = fig.add_subplot(111)

		minTimeValue = self.MinTimeValue
		maxTimeValue = self.MaxTimeValue
		mainAxis.set_xlim(xmin=minTimeValue, xmax=maxTimeValue)
		mainAxis.set_ylim(ymin=-1, ymax=+1)
		mainAxis.set_yticks(arange(-1, +1, 1/4))
		mainAxis.grid(visible=True, axis='both', color='lightgray', linestyle='--', linewidth=0.5)
		mainAxis.set_xticks(arange(minTimeValue, maxTimeValue, self.TimeRange/10))
		mainAxis.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labeltop=False, labelleft=False, labelright=False)
		mainAxis.scatter(x=[], y=[], label=f"{self.TimeScale} s/div.")
		mainAxis.add_patch(Arrow(x=0, dx=0, y=+1, dy=-1/16, width=(maxTimeValue-minTimeValue)/20, color='black'))

		for channel in self.Channels.values():
			if channel.IsEnabled:
				ax = mainAxis.twinx()
				waveform = channel.GetWaveform()
				x = waveform.keys()
				xmax = max(x)
				xmin = min(x)
				y = waveform.values()
				ymax = max(y)
				ymin = min(y)
				ax.set_ylim(ymin=ymin, ymax=ymax)
				ax.scatter(x=waveform.keys(), y=waveform.values(),
						label=f"{channel.__commandAddress__} {channel.Scale} {channel.Unit}/div.")
				
				ax.add_patch(Arrow(x=xmin, dx=(xmax-xmin)/40, y=0, dy=0, width=(ymax-ymin)/20, edgecolor='black'))
				ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labeltop=False, labelleft=False, labelright=False)
		
		legends = fig.legend(loc='lower center', ncols=5)
		legends.legend_handles[0].set_alpha(0)
		imageBytes = BytesIO()
		savefig(imageBytes)
		return imageBytes

	TIMESCALE_COMMAND:str = 'HOR:MAI:SCA'
	DELAY_COMMAND:str = 'HOR:MAI:POS'
	CHANNEL_TYPE = Channel
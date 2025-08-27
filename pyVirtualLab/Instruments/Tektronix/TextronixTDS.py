from pyVirtualLab.VISAInstrument import Instrument

class TektronixTDS(Instrument):
	def __init__(self, address):
		super(TektronixTDS, self).__init__(address)
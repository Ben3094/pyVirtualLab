from pyVirtualLab.Instruments.RohdeAndSchwarz.RTB2XXX import RTB2XXX

oscillo = RTB2XXX("TCPIP0::10.38.21.208::inst0::INSTR")
oscillo.Connect()
oscillo.Measurements
oscillo.Resource.last_status
oscillo.Format
oscillo.AnalogChannels[1].GetWaveform()

oscillo.Average
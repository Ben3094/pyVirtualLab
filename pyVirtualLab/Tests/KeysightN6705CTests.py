from pyVirtualLab.Instruments.KeysightN6705C.KeysightN6705C import KeysightN6705C
from pyVirtualLab.Instruments.KeysightN6705C.Triggers import ExtTrigger

source = KeysightN6705C('USB::0x2a8d::0xf02::MY56007654::INSTR')
source.Connect()

source1 = source.Outputs[4]
source1.Voltage = 2.5
source1.Current = 2.5
source1.NegativeLimit = -2.4
print(source1.Trigger)
source1.Trigger = ExtTrigger(source1)
print(source1.Trigger)
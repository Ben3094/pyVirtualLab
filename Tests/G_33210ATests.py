from pyVirtualLab.Instruments.Keysight.G_33210A import G_33210A
from pyVirtualLab.Instruments.Keysight.G_33210A.Functions import SineFunction, SquareFunction, RampFunction, PulseFunction, NoiseFunction, DCFunction
from pyVirtualLab.Instruments.Keysight.G_33210A.Modulations import AmplitudeModulation, Function, FrequencyModulation, PulseWidthModulation, FrequencySweepModulation, BurstModulation
from pyVirtualLab.Instruments.Keysight.G_33210A.Modulations import MODULATIONS_NAMES
from numpy import arange

gene = G_33210A("TCPIP0::169.254.2.20::inst0::INSTR")
gene.Connect()
gene.Frequency = 5e6
gene.Amplitude = 5
gene.Offset = 1
gene.Load = 51

function:SquareFunction = SquareFunction()
gene.Function = function
function.DutyCycle = 40

function:RampFunction = RampFunction()
gene.Function = function
function.Symmetry = 30

function:NoiseFunction = NoiseFunction()
gene.Function = function

function:DCFunction = DCFunction()
gene.Function = function

function:SineFunction = SineFunction()
gene.Function = function

modulation:AmplitudeModulation = AmplitudeModulation()
gene.Modulation = modulation
modulation.IsSourceExternal = True
modulation.Depth = 99
modulation.IsSourceExternal = False
modulation.InternalFrequency = 500
modulation.InternalFunction = Function.Triangle

modulation:FrequencyModulation = FrequencyModulation()
gene.Modulation = modulation
modulation.IsSourceExternal = True
modulation.Deviation = 1
modulation.IsSourceExternal = False
modulation.InternalFrequency = 100
modulation.InternalFunction = Function.Sinusoid

modulation:FrequencySweepModulation = FrequencySweepModulation()
gene.Modulation = modulation
modulation.IsSpacingLinear = False
modulation.IsSynced = False
modulation.SyncFrequency = 100
modulation.IsOutputTriggerEnabled = True
modulation.IsOutputTriggerSlopeNegative = True

function:PulseFunction = PulseFunction()
gene.Function = function
function.Period = 0.5
function.IsWidtHoldWithPeriod = True
function.Width = 0.2
function.DutyCycle = 0.1
function.EdgeTime = 80e-9

modulation:PulseWidthModulation = PulseWidthModulation()
gene.Modulation = modulation
modulation.IsSourceExternal = True
modulation.Deviation = 50e-6
modulation.IsSourceExternal = False
modulation.InternalFrequency = 20
# modulation.DutyCycle = 20

startFrequency = 10e3
stopFrequency = 10e6
frequencyStep = 10e3
amplitude = 10
function:SineFunction = SineFunction()
gene.Function = function
gene.Frequency = startFrequency
gene.Amplitude = amplitude
gene.Offset = 0
gene.Load = 50
for frequency in arange(startFrequency, stopFrequency, frequencyStep):
    gene.Frequency = frequency
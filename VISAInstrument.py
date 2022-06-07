import pyvisa

class VISAInstrument:
    def __init__(self, address):
        self._rm = pyvisa.ResourceManager('@py')
        self._instr = self._rm.open_resource(address)
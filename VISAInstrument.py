import pyvisa

class VISAInstrument:
    def __init__(self, address):
        self._rm = pyvisa.ResourceManager('@py')
        self._instr = self._rm.open_resource(address)

    def Write(self, command, args=None):
        return self._instr.write(command + ((' ' + args) if args is not None else ''))

    def Query(self, command, args=''):
        return str(self._instr.query(command + '?' + args)).strip('\n').strip('\r').lstrip(':').removeprefix(command).strip()

    def Read(self):
        return str(self._instr.read()).strip('\n')

    def Id(self):
        return self._instr.query('*IDN?')

    def SelfTest(self):
        if not bool(int(self._instr.query('*TST?'))):
            raise Exception('Error in the self test')
    
    def Reset(self):
        self._instr.write('*RST')

class Source(VISAInstrument):
    def _abort(self):
        self.Reset()

    def __init__(self, address):
        VISAInstrument.__init__(self, address)
        self.Abort = self._abort
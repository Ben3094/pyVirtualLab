import pyvisa
import inspect

class VISAInstrument:
    def __init__(self, address):
        self._rm = pyvisa.ResourceManager('@py')
        self._address = address
        self._isConnected = False

    @property
    def Address(self) -> str:
        return self._address
    @Address.setter
    def Address(self, value):
        if value != self.Address:
            self._address = value
            if self.IsConnected:
                self.Disconnect()
                self.Connect()

    @property
    def IsConnected(self) -> bool:
        return self._isConnected
        
    def Connect(self):
        self._isConnected = True
        try:
            self._instr = self._rm.open_resource(self.Address)
            self.Id
        except Exception as e:
            self._isConnected = False
            raise e

    def Disconnect(self):
        self._instr.close()
        self._isConnected = False
            
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

    def __repr__(self) -> str:
        result = ''
        for name, value in inspect.getmembers(self):
            result += f"{name}:{value}\n"
        return result

class Source(VISAInstrument):
    def _abort(self):
        self.Reset()

    def __init__(self, address):
        VISAInstrument.__init__(self, address)
        self.Abort = self._abort
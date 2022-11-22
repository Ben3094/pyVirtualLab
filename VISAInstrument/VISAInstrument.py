import pyvisa

class Instrument:
    DEFAULT_VISA_TIMEOUT = 2000

    def __init__(self, address, visaTimeout=DEFAULT_VISA_TIMEOUT):
        self.__rm__ = pyvisa.ResourceManager('@py')
        self.__address__ = address
        self.__isConnected__ = False
        self.__visaTimeout__ = visaTimeout

    @property
    def Address(self) -> str:
        return self.__address__
    @Address.setter
    def Address(self, value) -> str:
        if value != self.Address:
            self.__address__ = str(value)
            if self.IsConnected:
                self.Disconnect()
                self.Connect()
        return self.__address__

    @property
    def VISATimeout(self) -> int:
        return self.__visaTimeout__
    @VISATimeout.setter
    def VISATimeout(self, value):
        if value != self.__visaTimeout__:
            self.__visaTimeout__ = int(value)
            if self.IsConnected:
                self.Disconnect()
                self.Connect()

    @property
    def IsConnected(self) -> bool:
        return self.__isConnected__
        
    def Connect(self):
        self.__isConnected__ = True
        try:
            self.__instr__ = self.__rm__.open_resource(self.Address)
            self.__instr__.timeout = self.VISATimeout
            self.Id
        except Exception as e:
            self.__isConnected__ = False
            raise e

    def Disconnect(self):
        self.__instr__.close()
        self.__isConnected__ = False
            
    def Write(self, command, args=None):
        if self.IsConnected:
            return self.__instr__.write(command + ((' ' + args) if args is not None else ''))
        else:
            raise Exception("The instrument is not connected")

    def Query(self, command, args=''):
        if self.IsConnected:
            return str(self.__instr__.query(command + '? ' + args)).strip('\n').strip('\r').strip('"').lstrip(':').removeprefix(command).strip()
        else:
            raise Exception("The instrument is not connected")

    def Read(self):
        if self.IsConnected:
            return str(self.__instr__.read()).strip('\n')
        else:
            raise Exception("The instrument is not connected")

    def Id(self):
        if self.IsConnected:
            return self.__instr__.query('*IDN?')
        else:
            raise Exception("The instrument is not connected")

    def SelfTest(self):
        if self.IsConnected:
            if not bool(int(self.__instr__.query('*TST?'))):
                raise Exception('Error in the self test')
        else:
            raise Exception("The instrument is not connected")
    
    def Reset(self):
        if self.IsConnected:
            self.__instr__.write('*RST')
        else:
            raise Exception("The instrument is not connected")

class Source(Instrument):
    def _abort(self):
        self.Reset()

    def __init__(self, address, visaTimeout=Instrument.DEFAULT_VISA_TIMEOUT):
        Instrument.__init__(self, address, visaTimeout)
        self.Abort = self._abort
import sys
import arduino
import logging
import logging.config
import utils

logging.config.fileConfig('log.cfg', disable_existing_loggers=False)
log = logging.getLogger('wrapper')

class Wrapper:
    def __init__(self, arduino):
        log.info('init()')
        self._arduino = arduino

    def setProgramSize(self, newSize):
        """
        Zwraca 0 w przypadku sukcesu
        """
        log.info('setProgramSize(newSize=%s)' % newSize)
        ar = self._arduino
        ar.sendCommand('sps')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 1

        ar.sendCommand('%s' % newSize)
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 2

        return 0

    def getProgramSize(self):
        """
        Zwraca krotke (status, liczba_bajtow)
        status=0 oznacza sukces
        liczba_bajtow jest ustawiana tylko gdy sukces=0
        """

        log.info('getProgramSize()')
        ar = self._arduino

        ar.sendCommand('gps')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return (1, None)

        (code, desc) = ar.readResponse()

        if code == 0:
            programSize = int(desc)
            log.info('programSize=%d' % programSize)
            return (0, programSize)
        else:
            log.info('code=%s, desc=%s' % (code, desc))
            return (2, None)

    def setMemoryFragment(self, offset, data):
        log.info('setMemoryFragment(offset=%s)' % offset)
        log.debug('data=%s' % data)
        ar = self._arduino

        ar.sendCommand('smf')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 1

        ar.sendCommand('%d' % offset)
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 2

        ar.sendCommand('%d' % len(data))
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 3

        for textByte in utils.textNibblesToTextBytesIterator(utils.dataToTextNibblesIterator(data)):
            ar.sendText(textByte)

        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 4

        return 0

    def dumpProgram(self):
        """
        Odczytuje program z pamieci arduino
        Zwraca krotke (status, [lista_bajtow])
        """

        log.info('dumpProgram()')
        ar = self._arduino

        ar.sendCommand('dp')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return (1, None)

        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return (2, None)

        programSize = int(desc)

        line = ar.readLine()
        log.info('programSize=%d, len(line)=%d' % (programSize, len(line)))

        if len(line) != programSize * 2:
            return (3, None)

        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return (4, None)

        data = []
        for byte in utils.nibbleTextToValueIterator(utils.textIterator(line)):
            data.append(byte)

        return (0, data)

    def readSignature(self):
        """
        Odczytuje sygnature i zwraca ja jako tablice dwoch bajtow
        Pierwszy bajt to producent (manufacturer), drugi bajt to model
        Atmel = 0x1e (manufacturer)     0x1e = 0001 1110
        89c2051 = 0x21 (model)          0x21 = 0010 0001
        """
        log.info('readSignature()')
        ar = self._arduino

        ar.sendCommand('rs')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return (1, None)

        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return (2, None)

        assert len(desc) == 4

        signature = list(utils.nibbleTextToValueIterator(utils.textIterator(desc)))
        return (code, signature)

    def readProgram(self):
        """
        Kopiuje program z pamieci uC do pamieci arduino
        """

        log.info('readProgram()')
        ar = self._arduino

        ar.sendCommand('rp')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 1

        return 0

    def write(self):
        """
        Zapisuje program do uC
        """
        log.info('write()')
        ar = self._arduino

        ar.sendCommand('w')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 1

        return 0

    def erase(self):
        log.info('erase()')
        ar = self._arduino

        ar.sendCommand('er')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 1

        return 0

    #komendy testowe
    def testSetPort(self, port, value):
        """
            port            port                possible balues
            (func param)    (arduino board)

            0 = Vcc         port=1              value: 0 or 1
            1 = Vpp         port=2, 3           value: 0 [0V], 1 [5V] or 2 [12V]
            2 = Prog        port=4              value: 0 or 1
            3 = P33         port=5              value: 0 or 1
            4 = P34         port=6              value: 0 or 1
            5 = P35         port=7              value: 0 or 1
            6 = P37         port=8              value: 0 or 1
            7 = Data        port=[9; 16]        value: [0x00; 0xff]
        """
        log.info('testSetPort(port=%s, value=%s)' % (port, value))
        ar = self._arduino

        ar.sendCommand('tsp')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 1

        ar.sendCommand('%d' % value)
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 2

        ar.sendCommand('%d' % port)
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 3

        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 4

        return 0

    def testResetPorts(self):
        log.info('testResetPorts()')
        ar = self._arduino

        ar.sendCommand('trp')
        (code, desc) = ar.readResponse()

        if code != 0:
            log.info('code=%s, desc=%s' % (code, desc))
            return 1

        return code

def main():
    return 0

if __name__ == "__main__":
    sys.exit(main())
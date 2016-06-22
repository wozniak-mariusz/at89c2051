import sys
import logging
import logging.config
import argparse
import arduino
import wrapper
import os
import utils

logging.config.fileConfig('log.cfg', disable_existing_loggers=False)
log = logging.getLogger('at89c2051')

MAX_PROGRAM_SIZE = 1024 * 2

def debugGetSizeCmd(args=None, arduino=None):
    log.debug('args=%s' % args)
    (status, size) = arduino.getProgramSize()

    if status == 0:
        print size
        return 0
    else:
        log.error('status=%d' % status)
        return status

def debugSetSizeCmd(args=None, arduino=None):
    log.debug('args=%s' % args)
    status = arduino.setProgramSize(int(args.size))

    if status == 0:
        return 0
    else:
        log.error('status=%d' % status)
        return status

def debugGetSignatureCmd(args, arduino):
    log.debug('args=%s' % args)
    (status, signature) = arduino.readSignature()

    if status == 0:
        print utils.listToSeparatedText((hex(s) for s in signature), '\n')
        return 0
    else:
        log.error('status=%d' % status)
        return status

def debugEraseCmd(args, arduino):
    log.debug('args=%s' % args)
    arduino.erase()
    return 0

def isSignatureValid(arduino):
    (status, signature) = arduino.readSignature()

    if status != 0:
        log.error('status=%d' % status)
        return False

    if len(signature) != 2:
        log.error('wrong length of signature; expected 2 bytes, got %d byte(s); signature=%s wrong length' % (len(signature), signature))
        return False

    if signature[0] != 0x1e:
        log.error('expected uC manufacturer 0x1e (Atmel), got %s' % hex(signature[0]))
        return False

    if signature[1] != 0x21:
        log.error('expected uC model 0x21 (AT89C2051), got %s' % hex(signature[0]))
        return False

    return True

def downloadCmd(args, arduino):
    file = args.out

    try:
        return downloadCmdImpl(args, arduino)
    finally:
        file.close()

def downloadCmdImpl(args, arduino):
    log.debug('args=%s' % args)

    if isSignatureValid(arduino) == False:
        log.error('signature not valid')
        return 1

    status = arduino.readProgram()
    if status != 0:
        log.error('reading program from uC failed with status=%d' % status)
        return 2

    (status, program) = arduino.dumpProgram()
    if status != 0:
        log.error('dumping program from uC failed with status=%d' % status)
        return 3

    text = utils.listToSeparatedText(utils.dataToTextNibblesIterator(program), separator='')
    file = args.out
    file.write(text)

    return 0

def uploadCmd(args, arduino):
    file = args.input

    try:
        return uploadCmdImpl(args, arduino)
    finally:
        file.close()

def uploadCmdImpl(args, arduino):
    log.debug('args=%s' % args)
    file = args.input

    program = []

    try:
        it = utils.nibbleTextToValueIterator(utils.textIterator(file.read()))
        program = [i for i in it]
    except Exception, e:
        log.error('error when reading input file: %s' % e)
        return 1

    if len(program) == 0:
        log.error('program to short')
        return 2

    if len(program) > MAX_PROGRAM_SIZE:
        log.error('program longer then %d' % MAX_PROGRAM_SIZE)
        return 3

    atLeastOneByteToWrite = False
    for i in program:
        if i != 0xff:
            atLeastOneByteToWrite = True
            break

    if atLeastOneByteToWrite == False:
        log.error('no useful data in input program')
        return 4

    if isSignatureValid(arduino) == False:
        log.error('signature not valid')
        return 5

    if arduino.erase() != 0:
        log.error('cannot erase program')
        return 6

    if arduino.setProgramSize(len(program)) != 0:
        log.error('cannot set program size to %d' % len(program))
        return 7

    if arduino.setMemoryFragment(0, program) != 0:
        log.error('cannot copy program to arduino')
        return 8

    if arduino.write() != 0:
        log.error('cannot write program to uC')
        return 9
        
    if args.no_verify == False:
        if arduino.readProgram() != 0:
            log.error('verification failed: cannot read program')
            return 10
            
        (result, data) = arduino.dumpProgram()
        if result != 0:
            log.error('verification failed: cannot dump program')
            return 11
            
        if len(program) != len(data):
            log.error('verification failed: program size differs after uploading')
            return 12
            
        for (a,b) in itertools.izip(program, data):
            if a != b:
                log.error('verification failed: program content differs after uploading')
                return 13

    return 0

class ListOfValues:
    def __init__(self, mapping):
        """
        mapping - slownik z mapowaniem:
            wartosc_ustawiana_prze_uzytkownika -> wartosc_wysylana_do_arduino
        """
        self._mapping = mapping

    def translate(self, value):
        return self._mapping.get(value, None)

    def getValidValuesDesc(self):
        return utils.listToSeparatedText(self._mapping.keys(), separator=' or ')

class RangeOfValues:
    def __init__(self, min, max):
        self._min = min
        self._max = max

    def translate(self, value):
        if value >= self._min and value <= self._max:
            return value
        else:
            return None

    def getValidValuesDesc(self):
        return 'Range [%d, %d]' % (self._min, self._max)

"""
Pod kluczem range musi sie znajdowac obiekt ktory jest w stanie stwierdzic czy mozna dana wartosc
przypisac do portu czy nie. Obiekt bedacy tam musi miec przynajmiej dwie metody:
    translate(value) - tlumaczy wartosc podana przez uzytkownika na wartosc ktora bedzie wyslana
        przy pomocy komendy 'testSetPortCmd', jezeli nie da sie przetlumaczyc zwraca None

    getValidValuesDesc() - zwraca string (opis) ktory moze byc wyswietlony zeby poinformowac uzytkownika
        o wartosciach jaki dany pin moze przyjac
"""
pinDescMapping = {
    0: { 'desc':'Vcc',        'range':ListOfValues({0:0, 5:1}) },
    1: { 'desc':'Vpp/Rst',    'range':ListOfValues({0:0, 5:1, 12:2}) },
    2: { 'desc':'P3.2/~Prog', 'range':ListOfValues({0:0, 5:1}) },
    3: { 'desc':'P3.3',       'range':ListOfValues({0:0, 5:1}) },
    4: { 'desc':'P3.4',       'range':ListOfValues({0:0, 5:1}) },
    5: { 'desc':'P3.5',       'range':ListOfValues({0:0, 5:1}) },
    6: { 'desc':'P3.7',       'range':ListOfValues({0:0, 5:1}) },
    7: { 'desc':'P1/Data',    'range':RangeOfValues(0x00, 0xff) },
    8: { 'desc':'Mode',       'range':RangeOfValues(0, 5) },
}

def debugSetPin(args, arduino):
    log.debug('args=%s' % args)

    pinDesc = pinDescMapping.get(args.pin, None)
    if pinDesc == None:
        log.error('unknown pin %d' % args.pin)
        return 1

    values = pinDesc['range']
    name = pinDesc['desc']
    translatedValue = values.translate(args.value)

    if translatedValue == None:
        log.error('pin %d (%s) do not accept value %d, accepts %s' %
            (args.pin, name, args.value, values.getValidValuesDesc()))
        return 2

    if arduino.testSetPort(args.pin, translatedValue) != 0:
        log.error('Setting pin %d (%s) to %d failed' % (args.pin, name, translatedValue))
        return 3

    log.info('Set %s to %d (%d)' % (name, args.value, translatedValue))
    return 0

def debugResetPins(args, arduino):
    log.debug('args=%s' % args)

    status = arduino.testResetPorts()
    if status != 0:
        log.error('Resetting pins failed with status %d' % status)
        return 1

    return 0

handlers = {
    'download':downloadCmd,
    'upload':uploadCmd,
    'debug_getsignature':debugGetSignatureCmd,
    'debug_getsize':debugGetSizeCmd,
    'debug_setsize':debugSetSizeCmd,
    'debug_erase':debugEraseCmd,
    'debug_setpin':debugSetPin,
    'debug_resetpins':debugResetPins,
}

def main():
    parser = argparse.ArgumentParser()
    subParsers = parser.add_subparsers(help='commands for AT89C2051 programmer (based on Arduino)', dest='cmd')
    parser.add_argument('-p', '--port', help='arduino port', type=str, required=True)

    if os.getenv('AT89C2051_DEBUG', 'no').upper() == 'YES':
        subParsers.add_parser('debug_getsignature', help='read signature from uC')

        subParsers.add_parser('debug_getsize', help='read program size (from arduino cache)')

        setSizeParser = subParsers.add_parser('debug_setsize', help='read program size (from arduino cache)')
        setSizeParser.add_argument('size', help='size of program', type=int)

        subParsers.add_parser('debug_erase', help='erase uC memory')

        setPinParser = subParsers.add_parser('debug_setpin', help='set pin to value')
        setPinParser.add_argument('pin', help='selected pin', type=int)
        setPinParser.add_argument('value', help='value to assign to pin', type=int)

        subParsers.add_parser('debug_resetpins', help='reset all pins')

    downloadCmdParser = subParsers.add_parser('download', help='download program from uC')
    downloadCmdParser.add_argument('out', help='file with output', default='out.txt', type=argparse.FileType('w'))

    uploadCmdParser = subParsers.add_parser('upload', help='upload program to uC')
    uploadCmdParser.add_argument('input', help='file with program to upload', type=file)
    uploadCmdParser.add_argument('-n', '--no-verify', help='skip verification', action='store_true', dest='no_verify', required=False)

    args = parser.parse_args()

    cmdHandler = handlers.get(args.cmd, None)
    if cmdHandler:
        try:
            with arduino.guardedArduino(args.port) as guardedArduino:
                ar = wrapper.Wrapper(guardedArduino)
                return 1 + cmdHandler(args, ar)
        except Exception, e:
            log.error(e)
    else:
        log.error('Command "%s" has no handler' % args.cmd)
        return 1

if __name__ == '__main__':
    sys.exit(main())
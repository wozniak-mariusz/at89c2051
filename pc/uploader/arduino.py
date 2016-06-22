import hex
import sys
import serial
import logging
import logging.config
import utils

logging.config.fileConfig('log.cfg', disable_existing_loggers=False)
log = logging.getLogger('arduino')

class Arduino:
    def __init__(self):
        pass
        
    def connect(self, port):
        log.debug('connect')
        self._port = serial.Serial(port=port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, writeTimeout=None, dsrdtr=False, interCharTimeout=None)
        
    def disconnect(self):
        log.debug('disconnect')
        self._port.close;

    #TODO do skasowania?
    def sendCommand(self, text):
        self.sendText('%s\n' % text)
    
    def sendText(self, text):
        hasNL = text[-1] in ['\n', '\r']
        
        log.debug('PC -> AR: "%s"%s' % (text.strip(), " [NL]" if hasNL else ""))
        self._port.write(text)
        
    def readLine(self):
        return self._readNonEmptyResponse()

    def readResponse(self):
        return self._readResponseAndOptionalText()
        
    def _readNonEmptyResponse(self):
        while True:
            response = self._port.readline().strip()
            if len(response) > 0:
                #print '>> response="%s"' % response
                return response
                
    #czyta odpowiedz od arduino
    #zwraca krotke w postaci (kod, opis)
    #kod to liczba, opis to string (moze byc None)
    def _readResponseAndOptionalText(self):
        response = self._readNonEmptyResponse()
        log.debug('PC <- AR: "%s"' % (response))
        
        #odpowiedz moze sie wygladac na dwa sposoby:
        #   [kod_opowiedzi]
        #   lub
        #   [kod_odpowiedzi]=[opis]
        
        descriptionSeparatorIndex = response.find(':')
        
        if descriptionSeparatorIndex == -1:
            #brak opisu
            return (int(response), None)
        else:
            #jest opis
            code = int(response[0:descriptionSeparatorIndex])
            desc = response[descriptionSeparatorIndex+1:len(response)]
        
            return (code, desc)
        
def guardedArduino(port):
    def onEnter():
        arduino = Arduino()
        arduino.connect(port)
        return arduino
        
    def onExit(arduino, type, value, traceback):
        arduino.disconnect()
        
    return utils.guarded(onEnter, onExit)
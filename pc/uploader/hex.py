#na podstawie
#   https://en.wikipedia.org/wiki/Intel_HEX

class ChecksumException(Exception): pass
class UnknownRecordTypeException(Exception): pass

#tworzy generator znakow ze stringa
def charIterator(text):
    for c in text:
        yield c

#przetwarza nibble w postaci tekstu na odpowiadajaca mu wartosc
def valueFromHexNibble(c):
    assert len(c) == 1
    
    if (ord(c) >= ord('0') and ord(c) <= ord('9')):
        return ord(c) - ord('0')
    elif (c == 'a' or c == 'A'):
        return 0xA
    elif (c == 'b' or c == 'B'):
        return 0xB
    elif (c == 'c' or c == 'C'):
        return 0xC
    elif (c == 'd' or c == 'D'):
        return 0xD
    elif (c == 'e' or c == 'E'):
        return 0xE
    elif (c == 'f' or c == 'F'):
        return 0xF
    
    assert False, 'not a hex character ("%s")' % c
    
#przetwarza tekst skladajacy sie z nibbli na wartosci tych nibbli
def valueFromHexNibbleIterator(text):
    for c in text:
        yield valueFromHexNibble(c)
        
def pairIterator(data):
    first = None
    second = None
    count = 0
    
    for d in data:
        if count == 0:
            first = d
            count += 1
        elif count == 1:
            second = d
            yield (first, second)
            count = 0
            
    assert count == 0
        
#przetwarza kazde dwie wartosci nibble w jedna wartosc oktetu      
def octetValueFromTwoNibleValuesIterator(nibbles):
    for (a, b) in pairIterator(nibbles):
        assert a >= 0
        assert a <= 15
        assert b >= 0
        assert b <= 15
        
        yield (a << 4) + b

class CheckSumCalculator:
    def __init__(self):
        self._sum = 0
        
    def wrapIterator(self, data):
        for d in data:
            self._sum += d
            yield d
            
    def getResult(self):
        return ((self._sum & 0xff) ^ 0xff) + 1
            
def parseRecord(recordAsText):
    charIt = charIterator(recordAsText)
    assert charIt.next() == ':'
    
    checkSumCalculator = CheckSumCalculator()
    octetValueIt = checkSumCalculator.wrapIterator(octetValueFromTwoNibleValuesIterator(valueFromHexNibbleIterator(charIt)))
    
    byteCount = octetValueIt.next() #nbr of bytes in data field
    assert byteCount >= 0
    assert byteCount <= 0xFF
    
    address = (octetValueIt.next() << 8) + octetValueIt.next()
    assert address >= 0
    assert address <= 0xFFFF
    
    recordType = octetValueIt.next()
    if recordType < 0 or recordType > 5:
        raise UnknownRecordTypeException('recordType=%d' % recordType)
    
    #odczyt danych
    data = []
    for v in range(byteCount):
        data.append(octetValueIt.next())
        
    calculatedCheckSum = checkSumCalculator.getResult()
    checkSum = octetValueIt.next()
    
    if checkSum != calculatedCheckSum:
        raise ChecksumException("Expected 0x%x, got 0x%x" % (calculatedCheckSum, checkSum))
  
    return (byteCount, address, recordType, data);
    
def resizeArrayTo(array, size):
    if len(array) < size:
        array.extend([0] * (size - len(array)))
    
def parseRecords(textLines):
    out = []
    eof = False
    
    for line in textLines:
        assert eof == False, 'EOF not expected'
    
        (byteCount, address, recordType, data) = parseRecord(line)
        
        if recordType == 0:
            if byteCount > 0:
                resizeArrayTo(out, address + byteCount)
                out[address:address+byteCount] = data
        elif recordType == 1:
            eof = True
        elif recordType == 2:
            assert False, 'NOT IMPLEMENTED'
        elif recordType == 3:
            assert False, 'NOT IMPLEMENTED'
        elif recordType == 4:
            assert False, 'NOT IMPLEMENTED'
        elif recordType == 5:
            assert False, 'NOT IMPLEMENTED'
        else:
            assert False, "recordType=%d" % recordType
            
    assert eof == True, "last record not EOF"
    return out

def main():
    if len(sys.argv) != 2:
        print 'wrong numer of arguments (one expected)'
        return 1

    data = ''
    with open(sys.argv[1]) as file:
        for byte in parseRecords(file.readlines()):
            data += format(byte, '02x')
    print data

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
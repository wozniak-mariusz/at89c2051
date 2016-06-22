def textIterator(text):
    for c in text:
        yield c

def nibbleValueToText(value):
    assert value >= 0
    assert value <= 0xf

    if (value < 0xa):
        return chr(ord('0') + value)
    else:
        return chr(ord('a') + (value - 10))

def textNibbleToValue(character):
    chNum = ord(character.lower())
    zeroNum = ord('0')
    aNum = ord('a')

    if chNum >= zeroNum and chNum <= ord('9'):
        return chNum - zeroNum
    elif chNum >= aNum and chNum <= ord('f'):
        return chNum - aNum + 10
    else:
        assert False

def dataToTextNibblesIterator(data):
    for d in data:
        assert d >= 0
        assert d <= 0xff

        yield nibbleValueToText(d >> 4)
        yield nibbleValueToText(d & 0x0f)

def nibbleTextToValueIterator(textIt):
    for c in textIt:
        high = textNibbleToValue(c)
        low = textNibbleToValue(textIt.next())

        yield (high << 4) + low

def textNibblesToTextBytesIterator(textIt):
    for a in textIt:
        b = textIt.next()

        yield "%s%s" % (a, b)

def listToSeparatedText(list, separator=', '):
    text = ''

    for s in list:
        text += '%s%s' % (str(s), separator)

    if len(separator) > 0:
        return text[:-len(separator)]
    else:
        return text

#opakowuje dany zasob taki sposob ze mozna go uzyc w bloku with
#resource
#   zasob do opakowania
#onEnter
#   funkcja do wywolania gdy zasob wchodzi w obszar chroniony
#   onEnter musi zwracac zasob ktory ma byc przypisany poprzez 'as'
#onExit
#   funkcja wywolywana podczas wyjscia z bloku chronionego przez with
#   sygnatura:
#       onExit(res, type, value, traceback)
def guarded(onEnter, onExit):
    class Wrapper:
        def __enter__(self):
            self._res = onEnter()
            return self._res

        def __exit__(self, type, value, traceback):
            res = getattr(self, '_res', None)
            if res != None:
                onExit(res, type, value, traceback)

    return Wrapper()
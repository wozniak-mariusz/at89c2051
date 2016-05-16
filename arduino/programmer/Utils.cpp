#include "Utils.h"
#include "Code.h"
#include <Stream.h>

int readLine(Stream&      stream,
             char * const buf,
             const size_t bufSize) {

  int count = 0;
  while (true) {
    while (stream.available() > 0) {
      const int c = stream.read();
      const bool isEol = c == '\n' || c == '\r';
  
      if (count < bufSize) {
        buf[count++] = c;
      }
  
      if (isEol) {
        buf[--count] = 0;
        return count;
      }
    }
  }
}

int readLineAndConvertToInt(Stream&      stream,
                            char* const  buf,
                            const size_t bufSize,
                            bool&        success) {
  success = false;

  const int size = readLine(stream, buf, bufSize);
  
  for (int i=0; i<size; ++i) {
    if (isDecimalDigit(buf[i]) == false) {
      success = false;
      return 0;
    }
  }

  if (size > 0) {
    //TODO mozna uzyc innej funkcji niz strtol ktora w przypadku bledu daje 0
    const int value = strtol(buf, 0, 10);

    success = true;
    return value;
  } else {
    return 0;
  }
}

int readNibbleFrom(Stream& stream) {
  while (stream.available() < 1);
  
  const int c = stream.read();

  if (c >= '0' && c <= '9') {
    return c - '0';
  }
  
  switch (c) {
    case 'a': case 'A': return 0xA;
    case 'b': case 'B': return 0xB;
    case 'c': case 'C': return 0xC;
    case 'd': case 'D': return 0xD;
    case 'e': case 'E': return 0xE;
    case 'f': case 'F': return 0xF;
  }
  
  //blad
  return -1;
}

void sendCodeWithSeparatorButWithoutNewline(Stream&   stream,
                                            const int code) {
  stream.print(code);
  stream.print(":");
}

void sendCode(Stream&            stream,
              const int          code,
              char const * const comment) {
  if (comment) {
    sendCodeWithSeparatorButWithoutNewline(stream, code);
    stream.println(comment);
  } else {
    stream.println(code);
  }
}

void sendCode(Stream&   stream,
              const int code,
              const int commentValue) {
  stream.print(code);
  stream.print(":");
  stream.println(commentValue);
}

bool isDecimalDigit(const char c) {
  return (c >= '0' && c <= '9');
}

int readParamAndSendCodeInCaseOfError(Stream&      stream,
                                      char * const buf,
                                      const int    bufSize,
                                      const int    errorCode,
                                      bool&        success) {
  const int param = readLineAndConvertToInt(stream, buf, bufSize, success);

  if (success) {
    sendCode(stream, Code::OK, buf);
  } else {
    sendCode(stream, errorCode, buf);
  }

  return param;
}

int readByteFrom(Stream& stream) {
  const int highNibble = readNibbleFrom(stream);
  if (highNibble == -1) {
    return -1;
  }

  const int lowNibble = readNibbleFrom(stream);
  if (lowNibble == -1) {
    return -1;
  }

  return (highNibble << 4) + lowNibble;
}

char toTextNibble(unsigned char value) {
  if (value >=0 && value <= 9) {
    return '0' + value;
  } else if (value >= 0xA && value <= 0xF) {
    return 'a' + value - 0xA;
  } else {
    return 0;
  }
}

bool writeByteAsTwoTextNibblesTo(Stream& stream, const int value, const bool addEol) {
  const char highNibble = toTextNibble((value >> 4) & 0xf);
  if (highNibble == 0) {
    return false;
  }

  const char lowNibble = toTextNibble(value & 0xf);
  if (lowNibble == 0) {
    return false;
  }

  stream.write(highNibble);

  stream.write(lowNibble);
  if (addEol) {
    stream.println("");
  }

  return true;
}

VppStatus fromInt(const int value) {
  switch (value) {
    case 0: return VppStatus::VppStatus_0V;
    case 1: return VppStatus::VppStatus_5V;
    default: return VppStatus::VppStatus_12V;
  }
}


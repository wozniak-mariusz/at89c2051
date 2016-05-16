#pragma once

#include <stdlib.h>
#include "VoltageControl.h"

template <class T, size_t N>
size_t arraySize(T (&)[N]) {
  return N;
}

class Stream;

//Reads characters until \r or \n
//Returns nbr of characters saved in buf (without \r or \n at the end
//Last character is always 0 that means max len of text is bufSize-1
int readLine(Stream&      stream,
             char * const buf,
             const size_t bufSize);

int readLineAndConvertToInt(Stream&      stream,
                            char* const  buf,
                            const size_t bufSize,
                            bool&        success);

void sendCodeWithSeparatorButWithoutNewline(Stream&   stream,
                                            const int code);

void sendCode(Stream&            stream,
              const int          code,
              char const * const comment = nullptr);

void sendCode(Stream&   stream,
              const int code,
              const int commentValue);

bool isDecimalDigit(const char c);

int readParamAndSendCodeInCaseOfError(Stream&      stream,
                                      char * const buf,
                                      const int    bufSize,
                                      const int    errorCode,
                                      bool&        success);

int readByteFrom(Stream& stream);

//in case of error returns 0
char toTextNibble(unsigned char value);

//return true on success
bool writeByteAsTwoTextNibblesTo(Stream&    stream,
                                 const int  value,
                                 const bool addEol = false);

VppStatus fromInt(const int value);

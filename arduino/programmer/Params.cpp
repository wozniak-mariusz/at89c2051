#include "Params.h"

Params::Params(const int maxProgramSize)
  : maxProgramSize(maxProgramSize)
  , programSize(0)
{}

int Params::getProgramSize() const {
  return programSize;
}
bool Params::setProgramSize(const int size) {
  if (size >= 0 && size <= maxProgramSize) {
    programSize = size;
    return true;
  } else {
    return false;
  }
}


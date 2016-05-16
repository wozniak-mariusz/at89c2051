#include "Program.h"

Program::Program() {}

void Program::reset() {
  for (auto& c: data) {
    c = 0;
  }
}

#pragma once

class Params {
public:
  Params(const int maxProgramSize);

  int getProgramSize() const;
  bool setProgramSize(const int size);

private:
  Params(const Params&);
  Params& operator=(const Params&);

private:
  const int maxProgramSize;
  int programSize;
};

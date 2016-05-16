#pragma once

struct Program {
public:
  Program();
  void reset();
  
public:
  unsigned char data[1024 * 2];

private:
  Program(const Program&);
  Program& operator=(const Program&);
};

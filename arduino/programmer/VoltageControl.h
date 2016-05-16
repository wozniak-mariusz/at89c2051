#pragma once
#include "arduino.h"

enum class VppStatus {
  VppStatus_0V,
  VppStatus_5V,
  VppStatus_12V,
};

enum class Mode {
  WriteCodeData,
  ReadCodeData,
  WriteLock_Bit1,
  WriteLock_Bit2,
  ChipErase,
  ReadSignatureByte,
};

class VoltageControl {
public:
  VoltageControl();
  void initPorts();
  void setP1AsInput(bool);
  void reset();

  void setVcc(bool);
  void setVpp(VppStatus); //Vpp/Reset
  void setProg(bool);
  void setXtal1(bool);
  void setP33(bool);
  void setP34(bool);
  void setP35(bool);
  void setP37(bool);
  void setData(unsigned char data);
  unsigned char getData();
  bool isReady();
  bool isBusy();  //implemented in terms of isReady
  void setMode(const Mode mode);

private:
  VoltageControl(const VoltageControl&);
  VoltageControl& operator=(const VoltageControl&);
};

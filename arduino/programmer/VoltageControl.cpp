#include "VoltageControl.h"

const int VCC_PORT    = 10;  //Vcc - zasilanie at89
const int VPP_PORT_0  = A5;  //Rst/Vpp - stan wysoki dodaje do Vpp +5V
const int VPP_PORT_1  = 11;  //Rst/Vpp - stan wysoki dodaje do Vpp +7.5V
const int PROG_PORT   = A1;  //PROG (P3.2)
const int XTAL1_PORT  = A0;

const int P33_PORT    = A2;  //MODE 1
const int P34_PORT    = A3;  //MODE 2
const int P35_PORT    = A4;  //MODE 3
const int P37_PORT    = 1;   //MODE 4

const int DATA_PORT_0 = 2;
const int DATA_PORT_1 = 3;
const int DATA_PORT_2 = 4;
const int DATA_PORT_3 = 5;
const int DATA_PORT_4 = 6;
const int DATA_PORT_5 = 7;
const int DATA_PORT_6 = 8;
const int DATA_PORT_7 = 9;

const int RDY_PORT = 0; //RDY/!BSY

volatile int risingReadyPinCount = 0;

void risingReadyPinInterruptHandler(void) {
  ++risingReadyPinCount;
}

VoltageControl::VoltageControl() {
}

void VoltageControl::initPorts() {
  pinMode(VCC_PORT, OUTPUT);
  pinMode(VPP_PORT_0, OUTPUT);
  pinMode(VPP_PORT_1, OUTPUT);
  pinMode(PROG_PORT, OUTPUT);
  pinMode(XTAL1_PORT, OUTPUT);
  pinMode(P33_PORT, OUTPUT);
  pinMode(P34_PORT, OUTPUT);
  pinMode(P35_PORT, OUTPUT);
  pinMode(P37_PORT, OUTPUT);
  setP1AsInput(false);

  pinMode(RDY_PORT, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(RDY_PORT),
                  risingReadyPinInterruptHandler,
                  RISING);
}

void VoltageControl::setP1AsInput(const bool asInput) {
  static const auto input = INPUT_PULLUP;
  static const auto output = OUTPUT;
  
  pinMode(DATA_PORT_0, asInput ? input : output);
  pinMode(DATA_PORT_1, asInput ? input : output);
  pinMode(DATA_PORT_2, asInput ? input : output);
  pinMode(DATA_PORT_3, asInput ? input : output);
  pinMode(DATA_PORT_4, asInput ? input : output);
  pinMode(DATA_PORT_5, asInput ? input : output);
  pinMode(DATA_PORT_6, asInput ? input : output);
  pinMode(DATA_PORT_7, asInput ? input : output);
}

void VoltageControl::reset() {
  setVcc(0);
  setVpp(VppStatus::VppStatus_0V);
  setProg(0);
  setP33(0);
  setP34(0);
  setP35(0);
  setP37(0);
  setXtal1(0);
  setData(0);
  setP1AsInput(true);
}

void VoltageControl::setVcc(const bool flag) {
  digitalWrite(VCC_PORT, flag ? HIGH : LOW);
}

void VoltageControl::setVpp(const VppStatus status) {
  switch (status) {
    case VppStatus::VppStatus_0V:
      digitalWrite(VPP_PORT_0, LOW);
      digitalWrite(VPP_PORT_1, LOW);
      break;

    case VppStatus::VppStatus_5V:
      digitalWrite(VPP_PORT_0, HIGH);
      digitalWrite(VPP_PORT_1, LOW);
      break;

    case VppStatus::VppStatus_12V:
      digitalWrite(VPP_PORT_0, HIGH);
      digitalWrite(VPP_PORT_1, HIGH);
      break;
  }
}

void VoltageControl::setProg(const bool flag) {
  digitalWrite(PROG_PORT, flag ? HIGH : LOW);
}

void VoltageControl::setXtal1(const bool flag) {
  digitalWrite(XTAL1_PORT, flag ? HIGH : LOW);
}

void VoltageControl::setP33(const bool flag) {
    digitalWrite(P33_PORT, flag ? HIGH : LOW);
}

void VoltageControl::setP34(const bool flag) {
  digitalWrite(P34_PORT, flag ? HIGH : LOW);
}

void VoltageControl::setP35(const bool flag) {
  digitalWrite(P35_PORT, flag ? HIGH : LOW);
}

void VoltageControl::setP37(const bool flag) {
  digitalWrite(P37_PORT, flag ? HIGH : LOW);
}

void VoltageControl::setData(unsigned char data) {
  digitalWrite(DATA_PORT_0, ((data & 0x01) == 0) ? LOW : HIGH);
  digitalWrite(DATA_PORT_1, ((data & 0x02) == 0) ? LOW : HIGH);
  digitalWrite(DATA_PORT_2, ((data & 0x04) == 0) ? LOW : HIGH);
  digitalWrite(DATA_PORT_3, ((data & 0x08) == 0) ? LOW : HIGH);

  digitalWrite(DATA_PORT_4, ((data & 0x10) == 0) ? LOW : HIGH);
  digitalWrite(DATA_PORT_5, ((data & 0x20) == 0) ? LOW : HIGH);
  digitalWrite(DATA_PORT_6, ((data & 0x40) == 0) ? LOW : HIGH);
  digitalWrite(DATA_PORT_7, ((data & 0x80) == 0) ? LOW : HIGH);
}

unsigned char VoltageControl::getData() {
  return
    (digitalRead(DATA_PORT_0) << 0) |
    (digitalRead(DATA_PORT_1) << 1) |
    (digitalRead(DATA_PORT_2) << 2) |
    (digitalRead(DATA_PORT_3) << 3) |
    (digitalRead(DATA_PORT_4) << 4) |
    (digitalRead(DATA_PORT_5) << 5) |
    (digitalRead(DATA_PORT_6) << 6) |
    (digitalRead(DATA_PORT_7) << 7);
}

bool VoltageControl::isReady() {
  return digitalRead(RDY_PORT) == HIGH;
}

bool VoltageControl::isBusy() {
  return !isReady();
}

void VoltageControl::setMode(const Mode mode) {
  switch (mode) {
    case (Mode::WriteCodeData):
      setP33(0);
      setP34(1);
      setP35(1);
      setP37(1);
      break;

    case (Mode::ReadCodeData):
      setP33(0);
      setP34(0);
      setP35(1);
      setP37(1);
      break;

    case (Mode::WriteLock_Bit1):
      setP33(1);
      setP34(1);
      setP35(1);
      setP37(1);
      break;

    case (Mode::WriteLock_Bit2):
      setP33(1);
      setP34(1);
      setP35(0);
      setP37(0);
      break;

    case (Mode::ChipErase):
      setP33(1);
      setP34(0);
      setP35(0);
      setP37(0);
      break;

    case (Mode::ReadSignatureByte):
      setP33(0);
      setP34(0);
      setP35(0);
      setP37(0);
      break;
  }
}


#include "Code.h"
#include "Utils.h"
#include "Params.h"
#include "Program.h"
#include "VoltageControl.h"

const int MAX_COMMAND_LENGTH = 10;
struct Program program; //must be global to see memory consumption (compiler warns about low memory when it's consumed in compilation time)

class VoltageControl vc;

void setup() {
  Serial.begin(9600);
  vc.initPorts();
  vc.reset();
}

//====================================================================

using CMD_HANDLER_FUNC = void(*)(Stream&, Params&, Program&);

struct CmdHandler {
  char const* cmd;
  CMD_HANDLER_FUNC func;
};

template <size_t N>
CMD_HANDLER_FUNC getHandlerFor(CmdHandler (&handlers)[N], char const * const cmd) {
  if (handlers == nullptr || cmd == nullptr) {
    return nullptr;
  }

  for (auto& handler: handlers) {
    if (handler.cmd) {
      if (strcmp(handler.cmd, cmd) == 0) {
        return handler.func;
      }
    }
  }

  return nullptr;
}

//====================================================================

//Sets program size
//>[program_size]
//<[status]
void setProgramSizeCmd(Stream& stream, class Params& params, class Program& program) {
  char buf[10];
  
  bool success = false;
  const int programSize = readLineAndConvertToInt(stream, buf, arraySize(buf), success);

  if (!success) {
    sendCode(Serial, Code::ERROR_SPS_CANNOT_CONVERT_PARAM_PROGRAM_SIZE_TO_NUMBER, buf);
    return;
  }

  if (params.setProgramSize(programSize)) {
    program.reset();
    sendCode(Serial, Code::OK, buf);
  } else {
    sendCode(Serial, Code::ERROR_SPS_WRONG_PROGRAM_SIZE, buf);
  }
}

//Returns program size
//<[status]:[program_size_if_status_zero]
void getProgramSizeCmd(Stream& stream, class Params& params, class Program& program) {
  sendCode(Serial, Code::OK, params.getProgramSize());
}

void setMemoryFragmentCmd(Stream& stream, class Params& params, class Program& program) {
  char buf[10];
  bool success = false;

  const int fragmentOffset =
    readParamAndSendCodeInCaseOfError(stream,
                                      buf,
                                      arraySize(buf),
                                      Code::ERROR_SMF_CANNOT_CONVERT_PARAM_FRAGMENT_OFFSET_TO_NUMBER,
                                      success);

  if (!success) {
    return;
  }
  
  if (fragmentOffset < 0 || fragmentOffset >= params.getProgramSize()) {
    sendCode(stream, Code::ERROR_SMF_PARAM_FRAGMENT_OFFSET_WRONG_VALUE);
    return;
  }

  const int fragmentSize =
    readParamAndSendCodeInCaseOfError(stream,
                                      buf,
                                      arraySize(buf),
                                      Code::ERROR_SMF_CANNOT_CONVERT_PARAM_FRAGMENT_SIZE_TO_NUMBER,
                                      success);

  if (!success) {
    return;
  }

  if (fragmentSize < 1 || fragmentOffset + fragmentSize > params.getProgramSize()) {
    sendCode(stream, Code::ERROR_SMF_PARAM_FRAGMENT_SIZE_WRONG_VALUE);
    return;
  }

  for (int i=0; i<fragmentSize; ++i) {
    const int byte = readByteFrom(stream);

    if (byte == -1) {
      sendCode(stream, Code::ERROR_SMF_WRONG_BYTE_VALUE);
      return;
    }

    program.data[fragmentOffset + i] = static_cast<char>(byte);
  }

  sendCode(stream, Code::OK);
}

void dumpProgramCmd(Stream& stream, class Params& params, class Program& program) {
  sendCode(stream, Code::OK, params.getProgramSize());

  if (params.getProgramSize()) {
    for (int i=0; i<params.getProgramSize(); ++i) {
      if (writeByteAsTwoTextNibblesTo(stream, program.data[i]) == false) {
        sendCode(stream, Code::ERROR_DP_WRONG_PROGRAMY_BYTE_VALUE);
        return;
      }
    }
  }

  stream.println();
  sendCode(stream, Code::OK);
}

void testSetPortCmd(Stream& stream, class Params& params, class Program& program) {
  char buf[10];
  bool success = false;
  
  const int status =
    readParamAndSendCodeInCaseOfError(stream,
                                      buf,
                                      arraySize(buf),
                                      Code::ERROR_SP_CANNOT_CONVERT_PARAM_STATUS_TO_NUMBER,
                                      success);

  if (!success) {
    return;
  }

  if (status < 0 || status > 0xff) {
    sendCode(stream, Code::ERROR_SP_PARAM_STATUS_OUT_OF_RANGE);
    return;
  }

  const int port =
    readParamAndSendCodeInCaseOfError(stream,
                                      buf,
                                      arraySize(buf),
                                      Code::ERROR_SP_CANNOT_CONVERT_PARAM_PORT_TO_NUMBER,
                                      success);

  if (!success) {
    return;
  }

  switch (port) {
    case 0:
      vc.setVcc(status > 0);
      break;

    case 1:
      vc.setVpp(fromInt(status));
      break;

    case 2:
      vc.setProg(status > 0);
      break;

    case 3:
      vc.setP33(status > 0);
      break;

    case 4:
      vc.setP34(status > 0);
      break;

    case 5:
      vc.setP35(status > 0);
      break;

    case 6:
      vc.setP37(status > 0);
      break;

    case 7:
      vc.setData(status);
      break;

    case 8:
      switch(status) {
        case 0: vc.setMode(Mode::WriteCodeData); break;
        case 1: vc.setMode(Mode::ReadCodeData); break;
        case 2: vc.setMode(Mode::WriteLock_Bit1); break;
        case 3: vc.setMode(Mode::WriteLock_Bit2); break;
        case 4: vc.setMode(Mode::ChipErase); break;
        default: vc.setMode(Mode::ReadSignatureByte); break;
      };
      break;

    default:
      sendCode(stream, Code::ERROR_SP_UNKNOWN_PORT);
      return;
  }

  sendCode(stream, Code::OK);
}

void testResetPortsCmd(Stream& stream, class Params& params, class Program& program) {
  vc.reset();
}

void readSignatureCmd(Stream& stream, class Params& params, class Program& program) {
  vc.reset();

  vc.setVcc(1);
  vc.setVpp(VppStatus::VppStatus_5V);
  vc.setProg(1);
  vc.setMode(Mode::ReadSignatureByte);
  vc.setP1AsInput(true);

  delayMicroseconds(5);
  const unsigned char manufacturer = vc.getData();

  vc.setXtal1(1);
  delayMicroseconds(1);
  vc.setXtal1(0);

  delayMicroseconds(5);
  const unsigned char model = vc.getData();
  
  vc.reset();

  sendCodeWithSeparatorButWithoutNewline(stream, Code::OK);
  writeByteAsTwoTextNibblesTo(stream, manufacturer);
  writeByteAsTwoTextNibblesTo(stream, model, true);
}

void readProgramCmd(Stream& stream, class Params& params, class Program& program) {
  vc.reset();

  vc.setVcc(1);
  vc.setVpp(VppStatus::VppStatus_5V);
  vc.setProg(1);
  vc.setMode(Mode::ReadCodeData);
  vc.setP1AsInput(true);

  program.reset();
  for (int i=0; i<arraySize(program.data); ++i) {
    delayMicroseconds(5);
    program.data[i] = vc.getData();
  
    vc.setXtal1(1);
    delayMicroseconds(1);
    vc.setXtal1(0);
  }
  
  vc.reset();

  params.setProgramSize(arraySize(program.data));
}

  
void eraseCmd(Stream& stream, class Params& params, class Program& program) {
  vc.reset();

  vc.setVcc(1);
  vc.setVpp(VppStatus::VppStatus_5V);
  vc.setProg(1);
  vc.setMode(Mode::ChipErase);

  delay(1);
  vc.setVpp(VppStatus::VppStatus_12V);
  delay(1);

  vc.setProg(0);

  delay(10); 
  vc.setProg(1);
  
  delay(1);
  vc.reset();
}

void writeCmd(Stream& stream, class Params& params, class Program& program) {
  vc.reset();

  vc.setVcc(1);
  vc.setVpp(VppStatus::VppStatus_5V);
  vc.setProg(1);
  vc.setMode(Mode::WriteCodeData);
  vc.setP1AsInput(false);

  delay(1);
  vc.setVpp(VppStatus::VppStatus_12V);
  delay(1);

  for (int i=0; i<params.getProgramSize(); ++i) {
    vc.setData(program.data[i]);
  
    delay(1);

    risingReadyPinCount = 0;
  
    vc.setProg(0);
    delayMicroseconds(30);
    vc.setProg(1);

    while (risingReadyPinCount < 1) {
      delayMicroseconds(10);
    }

    //delay(1);
    delayMicroseconds(10);

    //pulse xtal
    vc.setXtal1(1);
    delayMicroseconds(1);
    vc.setXtal1(0);
  }

  delay(5);
  vc.reset();
}

//void writeLockBit1(Stream& stream, class Params& params, class Program& program) {
//  writeLockBitImpl(stream, true);
//}
//
//void writeLockBit2(Stream& stream, class Params& params, class Program& program) {
//  writeLockBitImpl(stream, true);
//}
//
//void writeLockBitImpl(Stream& stream, bool bit1) {
//  vc.reset();
//
//  vc.setVcc(1);
//  delay(1);
//  vc.setVpp(VppStatus::VppStatus_5V);
//  vc.setProg(1);
//  delay(1);
//  vc.setMode(bit1 ? Mode::WriteLock_Bit1 : Mode::WriteLock_Bit2);
//
//  delay(1);
//  vc.setVpp(VppStatus::VppStatus_12V);
//  delay(1);
//
//  vc.setProg(0);
//  delayMicroseconds(30);
//  vc.setProg(1);
//
//  delay(5);
//  vc.setVpp(VppStatus::VppStatus_5V);
//  delay(1);
//
//  vc.reset();
//}

//====================================================================

CmdHandler handlers[] = {
  { "sps", setProgramSizeCmd },
  { "gps", getProgramSizeCmd },
  { "smf", setMemoryFragmentCmd },
  { "dp",  dumpProgramCmd },
  { "rs", readSignatureCmd },
  { "rp", readProgramCmd },
  { "er", eraseCmd },
  { "w", writeCmd },
//  { "wlb1", writeLockBit1 },
//  { "wlb2", writeLockBit2 },

  { "tsp", testSetPortCmd },
  { "trp", testResetPortsCmd },
 
};

//====================================================================

void loop() {
  Params params(arraySize(program.data));
  char cmd[MAX_COMMAND_LENGTH];

  while (true) {
    const int bytesRead = readLine(Serial, cmd, arraySize(cmd));
    
    if (bytesRead == 0) {
      continue;
    }

    const CMD_HANDLER_FUNC handler = getHandlerFor(handlers, cmd);
    if (handler) {
      sendCode(Serial, Code::OK, cmd);
      handler(Serial, params, program);
    } else {
      sendCode(Serial, Code::ERROR_UNKNOWN_COMMAND, cmd);
    }
  }
}

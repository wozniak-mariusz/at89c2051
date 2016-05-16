#pragma once

namespace Code {
  enum {
    OK                                                       = 0,
    ERROR_UNKNOWN_COMMAND                                    = 1,
    //SET PROGRAM SIZE
    ERROR_SPS_CANNOT_CONVERT_PARAM_PROGRAM_SIZE_TO_NUMBER    = 2,
    ERROR_SPS_WRONG_PROGRAM_SIZE                             = 3,
    //SET MEMORY FRAGMENT
    ERROR_SMF_CANNOT_CONVERT_PARAM_FRAGMENT_OFFSET_TO_NUMBER = 4,
    ERROR_SMF_PARAM_FRAGMENT_OFFSET_WRONG_VALUE              = 5,
    ERROR_SMF_CANNOT_CONVERT_PARAM_FRAGMENT_SIZE_TO_NUMBER   = 6,
    ERROR_SMF_PARAM_FRAGMENT_SIZE_WRONG_VALUE                = 7,
    ERROR_SMF_WRONG_BYTE_VALUE                               = 8,
    //DUMP PROGRAM
    ERROR_DP_WRONG_PROGRAMY_BYTE_VALUE                       = 9,
    //SET VCC
    ERROR_SP_CANNOT_CONVERT_PARAM_STATUS_TO_NUMBER           = 10,
    ERROR_SP_PARAM_STATUS_OUT_OF_RANGE                       = 11,
    ERROR_SP_CANNOT_CONVERT_PARAM_PORT_TO_NUMBER             = 12,
    ERROR_SP_UNKNOWN_PORT                                    = 13,
  };
}


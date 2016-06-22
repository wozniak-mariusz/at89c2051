# AT89C2051 programmer on the top of Arduino

## Circuit
![image of circuit](/desc/circuit.png)

Every square connector ◇ means connection to arduino pin. Adjacent to ◇ symbol there is text label (text on the label refers to constant in code). For instance AT89C2051 (shortcut AT89) pin named VCC is connected to `VCC_PORT`. `VCC_PORT` must reflect the phisical connection between AT89 and Arduino. `VCC_PORT` (and other constants) value is defined in [VoltageControl.cpp](/arduino/programmer/VoltageControl.cpp). Currently `VCC_PORT = 10` (works for my hardware). Same applies to other constants.
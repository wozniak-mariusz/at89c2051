# AT89C2051 programmer on the top of Arduino

## Circuit
![image of circuit](/desc/circuit.png)

Relation between R1 and R2:
`R2 = 1.5 ×  R1`

I've used `R1=10kΩ` and `R2=15kΩ`. R3 is pull-down resistor so `R3=1MΩ`.

Every square connector ◇ means connection to arduino pin. Adjacent to ◇ symbol there is text label (text on the label refers to constant in code). For instance AT89C2051 (shortcut AT89) pin named VCC is connected to `VCC_PORT`. `VCC_PORT` must reflect the phisical connection between AT89 and Arduino. `VCC_PORT` (and other constants) value is defined in [VoltageControl.cpp](/arduino/programmer/VoltageControl.cpp). Currently `VCC_PORT = 10` (works for my hardware). Same applies to other constants.

## Hardware
![image of hardware](/desc/hardware.png)
My implementation of circuit using universal board.

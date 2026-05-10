
## Von Neumann Model

<!-- ![alt text](image-1.png) -->

### Memory

For a $2^k \times m$ array of memory bits,

**Address** unique ($k$-bit) identifier of location  
**Contents** $m$-bit value stored in location

Basic operations: **LOAD** and **STORE**

Here we have **MDR** (Memory Address Register) and **MAR** (Memory Data Register)

To LOAD a location (A):  
1. Write the address (A) into the MAR.  
2. Send a “read” signal to the memory.  
3. Read the data from MDR.

To STORE a value (X) to a location (A):  
1. Write the data (X) to the MDR.  
2. Write the address (A) into the MAR.  
3. Send a “write” signal to the memory.

### Processing Unit

ALU and Temp.

**ALU** (Arithmetic and Logic Unit), LC-3 performs *ADD*, *AND* and *NOT*

**Registers** (Temp) Operands and results of functional units, LC-3 has eight registers (R0, …, R7), each 16 bits wide.

**Word Size** number of bits normally processed by ALU in one instruction, and it is also the width of registers.  
LC-3 is 16 bits.

### Input and Output

LC-3 supports keyboard (input) and monitor (output).

Keyboard has data register (**KBDR**) and status register (**KBSR**)  
Monitor has data register (**DDR**) and status register (**DSR**)

### Control Unit

Orchestrates execution of the program

**Instruction Register** (IR) contains the current instruction  
**Program Counter** (PC) contains the *address* of the next instruction to be executed.  
**Control Unit** reads an instruction from the memory, interprets the instruction and generates signals that tell the other components what to do  

### Instruction

One instruction specifies two things:  
**opcode** operation to be performed  
**operands** data/locations to be used for operation

An instruction is encoded as a sequence of bits. They are often encoded in a fixed length, such as 16 or 32 bits.

A computer’s instructions and their formats is known as its **Instruction Set Architecture** (**ISA**).

`SEXT(x)` means **sign extension**. `M[x]` means memory at address `x`.

#### ADD

`ADD` has opcode `0001`.

Register mode:

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5</b></td>
<td align="center"><b>4:3</b></td>
<td align="center"><b>2:0</b></td>
</tr>
<tr>
<td align="center"><code>0001</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>SR1</code></td>
<td align="center"><code>0</code></td>
<td align="center"><code>00</code></td>
<td align="center"><code>SR2</code></td>
</tr>
</table>

$$
DR \leftarrow SR1 + SR2
$$

Immediate mode:

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5</b></td>
<td align="center"><b>4:0</b></td>
</tr>
<tr>
<td align="center"><code>0001</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>SR1</code></td>
<td align="center"><code>1</code></td>
<td align="center"><code>imm5</code></td>
</tr>
</table>

$$
DR \leftarrow SR1 + \mathrm{SEXT}(imm5)
$$

#### AND

`AND` has opcode `0101`.

Register mode:

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5</b></td>
<td align="center"><b>4:3</b></td>
<td align="center"><b>2:0</b></td>
</tr>
<tr>
<td align="center"><code>0101</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>SR1</code></td>
<td align="center"><code>0</code></td>
<td align="center"><code>00</code></td>
<td align="center"><code>SR2</code></td>
</tr>
</table>

$$
DR \leftarrow SR1 \ \&\ SR2
$$

Immediate mode:

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5</b></td>
<td align="center"><b>4:0</b></td>
</tr>
<tr>
<td align="center"><code>0101</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>SR1</code></td>
<td align="center"><code>1</code></td>
<td align="center"><code>imm5</code></td>
</tr>
</table>

$$
DR \leftarrow SR1 \ \&\ \mathrm{SEXT}(imm5)
$$

#### NOT

`NOT` has opcode `1001`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5:0</b></td>
</tr>
<tr>
<td align="center"><code>1001</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>SR</code></td>
<td align="center"><code>111111</code></td>
</tr>
</table>

$$
DR \leftarrow \sim SR
$$

#### LD

`LD` has opcode `0010`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:0</b></td>
</tr>
<tr>
<td align="center"><code>0010</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>PCoffset9</code></td>
</tr>
</table>

$$
DR \leftarrow M[PC + \mathrm{SEXT}(PCoffset9)]
$$

#### ST

`ST` has opcode `0011`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:0</b></td>
</tr>
<tr>
<td align="center"><code>0011</code></td>
<td align="center"><code>SR</code></td>
<td align="center"><code>PCoffset9</code></td>
</tr>
</table>

$$
M[PC + \mathrm{SEXT}(PCoffset9)] \leftarrow SR
$$

#### LDR

`LDR` has opcode `0110`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5:0</b></td>
</tr>
<tr>
<td align="center"><code>0110</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>BaseR</code></td>
<td align="center"><code>offset6</code></td>
</tr>
</table>

$$
DR \leftarrow M[BaseR + \mathrm{SEXT}(offset6)]
$$

#### STR

`STR` has opcode `0111`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5:0</b></td>
</tr>
<tr>
<td align="center"><code>0111</code></td>
<td align="center"><code>SR</code></td>
<td align="center"><code>BaseR</code></td>
<td align="center"><code>offset6</code></td>
</tr>
</table>

$$
M[BaseR + \mathrm{SEXT}(offset6)] \leftarrow SR
$$

#### LDI

`LDI` has opcode `1010`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:0</b></td>
</tr>
<tr>
<td align="center"><code>1010</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>PCoffset9</code></td>
</tr>
</table>

$$
DR \leftarrow M[M[PC + \mathrm{SEXT}(PCoffset9)]]
$$

#### STI

`STI` has opcode `1011`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:0</b></td>
</tr>
<tr>
<td align="center"><code>1011</code></td>
<td align="center"><code>SR</code></td>
<td align="center"><code>PCoffset9</code></td>
</tr>
</table>

$$
M[M[PC + \mathrm{SEXT}(PCoffset9)]] \leftarrow SR
$$

#### LEA

`LEA` has opcode `1110`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:0</b></td>
</tr>
<tr>
<td align="center"><code>1110</code></td>
<td align="center"><code>DR</code></td>
<td align="center"><code>PCoffset9</code></td>
</tr>
</table>

$$
DR \leftarrow PC + \mathrm{SEXT}(PCoffset9)
$$

#### BR

`BR` has opcode `0000`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11</b></td>
<td align="center"><b>10</b></td>
<td align="center"><b>9</b></td>
<td align="center"><b>8:0</b></td>
</tr>
<tr>
<td align="center"><code>0000</code></td>
<td align="center"><code>n</code></td>
<td align="center"><code>z</code></td>
<td align="center"><code>p</code></td>
<td align="center"><code>PCoffset9</code></td>
</tr>
</table>

$$
\text{if condition matches CC, } PC \leftarrow PC + \mathrm{SEXT}(PCoffset9)
$$

Examples:

```assembly
BRz LABEL
BRnp LABEL
BRnzp LABEL
```

#### JMP and RET

`JMP` has opcode `1100`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5:0</b></td>
</tr>
<tr>
<td align="center"><code>1100</code></td>
<td align="center"><code>000</code></td>
<td align="center"><code>BaseR</code></td>
<td align="center"><code>000000</code></td>
</tr>
</table>

$$
PC \leftarrow BaseR
$$

`RET` is a special form of `JMP`.

```assembly
RET
```

$$
PC \leftarrow R7
$$

#### JSR and JSRR

`JSR` has opcode `0100`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11</b></td>
<td align="center"><b>10:0</b></td>
</tr>
<tr>
<td align="center"><code>0100</code></td>
<td align="center"><code>1</code></td>
<td align="center"><code>PCoffset11</code></td>
</tr>
</table>

$$
R7 \leftarrow PC,\quad PC \leftarrow PC + \mathrm{SEXT}(PCoffset11)
$$

`JSRR` also has opcode `0100`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:9</b></td>
<td align="center"><b>8:6</b></td>
<td align="center"><b>5:0</b></td>
</tr>
<tr>
<td align="center"><code>0100</code></td>
<td align="center"><code>000</code></td>
<td align="center"><code>BaseR</code></td>
<td align="center"><code>000000</code></td>
</tr>
</table>

$$
R7 \leftarrow PC,\quad PC \leftarrow BaseR
$$

#### TRAP

`TRAP` has opcode `1111`.

<table>
<tr>
<td align="center"><b>15:12</b></td>
<td align="center"><b>11:8</b></td>
<td align="center"><b>7:0</b></td>
</tr>
<tr>
<td align="center"><code>1111</code></td>
<td align="center"><code>0000</code></td>
<td align="center"><code>trapvect8</code></td>
</tr>
</table>

$$
\text{call OS routine indexed by } trapvect8
$$

Common TRAP routines:

```text
GETC   x20   read one character
OUT    x21   print one character
PUTS   x22   print a string
IN     x23   read and echo one character
HALT   x25   stop execution
```

#### Opcode Summary

```text
0000  BR
0001  ADD
0010  LD
0011  ST
0100  JSR / JSRR
0101  AND
0110  LDR
0111  STR
1000  RTI
1001  NOT
1010  LDI
1011  STI
1100  JMP / RET
1101  reserved
1110  LEA
1111  TRAP
```

### Instruction Processing

(To be completed)


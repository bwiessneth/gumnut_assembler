__version__ = "1.0.0"
__author__ = "Benjamin Wiessneth"


from collections import OrderedDict

import re
import os
import logging
import json
from GumnutAssembler import GumnutExceptions

logger = logging.getLogger("root")


class GumnutAssembler:
    def __init__(self):
        # RAW asm source code as a list of strings
        self.ASMSourceList = list()
        self.ASMLineCount = -1
        self.ParsedASMLineCount = -1

        # Parsed asm source code as a list of ASMLINE tuples
        self.ParsedASMList = list()

        # Instruction memory as a list of integers
        self.InstrList = list()
        self.InstrCount = 0
        self.InstrMemPointer = 0

        # Data memory as a list of integers
        self.DataList = list()
        self.DataCount = 0
        self.DataMemPointer = 0

        self.text_directive = True

        # Clear instruction and data memory
        self._clear_memory()

        # Dictionaries for references
        self.ProgRefDict = dict()
        self.DataRefDict = dict()
        self.VarRefDict = dict()

        # Parser flags
        self.NeedSecondRun = False

        #
        self.source_objectcode_map = OrderedDict()

        #
        self.instruction_set_requirements = [
            GasmInstruction(instruction="text"),
            GasmInstruction(instruction="data"),
            GasmInstruction(instruction="org"),
            GasmInstruction(instruction="byte"),
            GasmInstruction(instruction="bss"),
            GasmInstruction(instruction="equ"),
            GasmInstruction(instruction="add"),
            GasmInstruction(instruction="addc"),
            GasmInstruction(instruction="sub"),
            GasmInstruction(instruction="subc"),
            GasmInstruction(instruction="and"),
            GasmInstruction(instruction="or"),
            GasmInstruction(instruction="xor"),
            GasmInstruction(instruction="mask"),
            GasmInstruction(instruction="shl"),
            GasmInstruction(instruction="shr"),
            GasmInstruction(instruction="rol"),
            GasmInstruction(instruction="ror"),
            GasmInstruction(instruction="ldm"),
            GasmInstruction(instruction="stm"),
            GasmInstruction(instruction="inp"),
            GasmInstruction(instruction="out"),
            GasmInstruction(instruction="bz"),
            GasmInstruction(instruction="bnz"),
            GasmInstruction(instruction="bc"),
            GasmInstruction(instruction="bnc"),
            GasmInstruction(instruction="jmp"),
            GasmInstruction(instruction="jsb"),
            GasmInstruction(instruction="ret"),
            GasmInstruction(instruction="reti"),
            GasmInstruction(instruction="enai"),
            GasmInstruction(instruction="disi"),
            GasmInstruction(instruction="wait"),
            GasmInstruction(instruction="stby"),
        ]

    def load_asm_source_from_file(self, filename):
        """
        Load assembler source from file and split each line into a list

        :param filename: Path to source file
        """
        with open(filename) as f:
            file_content = f.read()

        self.ASMSourceList = file_content.split("\n")
        self.ASMLineCount = len(self.ASMSourceList)

    def load_asm_source(self, source):
        """
        Load assembler source from string and split each line into a
        list

        :param source: Source code as a string
        """
        self.ASMSourceList = source.split("\n")
        self.ASMLineCount = len(self.ASMSourceList)

    def assemble(self):
        self._parse_asm_source()
        logger.debug("FIRST PASS")
        self._iterate()
        logger.debug("SECOND PASS")
        self._iterate()

    def _check_number(self, operand):
        """
        Check operand for number format and return number as base 10
        otherwise return original operand

        :param operand: The number to check as a string.
                        ``0xDE``, ``0b0110``, ``12``

        :return: The number as a integer with base ``10`` if the
                 input was a valid number string. Otherwise ``-1``

        :todo: Refactor two's complement conversion
        """
        # Check if operand isn't of type None and isn't a register
        if operand and not operand[0] == "r":
            # Check for floating point numbers
            if operand.find(".") != -1 or operand.find(",") != -1:
                return -1

            negative = False
            result = 0

            # Strip sign from operand
            if operand[0] == "+":
                operand = operand.replace("+", "")
            elif operand[0] == "-":
                operand = operand.replace("-", "")
                negative = True

            # Check for HEX prefix
            if operand[0:2] == "0x":
                # Convert number to DEC
                result = int(operand[2 : len(operand)], 16)
                if negative:
                    result = (~(result) & 0xFF) + 1
                    return result
                else:
                    return result
            # Check for BIN prefix
            elif operand[0:2] == "0b":
                # Convert number to DEC
                result = int(operand[2 : len(operand)], 2)
                return result
            elif operand.isdigit():
                # Operand is already a number
                result = int(operand)
                if negative and result != 0:
                    result = (~(result) & 0xFF) + 1
                    return result
                else:
                    return result

        return operand

    def _format_input(self, operand):
        """
        Format the parsed inputs by removing any whitespace
        """
        if operand:
            operand = operand.replace(" ", "")
            return operand
        else:
            return None

    def _extract_identifier_from_line(self, asm_source):
        """
        Extract identifiers from assembly source line via regex

        :param asm_source: A string containing a single line of asm
                           code.

        :return: A GasmLine Object containing the extracted data.
                 ``False`` if there was no match.

        :todo: Add support for ascii chars e.g.:  char_a: equ 'a'
        """
        # Generate regex pattern
        pattern = re.compile(
            r"^\s*(?:([A-Za-z]\w*)[:])?(?:\s*([A-Za-z]{2,4})(?:\s+([A-Za-z0-9+-]\w*)(?:\s)*(?:[,])*(?:\s)*(?:[\(])*(?:\s*)([A-Za-z0-9]\w*)?(?:\s)*(?:[\)])*(?:\s*[,]*\s*([A-Za-z0-9\+\-\ \_]*))?)?)?"  # noqa: E501
        )

        # Match regex pattern against current line
        match = pattern.match(asm_source)

        # Check if we got a match
        if match:
            # List to hold parsed identifiers and/or values
            result = [None, None, None, None, None, None]

            # TODO: Fix regex pattern to avoid the following few lines
            for i in range(1, 6, 1):
                result[i] = self._format_input(match.group(i))

            # Take data from each group and build a GasmLine
            # Check and convert numbers for rd, rs and rs2
            parsed_asm_line = GasmLine(
                label=result[1],
                instruction=result[2],
                rd=self._check_number(result[3]),
                op1=self._check_number(result[4]),
                op2=self._check_number(result[5]),
            )

            self._validate_asm_line(parsed_asm_line)
            return parsed_asm_line
        else:
            # TODO: Catch source errors?
            logger.critical("No match found")
            return False

    def _parse_asm_source(self):
        """
        Loop through each line of raw assembler source and generate a
        list of GasmLines.
        """
        self.ParsedASMLineCount = 0

        # Loop through each line of raw assembler source
        for asm_source_line in self.ASMSourceList:
            parsed_asm_line = self._extract_identifier_from_line(asm_source_line)
            if parsed_asm_line:
                # Append this GasmLine to our list of parsed GasmLines
                self.ParsedASMList.append(parsed_asm_line)

                # Populate source code column in source_objectcode_map
                self.source_objectcode_map.update(
                    {self.ParsedASMLineCount: [asm_source_line, parsed_asm_line, None, None]}
                )

                self.ParsedASMLineCount += 1
            else:
                logger.error("No match found")

        logger.info("Parsed %d lines of code", self.ParsedASMLineCount)

    def _check_if_immed_instr(self, operand):
        """
        Check if the passed operand is suitable for a immediate
        instruction. To do this check if passed operand is a
        register/reference or a number.

        :param operand: A string to check for register/reference.

        :return: ``True`` if operand is a number or reference
                 ``False`` if operand is register or invalid
        """
        if type(operand) is None:
            return False
        elif type(operand) == int:
            return True
        elif operand[0] == "r" and operand[1].isdigit():
            return False
        elif self._get_reference_or_value(operand):
            return True
        else:
            return False

    def _get_register_number(self, operand):
        """
        Extract the register number from operand string

        :param operand: A string from which to get the register number

        :return: ``integer`` if operand is a number
                 ``-1`` if operand is no valid number
        """
        # Check if operand isn't of type None
        if operand and type(operand) != int:
            # Check if operand has the format "r1"
            if operand[0] == "r" and operand[1].isdigit():
                # Return number without "r"
                return int(operand[1 : len(operand)])
            else:
                # No valid register number
                return -1
        else:
            # No valid register number
            return -1

    def _get_reference_or_value(self, operand):
        # Check if operand isn't of type None
        if type(operand) is not None and operand:
            # Check if operand is a reference
            if self._check_operand_for_reference(operand):
                # Get reference address from dictionary
                ref = self._get_reference(operand)
                return ref
            else:
                tmp = int(operand)
                return tmp
        else:
            return 0

    def _check_operand_for_reference(self, operand):
        """
        Check if operand is a valid reference
        """
        # Check if operand isn't of type None
        if type(operand) is not None and operand:
            # Check if op is a digit
            if type(operand) == int or operand.isdigit():
                return False
            # Check if op is a HEX number
            elif operand[0:2] == "0x":
                return False
            # Check if op is a BIN number
            elif operand[0:2] == "0b":
                return False
            # Check if op is a register
            elif operand[0] == "r" and operand[1].isdigit():
                return False
            else:
                # op is a reference
                return True
        else:
            # op is can't be a reference
            return False

    def _get_reference(self, reference):
        """
        Get a reference's value
        """
        # Check if reference is a prog reference
        if self.ProgRefDict.get(reference):
            return self.ProgRefDict[reference]
        # Check if reference is a data reference
        elif self.DataRefDict.get(reference):
            return self.DataRefDict[reference]
        else:
            # reference isn't known yet
            logger.debug('Unknown reference "%s". Need a second pass', reference)
            self.NeedSecondRun = True
            return False

    def _clear_memory(self):
        """
        Clear both memory lists and set each cell to 0
        """
        self.InstrList.clear()
        for i in range(0, 4096, 1):
            self.InstrList.insert(i, 0)
        self.DataList.clear()
        for i in range(0, 256, 1):
            self.DataList.insert(i, 0)

    def _assemble_source_line(self, asm_line):
        """
        Assemble a single code line
        """
        # Split content of GasmLine into shorter, readable vars
        label = asm_line.label
        instr = asm_line.instruction
        rd = asm_line.rd
        rs = asm_line.op1
        rs2 = asm_line.op2

        # Var to hold generated Bit sequence of current line
        BitField = 0x00

        # Check for directives
        if instr == "byte":
            logger.debug('Found data var "%s" (%s) = %s @ %d', label, instr, rd, self.DataMemPointer)
            self.DataRefDict[label] = self.DataMemPointer
            self.DataList[self.DataMemPointer] = rd
            self.DataMemPointer += 1
            return -1
        elif instr == "bss":
            logger.debug('Found data var "%s" (%s) = %s @ %d', label, instr, rd, self.DataMemPointer)
            self.DataRefDict[label] = self.DataMemPointer
            self.DataList[self.DataMemPointer] = 0
            self.DataMemPointer += 1
            return -1
        elif instr == "ascii":
            logger.debug('Found data var "%s" (%s) = %s @ %d', label, instr, rd, self.DataMemPointer)
            self.DataRefDict[label] = self.DataMemPointer
            self.DataList[self.DataMemPointer] = rd
            self.DataMemPointer += 1
            return -1
        elif instr == "equ":
            logger.debug("%s instruction %s = %s", instr, label, rd)
            value = rd
            self.DataRefDict[label] = value
            return -1
        elif instr == "text":
            logger.debug("%s directive found", instr)
            self.text_directive = True
            return -1
        elif instr == "data":
            logger.debug("%s directive found", instr)
            self.text_directive = False
            return -1
        elif instr == "org":
            logger.debug("%s instruction = %s", instr, rd)
            if self.text_directive:
                self.InstrMemPointer = int(rd)
            else:
                self.DataMemPointer = int(rd)
            return -1

        # Check if current line has a label
        if label:
            logger.debug('Found label "%s" @ %d', label, self.InstrMemPointer)
            # Create dictionary item with label and instruction memory pointer
            self.ProgRefDict[label] = self.InstrMemPointer

        # Generate instruction memory from instruction, rd, op1, op2
        # Arithemtic and logical instructions
        if instr == "add":
            if self._check_if_immed_instr(rs2):
                # Immediate access
                logger.debug("%s immediate instruction", instr)
                BitField |= 0b0000 << 14
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_reference_or_value(rs2)
            else:
                # Register access
                logger.debug("%s register access instruction", instr)
                BitField |= 0b1110 << 14
                BitField |= 0b000
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_register_number(rs2) << 5  # Place rs2
        elif instr == "addc":
            if self._check_if_immed_instr(rs2):
                # Immediate access
                logger.debug("%s immediate instruction", instr)
                BitField |= 0b0001 << 14
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_reference_or_value(rs2)
            else:
                # Register access
                logger.debug("%s register access instruction", instr)
                BitField |= 0b1110 << 14
                BitField |= 0b001
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_register_number(rs2) << 5  # Place rs2
        elif instr == "sub":
            if self._check_if_immed_instr(rs2):
                # Immediate access
                logger.debug("%s immediate instruction", instr)
                BitField |= 0b0010 << 14
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_reference_or_value(rs2)  # Place rs2
            else:
                # Register access
                logger.debug("%s sing AJAXregister access instruction", instr)
                BitField |= 0b1110 << 14
                BitField |= 0b010
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_register_number(rs2) << 5  # Place rs2
        elif instr == "subc":
            if self._check_if_immed_instr(rs2):
                # Immediate access
                logger.debug("%s immediate instruction", instr)
                BitField |= 0b0011 << 14
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_reference_or_value(rs2)  # Place rs2
            else:
                # Register access
                logger.debug("%s register access instruction", instr)
                BitField |= 0b1110 << 14
                BitField |= 0b011
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_register_number(rs2) << 5  # Place rs2
        elif instr == "and":
            if self._check_if_immed_instr(rs2):
                # Immediate access
                logger.debug("%s immediate instruction", instr)
                BitField |= 0b0100 << 14
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_reference_or_value(rs2)
            else:
                # Register access
                logger.debug("%s register access instruction", instr)
                BitField |= 0b1110 << 14
                BitField |= 0b100
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_register_number(rs2) << 5  # Place rs2
        elif instr == "or":
            if self._check_if_immed_instr(rs2):
                # Immediate access
                logger.debug("%s immediate instruction", instr)
                BitField |= 0b0101 << 14
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_reference_or_value(rs2)  # Place rs2
            else:
                # Register access
                logger.debug("%s register access instruction", instr)
                BitField |= 0b1110 << 14
                BitField |= 0b101
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_register_number(rs2) << 5  # Place rs2
        elif instr == "xor":
            if self._check_if_immed_instr(rs2):
                # Immediate access
                logger.debug("%s immediate instruction", instr)
                BitField |= 0b0110 << 14
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_reference_or_value(rs2)  # Place rs2
            else:
                # Register access
                logger.debug("%s register access instruction", instr)
                BitField |= 0b1110 << 14
                BitField |= 0b110
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_register_number(rs2) << 5  # Place rs2
        elif instr == "mask":
            if self._check_if_immed_instr(rs2):
                # Immediate access
                logger.debug("%s immediate instruction", instr)
                BitField |= 0b0111 << 14
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_reference_or_value(rs2)  # Place rs2
            else:
                # Register access
                logger.debug("%s register access instruction", instr)
                BitField |= 0b1110 << 14
                BitField |= 0b111
                BitField |= self._get_register_number(rd) << 11  # Place rd
                BitField |= self._get_register_number(rs) << 8  # Place rs
                BitField |= self._get_register_number(rs2) << 5  # Place rs2

        # Shift instructions
        elif instr == "shl":
            logger.debug("%s instruction", instr)
            BitField |= 0b110 << 15
            BitField |= 0b00
            BitField |= self._get_register_number(rd) << 11  # Place rd
            BitField |= self._get_register_number(rs) << 8  # Place rs
            BitField |= self._get_reference_or_value(rs2) << 5  # Place rs2
        elif instr == "shr":
            logger.debug("%s instruction", instr)
            BitField |= 0b110 << 15
            BitField |= 0b01
            BitField |= self._get_register_number(rd) << 11  # Place rd
            BitField |= self._get_register_number(rs) << 8  # Place rs
            BitField |= self._get_reference_or_value(rs2) << 5  # Place rs2
        elif instr == "rol":
            logger.debug("%s instruction", instr)
            BitField |= 0b110 << 15
            BitField |= 0b10
            BitField |= self._get_register_number(rd) << 11  # Place rd
            BitField |= self._get_register_number(rs) << 8  # Place rs
            BitField |= self._get_reference_or_value(rs2) << 5  # Place rs2
        elif instr == "ror":
            logger.debug("%s instruction", instr)
            BitField |= 0b110 << 15
            BitField |= 0b11
            BitField |= self._get_register_number(rd) << 11  # Place rd
            BitField |= self._get_register_number(rs) << 8  # Place rs
            BitField |= self._get_reference_or_value(rs2) << 5  # Place rs2

        # Memory and I/O instructions
        elif instr == "ldm":
            logger.debug("%s instruction", instr)
            BitField |= 0b10 << 16
            BitField |= 0b00 << 14
            BitField |= self._get_register_number(rd) << 11  # Place rd
            if self._get_register_number(rs) == -1:
                # Direct offset
                source = 0
                offset = self._get_reference_or_value(rs)
                if rs2:
                    offset += rs2
            else:
                # Register + offset
                source = self._get_register_number(rs)
                offset = self._get_reference_or_value(rs2)

            BitField |= source << 8
            BitField |= offset
        elif instr == "stm":
            logger.debug("%s instruction", instr)
            BitField |= 0b10 << 16
            BitField |= 0b01 << 14
            BitField |= self._get_register_number(rd) << 11  # Place rd
            if self._get_register_number(rs) == -1:
                # Direct offset
                source = 0
                offset = self._get_reference_or_value(rs)
            else:
                # Register + offset
                source = self._get_register_number(rs)
                offset = self._get_reference_or_value(rs2)

            BitField |= source << 8
            BitField |= offset
        elif instr == "inp":
            logger.debug("%s instruction", instr)
            BitField |= 0b10 << 16
            BitField |= 0b10 << 14
            BitField |= self._get_register_number(rd) << 11  # Place rd
            if self._get_register_number(rs) == -1:
                # Direct offset
                source = 0
                offset = self._get_reference_or_value(rs)
            else:
                # Register + offset
                source = self._get_register_number(rs)
                offset = self._get_reference_or_value(rs2)

            BitField |= source << 8
            BitField |= offset
        elif instr == "out":
            logger.debug("%s instruction", instr)
            BitField |= 0b10 << 16
            BitField |= 0b11 << 14
            BitField |= self._get_register_number(rd) << 11  # Place rd
            if self._get_register_number(rs) == -1:
                # Direct offset
                source = 0
                offset = self._get_reference_or_value(rs)
            else:
                # Register + offset
                source = self._get_register_number(rs)
                offset = self._get_reference_or_value(rs2)

            BitField |= source << 8
            BitField |= offset

        # Branch instructions
        elif instr == "bz":
            logger.debug("%s instruction", instr)
            BitField |= 0b111110 << 12
            BitField |= 0b00 << 10
            disp = (self._get_reference_or_value(rd) - 1 - self.InstrMemPointer) & 0xFF
            BitField |= disp
        elif instr == "bnz":
            logger.debug("%s instruction", instr)
            BitField |= 0b111110 << 12
            BitField |= 0b01 << 10
            disp = (self._get_reference_or_value(rd) - 1 - self.InstrMemPointer) & 0xFF
            BitField |= disp
        elif instr == "bc":
            logger.debug("%s instruction", instr)
            BitField |= 0b111110 << 12
            BitField |= 0b10 << 10
            disp = (self._get_reference_or_value(rd) - 1 - self.InstrMemPointer) & 0xFF
            BitField |= disp
        elif instr == "bnc":
            logger.debug("%s instruction", instr)
            BitField |= 0b111110 << 12
            BitField |= 0b11 << 10
            disp = (self._get_reference_or_value(rd) - 1 - self.InstrMemPointer) & 0xFF
            BitField |= disp

        # Jump instructions
        elif instr == "jmp":
            logger.debug("%s instruction", instr)
            BitField |= 0b11110 << 13
            BitField |= 0b0 << 12
            BitField |= self._get_reference_or_value(rd) & 0xFFF
        elif instr == "jsb":
            logger.debug("%s instruction", instr)
            BitField |= 0b11110 << 13
            BitField |= 0x1 << 12
            BitField |= self._get_reference_or_value(rd) & 0xFFF

        # Others
        elif instr == "ret":
            logger.debug("%s instruction", instr)
            BitField |= 0b1111110 << 11
            BitField |= 0b000 << 8
        elif instr == "reti":
            logger.debug("%s instruction", instr)
            BitField |= 0b1111110 << 11
            BitField |= 0b001 << 8
        elif instr == "enai":
            logger.debug("%s instruction", instr)
            BitField |= 0b1111110 << 11
            BitField |= 0b010 << 8
        elif instr == "disi":
            logger.debug("%s instruction", instr)
            BitField |= 0b1111110 << 11
            BitField |= 0b011 << 8
        elif instr == "wait":
            logger.debug("%s instruction", instr)
            BitField |= 0b1111110 << 11
            BitField |= 0b100 << 8
        elif instr == "stby":
            logger.debug("%s instruction", instr)
            BitField |= 0b1111110 << 11
            BitField |= 0b101 << 8
        return BitField

    def _iterate(self):
        """
        Loop one time through all source lines and assemble object
        code.
        """
        self.InstrMemPointer = 0
        self.DataMemPointer = 0
        self._clear_memory()

        used_dict_entry = list()

        # Loop through all parsed lines
        for line in self.ParsedASMList:
            # Check if the current line is empty (Comment or line break)
            if line.is_empty():
                continue
            else:
                result = self._assemble_source_line(line)
                if result != -1:
                    if self.InstrMemPointer > 4095:
                        raise GumnutExceptions.InstructionMemorySizeExceeded(
                            self.InstrMemPointer, "Maximum instruction memory size hit"
                        )

                    self.InstrList[self.InstrMemPointer] = result

                    for line_number, value in self.source_objectcode_map.items():
                        if value[1] == line and not (line_number in used_dict_entry):
                            # print(line_number)
                            used_dict_entry.append(line_number)
                            old_value = self.source_objectcode_map[line_number]
                            new_value = (old_value[0], old_value[1], result, self.InstrMemPointer)
                            self.source_objectcode_map[line_number] = new_value
                            break

                    self.InstrCount += 1
                    self.InstrMemPointer += 1
                    # logger.debug('Insert instruction "%s" @ %d', result,
                    #             self.InstrMemPointer)
                else:
                    continue

    def create_output_files(self, datafile=r"gasm_data.dat", textfile=r"gasm_text.dat"):
        """
        Create output files
        """
        # Open/Create output files
        # import pdb; pdb.set_trace()

        os.makedirs(os.path.dirname(datafile), exist_ok=True)
        with open(textfile, "w") as tf:
            for bitfield in self.InstrList:
                tf.write(str("%x" % bitfield) + "\n")

        os.makedirs(os.path.dirname(textfile), exist_ok=True)
        with open(datafile, "w") as df:
            for data in self.DataList:
                df.write(str("%x" % int(data)) + "\n")

    def get_instruction_memory(self):
        """
        Return instruction memory as a list.
        """
        return self.InstrList

    def get_data_memory(self):
        """
        Return data memory as a list
        """
        return self.DataList

    # ..
    def print_source_objcode_map(self):
        print("%-8s%-80s%-10s%-10s" % ("Line", "Source", "OBJCode", "Address"))
        for line_number, value in self.source_objectcode_map.items():
            if value[2] and value[3]:
                print("%-8s%-80s%-10s%-10s" % (line_number, value[0], hex(value[2]), hex(value[3])))
            else:
                print("%-8s%-80s" % (line_number, value[0]))
        return

    def _validate_asm_line(self, asm_line):
        if asm_line.instruction is not None:

            # Get requirements for the instruction
            # TODO: Only instruction is evaluated as of now. Extend by rd, op1, op2
            if any(x.instruction == asm_line.instruction for x in self.instruction_set_requirements):
                return True

            raise GumnutExceptions.InvalidInstruction(asm_line.__str__(), "Unknown instruction")
        else:
            return True


class GasmLine:
    def __init__(self, label=None, instruction=None, rd=None, op1=None, op2=None):
        self.label = label
        self.instruction = instruction
        self.rd = rd
        self.op1 = op1
        self.op2 = op2

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def is_empty(self):
        if (
            self.label is None
            and self.instruction is None
            and self.rd is None
            and self.op1 is None
            and self.op2 is None
        ):
            return True
        else:
            return False

    def __str__(self):
        output_str = ""
        if self.label:
            output_str += self.label + " "
        if self.instruction:
            output_str += self.instruction + " "
        if self.rd:
            output_str += str(self.rd) + " "
        if self.op1:
            output_str += str(self.op1) + " "
        if self.op2:
            output_str += str(self.op2) + " "
        return output_str

    def __repr__(self):
        return "<GasmLine> " + self.__str__()


class GasmInstruction:
    def __init__(self, instruction=None, rd=False, op1=False, op2=False):
        self.instruction = instruction
        self.rd = rd
        self.op1 = op1
        self.op2 = op2


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GumnutAssembler")
    parser.add_argument("source", help="Gumnut assembler source files")
    parser.add_argument("-o", "--out-dir", help="Directory where the output files should be placed", default=".\\")
    parser.add_argument("-j", "--json", help="Enable JSON output", action="store_true")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {}".format(__version__),
        help="show the version number and exit",
    )

    args = parser.parse_args()

    file_name = os.path.basename(args.source)
    out_name, file_ext = os.path.splitext(file_name)

    datafile = os.path.join(args.out_dir, out_name + "_data.dat")
    textfile = os.path.join(args.out_dir, out_name + "_text.dat")

    gass = GumnutAssembler()
    gass.load_asm_source_from_file(args.source)
    gass.assemble()

    if args.json:
        return_data = {}
        return_data["text"] = gass.get_instruction_memory()
        return_data["data"] = gass.get_data_memory()
        print(json.dumps(return_data))
        return 0
    else:
        gass.create_output_files(datafile, textfile)
        return 0


if __name__ == "__main__":
    main()

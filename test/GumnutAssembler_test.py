import os
import sys

import pytest
from helper import generate_md5

test_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, test_path + "/../")
sys.path.insert(0, "GumnutSimulator")
sys.path.insert(0, os.getcwd())  # Add current directory to PYTHONPATH

from gaspy import GumnutAssembler  # noqa: E402
from gaspy import GumnutExceptions  # noqa: E402
from gaspy.GumnutAssembler import GasmLine  # noqa: E402


@pytest.fixture
def gass():
    return GumnutAssembler.GumnutAssembler()


def test_check_number_dec(gass):
    assert gass._check_number("0") == 0
    assert gass._check_number("1") == 1
    assert gass._check_number("15") == 15
    assert gass._check_number("255") == 255


def test_check_number_hex(gass):
    assert gass._check_number("0x0") == 0
    assert gass._check_number("0x1") == 1
    assert gass._check_number("0xF") == 15
    assert gass._check_number("0xFF") == 255


def test_check_number_bin(gass):
    assert gass._check_number("0b0") == 0
    assert gass._check_number("0b1") == 1
    assert gass._check_number("0b1111") == 0xF
    assert gass._check_number("0b11111111") == 0xFF


def test_check_number_negative(gass):
    assert gass._check_number("-1") == 0xFF
    assert gass._check_number("-2") == 0xFE
    assert gass._check_number("-3") == 0xFD
    assert gass._check_number("-126") == 0x82
    assert gass._check_number("-127") == 0x81
    assert gass._check_number("-128") == 0x80


def test_check_number_identifier(gass):
    assert gass._check_number("r0") == "r0"
    assert gass._check_number("reference") == "reference"
    assert gass._check_number("label:") == "label:"


def test_check_number_floats(gass):
    assert gass._check_number("0.123") == -1
    assert gass._check_number("0,123") == -1
    assert gass._check_number("+0.123") == -1
    assert gass._check_number("+0,123") == -1
    assert gass._check_number("-0.123") == -1
    assert gass._check_number("-0,123") == -1


def test_extract_identifier_from_line_arithmetic_instructions(gass):
    # Arithemtic and logical instructions
    # Register access
    assert gass._extract_identifier_from_line("add r0, r0, r0") == GasmLine(None, "add", "r0", "r0", "r0")
    assert gass._extract_identifier_from_line("add r0, r1, r2") == GasmLine(None, "add", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("addc r0, r1, r2") == GasmLine(None, "addc", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("sub r0, r1, r2") == GasmLine(None, "sub", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("subc r0, r1, r2") == GasmLine(None, "subc", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("and r0, r1, r2") == GasmLine(None, "and", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("or r0, r1, r2") == GasmLine(None, "or", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("xor r0, r1, r2") == GasmLine(None, "xor", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("mask r0, r1, r2") == GasmLine(None, "mask", "r0", "r1", "r2")

    assert gass._extract_identifier_from_line("add r8, r9, r10") == GasmLine(None, "add", "r8", "r9", "r10")
    # Immediate access
    assert gass._extract_identifier_from_line("add r0, r0, 0x0") == GasmLine(None, "add", "r0", "r0", 0)
    assert gass._extract_identifier_from_line("add r0, r1, 0x12") == GasmLine(None, "add", "r0", "r1", 18)
    assert gass._extract_identifier_from_line("addc r0, r1, 0x12") == GasmLine(None, "addc", "r0", "r1", 18)
    assert gass._extract_identifier_from_line("sub r0, r1, 0x12") == GasmLine(None, "sub", "r0", "r1", 18)
    assert gass._extract_identifier_from_line("subc r0, r1, 0x12") == GasmLine(None, "subc", "r0", "r1", 18)
    assert gass._extract_identifier_from_line("and r0, r1, 0x12") == GasmLine(None, "and", "r0", "r1", 18)
    assert gass._extract_identifier_from_line("or r0, r1, 0x12") == GasmLine(None, "or", "r0", "r1", 18)
    assert gass._extract_identifier_from_line("xor r0, r1, 0x12") == GasmLine(None, "xor", "r0", "r1", 18)
    assert gass._extract_identifier_from_line("mask r0, r1, 0x12") == GasmLine(None, "mask", "r0", "r1", 18)


def test_extract_identifier_from_line_shift_instructions(gass):
    # Shift instructions
    assert gass._extract_identifier_from_line("shl r1, r2, 0x2") == GasmLine(None, "shl", "r1", "r2", 2)
    assert gass._extract_identifier_from_line("shr r1, r2, 0x2") == GasmLine(None, "shr", "r1", "r2", 2)
    assert gass._extract_identifier_from_line("rol r1, r2, 0x2") == GasmLine(None, "rol", "r1", "r2", 2)
    assert gass._extract_identifier_from_line("ror r1, r2, 0x2") == GasmLine(None, "ror", "r1", "r2", 2)


def test_extract_identifier_from_line_memory_io_instructions(gass):
    # Memory and I/O instructions
    # Direct access
    assert gass._extract_identifier_from_line("ldm r1, 0x12") == GasmLine(None, "ldm", "r1", 18, None)
    assert gass._extract_identifier_from_line("stm r1, 0x12") == GasmLine(None, "stm", "r1", 18, None)
    assert gass._extract_identifier_from_line("inp r1, 0x12") == GasmLine(None, "inp", "r1", 18, None)
    assert gass._extract_identifier_from_line("out r1, 0x12") == GasmLine(None, "out", "r1", 18, None)
    # Register + offset
    assert gass._extract_identifier_from_line("ldm r1, (r2) + 0x12") == GasmLine(None, "ldm", "r1", "r2", 18)
    assert gass._extract_identifier_from_line("ldm r1, (r2) - 0x12") == GasmLine(None, "ldm", "r1", "r2", 0xEE)
    assert gass._extract_identifier_from_line("stm r1, (r2) + 0x12") == GasmLine(None, "stm", "r1", "r2", 18)
    assert gass._extract_identifier_from_line("inp r1, (r2) + 0x12") == GasmLine(None, "inp", "r1", "r2", 18)
    assert gass._extract_identifier_from_line("out r1, (r2) + 0x12") == GasmLine(None, "out", "r1", "r2", 18)
    # Reference
    assert gass._extract_identifier_from_line("ldm r1, start_val") == GasmLine(None, "ldm", "r1", "start_val", None)
    assert gass._extract_identifier_from_line("ldm r1, (start_val)+0x12") == GasmLine(
        None, "ldm", "r1", "start_val", 18
    )
    assert gass._extract_identifier_from_line("ldm r1, (start_val)-0x12") == GasmLine(
        None, "ldm", "r1", "start_val", 0xEE
    )


def test_extract_identifier_from_line_branch_instructions(gass):
    # Branch instructions
    assert gass._extract_identifier_from_line("bz 12") == GasmLine(None, "bz", 12, None, None)
    assert gass._extract_identifier_from_line("bz -12") == GasmLine(None, "bz", 244, None, None)
    assert gass._extract_identifier_from_line("bnz 12") == GasmLine(None, "bnz", 12, None, None)
    assert gass._extract_identifier_from_line("bnz -12") == GasmLine(None, "bnz", 244, None, None)
    assert gass._extract_identifier_from_line("bc 12") == GasmLine(None, "bc", 12, None, None)
    assert gass._extract_identifier_from_line("bc -12") == GasmLine(None, "bc", 244, None, None)
    assert gass._extract_identifier_from_line("bnc 12") == GasmLine(None, "bnc", 12, None, None)
    assert gass._extract_identifier_from_line("bnc -12") == GasmLine(None, "bnc", 244, None, None)


def test_extract_identifier_from_line_jump_instructions(gass):
    # Jump instructions
    assert gass._extract_identifier_from_line("jmp 0xFC12") == GasmLine(None, "jmp", 64530, None, None)
    assert gass._extract_identifier_from_line("jsb 0xFC12") == GasmLine(None, "jsb", 64530, None, None)


def test_extract_identifier_from_line_misc_instructions(gass):
    # Empty lines, comments and labels
    assert gass._extract_identifier_from_line("") == GasmLine(None, None, None, None, None)
    assert gass._extract_identifier_from_line(";Comment") == GasmLine(None, None, None, None, None)
    assert gass._extract_identifier_from_line(" ; Comment") == GasmLine(None, None, None, None, None)
    assert gass._extract_identifier_from_line("; Comment org 0x1") == GasmLine(None, None, None, None, None)
    assert gass._extract_identifier_from_line(" ; Comment org 0x1") == GasmLine(None, None, None, None, None)
    assert gass._extract_identifier_from_line("label:") == GasmLine("label", None, None, None, None)
    assert gass._extract_identifier_from_line("label: add r0, r1, r2") == GasmLine("label", "add", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("label: bz 0x12") == GasmLine("label", "bz", 18, None, None)
    assert gass._extract_identifier_from_line("label: ldm r1, 0x12") == GasmLine("label", "ldm", "r1", 18, None)
    assert gass._extract_identifier_from_line("label: add r0, r1, r2") == GasmLine("label", "add", "r0", "r1", "r2")
    assert gass._extract_identifier_from_line("label: out r1, (r2) + 0x12") == GasmLine("label", "out", "r1", "r2", 18)

    assert gass._extract_identifier_from_line("org 0x1") == GasmLine(None, "org", 1, None, None)
    assert gass._extract_identifier_from_line("bigdec1024: byte 1024") == GasmLine(
        "bigdec1024", "byte", 1024, None, None
    )
    assert gass._extract_identifier_from_line("null0: byte 0") == GasmLine("null0", "byte", 0, None, None)
    assert gass._extract_identifier_from_line("neg_1: byte -1") == GasmLine("neg_1", "byte", 0xFF, None, None)

    with pytest.raises(GumnutExceptions.InvalidInstruction):
        gass._extract_identifier_from_line("zyxq")


def test_objectcode_comparison_static(gass):
    source_directory = "test/asm_source/"
    output_directory = "test/asm_output/"
    gasm_directory = "test/gasm_output/"
    sample_sources = [
        "sample.gsm",
        "sensor_isr.gsm",
        "polling_loop.gsm",
        "rtc_handler.gsm",
        "jmp.gsm",
        "bz_bnz.gsm",
        "bc_bnc.gsm",
        "ldm.gsm",
    ]  # , 'limits.gsm'

    for source in sample_sources:
        source_name, source_ext = os.path.splitext(source)
        datafile = os.path.join(output_directory, source_name + "_data.dat")
        textfile = os.path.join(output_directory, source_name + "_text.dat")
        gasm_datafile = os.path.join(gasm_directory, source_name + "_data.dat")
        gasm_textfile = os.path.join(gasm_directory, source_name + "_text.dat")

        asm = GumnutAssembler.GumnutAssembler()
        asm.load_asm_source_from_file(source_directory + source)
        asm.assemble()
        asm.create_output_files(datafile=datafile, textfile=textfile)

        # Create md5 hash and compare outputs
        assert generate_md5(textfile) == generate_md5(gasm_textfile)
        assert generate_md5(datafile) == generate_md5(gasm_datafile)


# # TODO:
# def test_objectcode_comparison_dynamic(gass, source):
#     source_directory = "test/asm_source/"
#     output_directory = "test/asm_output/"
#     gasm_directory = "test/gasm_output/"

#     source_name, source_ext = os.path.splitext(source)
#     datafile = os.path.join(output_directory, source_name + "_data.dat")
#     textfile = os.path.join(output_directory, source_name + "_text.dat")
#     gasm_datafile = os.path.join(gasm_directory, source_name + "_data.dat")
#     gasm_textfile = os.path.join(gasm_directory, source_name + "_text.dat")

#     asm = GumnutAssembler.GumnutAssembler()
#     asm.load_asm_source_from_file(source)
#     asm.assemble()
#     asm.create_output_files(datafile=datafile, textfile=textfile)

#     # TODO:
#     # Call gasm assembler subprocess.run(['java', '-classpath', 'test/gasm/Gasm.jar;test/gasm/antlr.jar;test/gasm/',
#     # 'Gasm', source_directory + source, '-t','test/gasm_output/'+source_name+'_text.dat',
#     #'-d','test/gasm_output/'+source_name+'_data.dat'],
#     # shell=True, check=True)

#     # Create md5 hash and compare outputs
#     # assert generate_md5(textfile) == generate_md5(gasm_textfile)
#     # assert generate_md5(datafile) == generate_md5(gasm_datafile)
#     pass


def test_get_register_number(gass):
    assert gass._get_register_number(None) == -1
    assert gass._get_register_number("r0") == 0
    assert gass._get_register_number("r2") == 2
    assert gass._get_register_number("r1024") == 1024  # Muss False liefern
    assert gass._get_register_number("register0") == -1
    assert gass._get_register_number("varname") == -1
    assert gass._get_register_number("0x12") == -1
    assert gass._get_register_number("12") == -1
    assert gass._get_register_number(12) == -1


def test_check_if_immedinstr(gass):
    assert not gass._check_if_immed_instr("r2")
    assert not gass._check_if_immed_instr("register0")
    assert not gass._check_if_immed_instr("varname")
    assert gass._check_if_immed_instr(18)
    assert gass._check_if_immed_instr(12)


def test_check_operand_for_reference(gass):
    assert not gass._check_operand_for_reference(None)
    assert gass._check_operand_for_reference("label")
    assert gass._check_operand_for_reference("value_1")
    assert not gass._check_operand_for_reference("r0")
    assert not gass._check_operand_for_reference("r1")
    assert not gass._check_operand_for_reference("0x12")
    assert not gass._check_operand_for_reference("0b1101")
    assert not gass._check_operand_for_reference("22")


def test_get_reference(gass):
    assert not gass._get_reference(None)
    assert not gass._get_reference("label")
    assert not gass._get_reference("value_1")
    assert gass.NeedSecondRun
    assert not gass._get_reference("r0")
    assert not gass._get_reference("r1")
    assert not gass._get_reference("0x12")
    assert not gass._get_reference("0b1101")
    assert not gass._get_reference("22")
    # ..


def test_assemble_source_line_arithmetic_instructions(gass):
    # Arithemtic and logical instructions
    # Register access
    assert gass._assemble_source_line(GasmLine(None, "add", "r1", "r2", "r3")) == 0x38A60
    assert gass._assemble_source_line(GasmLine(None, "addc", "r1", "r2", "r3")) == 0x38A61
    assert gass._assemble_source_line(GasmLine(None, "sub", "r1", "r2", "r3")) == 0x38A62
    assert gass._assemble_source_line(GasmLine(None, "subc", "r1", "r2", "r3")) == 0x38A63
    assert gass._assemble_source_line(GasmLine(None, "and", "r1", "r2", "r3")) == 0x38A64
    assert gass._assemble_source_line(GasmLine(None, "or", "r1", "r2", "r3")) == 0x38A65
    assert gass._assemble_source_line(GasmLine(None, "xor", "r1", "r2", "r3")) == 0x38A66
    assert gass._assemble_source_line(GasmLine(None, "mask", "r1", "r2", "r3")) == 0x38A67
    assert gass._assemble_source_line(GasmLine(None, "add", "r8", "r9", "r10")) == 248128

    # Immediate access
    assert gass._assemble_source_line(GasmLine(None, "add", "r1", "r2", 0x12)) == 0xA12
    assert gass._assemble_source_line(GasmLine(None, "addc", "r1", "r2", 0x12)) == 0x4A12
    assert gass._assemble_source_line(GasmLine(None, "sub", "r1", "r2", 0x12)) == 0x8A12
    assert gass._assemble_source_line(GasmLine(None, "subc", "r1", "r2", 0x12)) == 0xCA12
    assert gass._assemble_source_line(GasmLine(None, "and", "r1", "r2", 0x12)) == 0x10A12
    assert gass._assemble_source_line(GasmLine(None, "or", "r1", "r2", 0x12)) == 0x14A12
    assert gass._assemble_source_line(GasmLine(None, "xor", "r1", "r2", 0x12)) == 0x18A12
    assert gass._assemble_source_line(GasmLine(None, "mask", "r1", "r2", 0x12)) == 0x1CA12


def test_assemble_source_line_shift_instructions(gass):
    # Shift instructions
    assert gass._assemble_source_line(GasmLine(None, "shl", "r1", "r2", 0x12)) == 0x30A40
    assert gass._assemble_source_line(GasmLine(None, "shr", "r1", "r2", 0x12)) == 0x30A41
    assert gass._assemble_source_line(GasmLine(None, "rol", "r1", "r2", 0x12)) == 0x30A42
    assert gass._assemble_source_line(GasmLine(None, "ror", "r1", "r2", 0x12)) == 0x30A43


def test_assemble_source_line_memory_io_instructions(gass):
    # Memory and I/O instructions
    # Direct offset
    assert gass._assemble_source_line(GasmLine(None, "ldm", "r1", 0x12, None)) == 0x20812
    assert gass._assemble_source_line(GasmLine(None, "stm", "r1", 0x12, None)) == 0x24812
    assert gass._assemble_source_line(GasmLine(None, "inp", "r1", 0x12, None)) == 0x28812
    assert gass._assemble_source_line(GasmLine(None, "out", "r1", 0x12, None)) == 0x2C812
    # Register + offset
    assert gass._assemble_source_line(GasmLine(None, "ldm", "r1", "r2", 0x12)) == 0x20A12
    assert gass._assemble_source_line(GasmLine(None, "stm", "r1", "r2", 0x12)) == 0x24A12
    assert gass._assemble_source_line(GasmLine(None, "inp", "r1", "r2", 0x12)) == 0x28A12
    assert gass._assemble_source_line(GasmLine(None, "out", "r1", "r2", 0x12)) == 0x2CA12


def test_assemble_source_line_branch_instructions(gass):
    # Branch instructions
    assert gass._assemble_source_line(GasmLine(None, "bz", 0x00, None, None)) == 0x3E0FF
    assert gass._assemble_source_line(GasmLine(None, "bz", 0x01, None, None)) == 0x3E000
    assert gass._assemble_source_line(GasmLine(None, "bz", 0x80, None, None)) == 0x3E07F
    gass.InstrMemPointer = 0x10
    assert gass._assemble_source_line(GasmLine(None, "bz", 0x00, None, None)) == 0x3E0EF
    assert gass._assemble_source_line(GasmLine(None, "bz", 0x01, None, None)) == 0x3E0F0
    assert gass._assemble_source_line(GasmLine(None, "bz", 0x80, None, None)) == 0x3E06F
    gass.InstrMemPointer = 0x00
    assert gass._assemble_source_line(GasmLine(None, "bnz", 0x00, None, None)) == 0x3E4FF
    assert gass._assemble_source_line(GasmLine(None, "bnz", 0x01, None, None)) == 0x3E400
    assert gass._assemble_source_line(GasmLine(None, "bnz", 0x80, None, None)) == 0x3E47F
    gass.InstrMemPointer = 0x10
    assert gass._assemble_source_line(GasmLine(None, "bnz", 0x00, None, None)) == 0x3E4EF
    assert gass._assemble_source_line(GasmLine(None, "bnz", 0x01, None, None)) == 0x3E4F0
    assert gass._assemble_source_line(GasmLine(None, "bnz", 0x80, None, None)) == 0x3E46F
    gass.InstrMemPointer = 0x00
    assert gass._assemble_source_line(GasmLine(None, "bc", 0x00, None, None)) == 0x3E8FF
    assert gass._assemble_source_line(GasmLine(None, "bc", 0x01, None, None)) == 0x3E800
    assert gass._assemble_source_line(GasmLine(None, "bc", 0x80, None, None)) == 0x3E87F
    gass.InstrMemPointer = 0x10
    assert gass._assemble_source_line(GasmLine(None, "bc", 0x00, None, None)) == 0x3E8EF
    assert gass._assemble_source_line(GasmLine(None, "bc", 0x01, None, None)) == 0x3E8F0
    assert gass._assemble_source_line(GasmLine(None, "bc", 0x80, None, None)) == 0x3E86F
    gass.InstrMemPointer = 0x00
    assert gass._assemble_source_line(GasmLine(None, "bnc", 0x00, None, None)) == 0x3ECFF
    assert gass._assemble_source_line(GasmLine(None, "bnc", 0x01, None, None)) == 0x3EC00
    assert gass._assemble_source_line(GasmLine(None, "bnc", 0x80, None, None)) == 0x3EC7F
    gass.InstrMemPointer = 0x10
    assert gass._assemble_source_line(GasmLine(None, "bnc", 0x00, None, None)) == 0x3ECEF
    assert gass._assemble_source_line(GasmLine(None, "bnc", 0x01, None, None)) == 0x3ECF0
    assert gass._assemble_source_line(GasmLine(None, "bnc", 0x80, None, None)) == 0x3EC6F


def test_assemble_source_line_jump_instructions(gass):
    # Jump instructions
    assert gass._assemble_source_line(GasmLine(None, "jmp", 0x00, None, None)) == 0x3C000
    assert gass._assemble_source_line(GasmLine(None, "jmp", 0xFFF, None, None)) == 0x3CFFF
    assert gass._assemble_source_line(GasmLine(None, "jmp", 0xFFFF, None, None)) == 0x3CFFF
    assert gass._assemble_source_line(GasmLine(None, "jsb", 0x00, None, None)) == 0x3D000
    assert gass._assemble_source_line(GasmLine(None, "jsb", 0xFFF, None, None)) == 0x3DFFF
    assert gass._assemble_source_line(GasmLine(None, "jsb", 0xFFFF, None, None)) == 0x3DFFF


def test_assemble_source_line_misc_instructions(gass):
    # Misc instructions
    assert gass._assemble_source_line(GasmLine(None, "ret", None, None, None)) == 0x3F000
    assert gass._assemble_source_line(GasmLine(None, "reti", None, None, None)) == 0x3F100
    assert gass._assemble_source_line(GasmLine(None, "enai", None, None, None)) == 0x3F200
    assert gass._assemble_source_line(GasmLine(None, "disi", None, None, None)) == 0x3F300
    assert gass._assemble_source_line(GasmLine(None, "wait", None, None, None)) == 0x3F400
    assert gass._assemble_source_line(GasmLine(None, "stby", None, None, None)) == 0x3F500

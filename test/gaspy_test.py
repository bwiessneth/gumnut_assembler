import os
import subprocess

from helper import generate_md5


def capture(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_gaspy_cli_arg_help():
    command = ["gaspy", "-h"]
    out, err, exitcode = capture(command)
    assert exitcode == 0

    command = ["gaspy", "--help"]
    out, err, exitcode = capture(command)
    assert exitcode == 0


def test_gaspy_cli_arg_version():
    command = ["gaspy", "-v"]
    out, err, exitcode = capture(command)
    assert exitcode == 0

    command = ["gaspy", "--version"]
    out, err, exitcode = capture(command)
    assert exitcode == 0



def test_gaspy_cli_objectcode_comparison_static():
    source_directory = "test/asm_source/"
    output_directory = "test/gaspy_output/"
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
    ]

    for source in sample_sources:
        source_name, source_ext = os.path.splitext(source)
        datafile = os.path.join(output_directory, source_name + "_data.dat")
        textfile = os.path.join(output_directory, source_name + "_text.dat")
        gasm_datafile = os.path.join(gasm_directory, source_name + "_data.dat")
        gasm_textfile = os.path.join(gasm_directory, source_name + "_text.dat")

        command = ["gaspy", source_directory + source, "-o", output_directory]
        out, err, exitcode = capture(command)
        assert exitcode == 0

        # Create md5 hash and compare outputs
        assert generate_md5(textfile) == generate_md5(gasm_textfile)
        assert generate_md5(datafile) == generate_md5(gasm_datafile)

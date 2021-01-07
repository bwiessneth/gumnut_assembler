import setuptools
import codecs
import os.path


# Taken from pip itself (https://github.com/pypa/pip/blob/master/setup.py#L11)
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


with open("README.rst", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="gumnut-assembler",
    version=get_version("gumnut_assembler/__init__.py"),
    author="Benjamin Wiessneth",
    author_email="b.wiessneth@gmail.com",
    description="Gumnut Assembler written in Python",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/bwiessneth/gumnut-assembler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["gumnut-assembler = gumnut_assembler.assembler:main"]},
)

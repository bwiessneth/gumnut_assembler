[![tests](https://github.com/bwiessneth/gaspy/workflows/tests/badge.svg)](https://github.com/bwiessneth/gaspy/actions?query=workflow%3Atests)
[![Documentation Status](https://readthedocs.org/projects/gumnut-assembler/badge/?version=latest)](https://gumnut-assembler.readthedocs.io/en/latest/?badge=latest)



# gaspy

Gumnut Assembler written in Python.



## Motivation

*gaspy* is a python-based implementation of Peter Ashenden's Gumnut assembler *gasm* which assembles the objectcode to be used with his 8-bit soft-core *Gumnut*.
For more information refer to *The Designers Guide to VHDL* https://www.sciencedirect.com/book/9780120887859/the-designers-guide-to-vhdl



## Status

As of now *gaspy* support all *gasm* instructions and assembles the same objectcode as *gasm*.

The only (known) limitation is the implementation of the ```equ``` directive in conjunction with ascii values.



# Documentation 

Please refer to https://gaspy.readthedocs.io/en/latest/

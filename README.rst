.. image:: https://github.com/bwiessneth/gumnut-assembler/workflows/tests/badge.svg
   :target: https://github.com/bwiessneth/gumnut-assembler/actions?query=workflow%3Atests
   :alt: tests status

.. image:: https://readthedocs.org/projects/gumnut_assembler/badge/?version=latest
   :target: https://gumnut_assembler.readthedocs.io/en/latest/?badge=latest
   :alt: docs status



gumnut_assembler
################

Gumnut Assembler written in Python.

*gumnut_assembler* is a python-based implementation of Peter Ashenden's Gumnut assembler *gasm* which assembles the machine code to
be used with his 8-bit soft-core *Gumnut*. For more information refer to *The Designers Guide to VHDL*
https://www.sciencedirect.com/book/9780120887859/the-designers-guide-to-vhdl

*gumnut_assembler* was forked from my very first implementation created at the laboratory for digital engineering at the University of
Applied Sciences Augsburg back in 2015.

As of now, *gumnut_assembler* supports all *gasm* instructions and assembles the same machine code as *gasm*.



Documentation
*************

Please refer to https://gumnut-assembler.readthedocs.io/en/latest/



Changelog
*********

2.0.0
=====

Changed
-------

-  Enforced proper module names and naming convention



1.0.3
=====

Fixed
-----

- Typos in README
- Making sure ``tox`` is using the package, not the source files for testing
- Updated development docs



1.0.2
=====

Changed
-------

- The README file is now also using reStructuredText format

Fixed
-----

- ``equ`` directive is now working for ascii values (e.g. ``char_a: equ 'a'``)



1.0.1
=====

Added
-----

-  Proper CLI for standalone usage
-  Documentation (still in progress, though)
-  Introduced ``tox`` for handling testing, build, and publishing tasks
-  Introduced Github Actions for automated testing

Changed
-------

-  Replaced ``nosetest`` with ``pytest`` as the choice for unit and
   integration testing
-  Updated the existing tests for ``pytest``

Fixed
-----

-  Module imports were fixed



1.0.0
=====

The initial version which was *gumnut_assembler* was forked from.

.. image:: https://github.com/bwiessneth/gaspy/workflows/tests/badge.svg
   :target: https://github.com/bwiessneth/gaspy/actions?query=workflow%3Atests
   :alt: tests status

.. image:: https://readthedocs.org/projects/gaspy/badge/?version=latest
   :target: https://gaspy.readthedocs.io/en/latest/?badge=latest
   :alt: docs status



gaspy
=====

Gumnut Assembler written in Python.

*gaspy* is a python-based implementation of Peter Ashenden's Gumnut assembler *gasm* which assembles the machine code to
be used with his 8-bit soft-core *Gumnut*. For more information refer to *The Designers Guide to VHDL*
https://www.sciencedirect.com/book/9780120887859/the-designers-guide-to-vhdl

*gaspy* was forked from my very first implementation created at the Laboratory for digital engineering at University of
Applied Sciences in 2015.

As of now *gaspy* support all *gasm* instructions and assembles the same machine code as *gasm*.

Documentation
=============

Please refer to https://gaspy.readthedocs.io/en/latest/

Changelog
=========

1.0.2
-----

Changed
~~~~~~~
- The README file is now also using reStructuredText format

Fixed
~~~~~

- ``equ`` directive is now working for ascii values (e.g. ``char_a: equ 'a'``)



1.0.1
-----

Added
~~~~~

-  Proper CLI for standalone usage
-  Documentation (still in progress, though)
-  Introduced ``tox`` for handling testing, build, and publishing tasks
-  Introduced Github Actions for automated testing

Changed
~~~~~~~

-  Replaced ``nosetest`` with ``pytest`` as the choice for unit and
   integration testing
-  Updated the existing tests for ``pytest``

Fixed
~~~~~

-  Module imports were fixed



1.0.0
-----

The initial version which was *gaspy* was forked from.


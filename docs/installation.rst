============
Installation
============

Install the package with pip::

$ pip install GumnutAssembler


After that the Gumnut assembler executable ``gaspy`` should be accessible from anywhere on your machine.
Check if the installation was successful by calling it with the ``-v`` or ``--version`` argument:

.. code-block:: console

    [john@desktop ~]$ gaspy --version
    gaspy 1.0.0



.. code-block:: console

	[john@desktop ~]$ gaspy --help
	usage: gaspy [-h] [-o OUT_DIR] [-j] [-v] source
	Gumnut assembler written in Python

	positional arguments:
	source                Gumnut assembler source files

	optional arguments:
	-h, --help            show this help message and exit
	-o OUT_DIR, --out-dir OUT_DIR
	                      Directory where the output files should be placed
	-j, --json            Enable JSON output
	-v, --version         show the version number and exit
	

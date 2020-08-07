=====
Usage
=====

See the possible arguments and options by calling *gaspy* with the ``-h`` or ``--help`` argument:

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



Assemble from source
--------------------

Assuming you have source file ``jmp.gsm`` located on your desktop you can assemble it by passing it to *gaspy*

.. code-block:: console
	
	[john@desktop ~]$ gaspy jmp.gsm

Per default gaspy always returns two files:

* The text file (``jmp_text.dat``) containing assembled the instruction memory
* The data file (``jmp_data.dat``) containing assembled the data memory

Those files are always placed in the same directory the source file is located.



Output directory
----------------

You can tell *gaspy* to place the output files into another directory by supplying the ``-o``/``--output`` argument and the desired path:

.. code-block:: console

	[john@desktop ~]$ gaspy jmp.gsm -o asm_files



JSON output
-----------

Initially meant to be used as a supplement for the GumnutSimulator, there is an option to enable JSON output. Enable it by passing the ``-j``/``--json`` argument.
Using this will return the instruction and data memory as a JSON object to ``stdout``. If this option is enabled no other output files will be generated.

.. code-block:: console
	
	[john@desktop ~]$ gaspy jmp.gsm -j
	{"text": [245778, 0, 0, 0, 0, 0, 0, 0, 2305, 245781, 2305, 2305, 245776, 35073, ... ],
	 "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ... ]}


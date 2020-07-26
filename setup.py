import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GumnutAssembler", # Replace with your own username
    version="1.0.0",
    author="Benjamin Wiessneth",
    author_email="b.wiessneth@gmail.com",
    description="Gumnut Assembler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bwiessneth/gumnut_assembler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",        
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={'console_scripts': [
        'GumnutAssembler = GumnutAssembler.GumnutAssembler:main',
    ]}
)
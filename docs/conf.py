# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'gumnut-assembler'
copyright = '2020, Benjamin Wießneth'
author = 'Benjamin Wießneth'

# The full version, including alpha/beta/rc tags
release = version = '3.0.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.extlinks',
    'autoapi.extension',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'



# -- Options for HTML output -------------------------------------------------

import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'display_version': False,
    'navigation_depth': 2,
    'collapse_navigation': True
}
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_last_updated_fmt = '%b %d, %Y'
html_context = {
    'css_files': [],
    'display_github': True,
    'github_user': 'bwiessneth',
    'github_repo': 'gumnut-assembler',
    'github_version': 'master',
    'conf_py_path': '/docs/'
}
html_show_copyright = False



# -- Options for autoapi -----------------------------------------------------

autoapi_dirs = ['../gumnut_assembler']

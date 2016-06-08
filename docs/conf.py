
import sys
import os

extensions = [
    'sphinx.ext.todo',
]

source_suffix = '.txt'

master_doc = 'index'

### part to update ###################################
project = u'domogik-plugin-body'
copyright = u'2016, Fritz SMH'
version = '1.0'
release = version
######################################################

pygments_style = 'sphinx'

html_theme = 'default'
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'domogik-plugin-body'

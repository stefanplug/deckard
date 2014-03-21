import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "deckard-node",
    license = "GPLv3",
    author = "Stefan Plug, Sean Rijs",
    url = "https://github.com/stefanplug/deckard",
    version = "0.3.0",
    scripts = ['deckard-node'],
    packages = ['deckard-node'],
    package_dir = {'deckard-node': 'src'},
    package_data = {'deckard-node': ['etc/*']},
)

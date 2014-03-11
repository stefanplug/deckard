import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "deckard",
    license = "GPLv3",
    author = "Stefan Plug, Sean Rijs",
    url = "https://github.com/stefanplug/deckard",
    version = "0.1.1",
    scripts=['deckard-client.py', 'deckard-server.py'],
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.cfg'],
    },
)

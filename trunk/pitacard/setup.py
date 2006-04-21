#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='pitacard',
      version='0.7',
      description='Leitner-method flash card system',
      author='Austin Bingham',
      author_email='austin.bingham@gmail.com',
      url='http://austin.bingham.googlepages.com/pitacard',
      packages=['pitacard'],
      scripts=['scripts/pitacard'],
      package_data={'pitacard' : [os.path.join('glade','pitacard.glade')]},
     )

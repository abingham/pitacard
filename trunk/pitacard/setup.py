#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='pitacard',
      version='0.9',
      description='Leitner-method flash card system',
      author='Austin Bingham',
      author_email='austin.bingham@gmail.com',
      url='http://austin.bingham.googlepages.com/pitacard',
      license='GPL',
      packages=['pitacard'],
      scripts=['scripts/pitacard'],
      package_data={'pitacard' : [os.path.join('glade','pitacard.glade'),
                                  os.path.join('glade','pita.jpg'),
				  'INSTALL',
 				  'AUTHORS']},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: X11 Applications :: GTK',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: POSIX',
                   'Programming Language :: Python',
                   'Topic :: Education'
                   ]
     )

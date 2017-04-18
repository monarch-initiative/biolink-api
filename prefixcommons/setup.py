import os
import re
import subprocess

import setuptools

directory = os.path.dirname(os.path.abspath(__file__))

# version
init_path = os.path.join(directory, 'prefixcommons', '__init__.py')
with open(init_path) as read_file:
    text = read_file.read()
version = '0.1.4'

# long_description
readme_path = os.path.join(directory, 'README.md')
try:
    # copied from dhimmel/obonet:
    # Try to create an reStructuredText long_description from README.md
    args = 'pandoc', '--from', 'markdown', '--to', 'rst', readme_path
    long_description = subprocess.check_output(args)
    long_description = long_description.decode()
except Exception as error:
    # Fallback to markdown (unformatted on PyPI) long_description
    print('README.md conversion to reStructuredText failed. Error:')
    print(error)
    with open(readme_path) as read_file:
        long_description = read_file.read()


setuptools.setup(
    name='prefixcommons',
    version=version,
    author='Chris Mungall',
    author_email='cmungall@gmail.com',
    url='https://github.com/biolink-api/prefixcommons',
    description='Library for working prefixcommons.org CURIEs',
    long_description=long_description,
    license='BSD3',
    packages=['prefixcommons'],

    keywords='ontology graph obo owl sparql networkx network',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],

    # Dependencies
    install_requires=[
        'pyyaml',
        'requests',
        'cachier'
    ]
)

#!/usr/bin/env python3
"""
setup.py file for atmosphere package
"""

import sys
from setuptools import setup, Extension, find_packages

# Compiler options
if sys.platform == "darwin":
    extra_compile_args = [
        "-fno-strict-aliasing",
        "-fno-common",
    ]
else:
    extra_compile_args = ["-O2"]

cdisort = Extension(
    name="atmosphere.rt._cdisort",
    sources=[
        "src/cdisort.i",
        "src/cdisort.c",
        "src/locate.c",
        #"src/disotest.c",
    ],
    include_dirs=["src"],
    swig_opts=[
        "-relativeimport",
        "-outdir", "atmosphere/rt",
    ],
    extra_compile_args=extra_compile_args,
    libraries=["m"],
)

setup(name='atmosphere',
      version='0.0.4',
      description='Radiative transfer model for planetary atmospheres.',
      install_requires=['numpy','scipy'],
      author='Mate Adamkovics',
      author_email='mate@berkeley.edu',
      url='http://astro.berkeley.edu:~/madamkov/',
      packages=['atmosphere','atmosphere/rt'],
      ext_modules=[cdisort]
      )

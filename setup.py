#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    ##  don't do this unless you want a globally visible script
    # scripts=['bin/myscript'],
    packages=['lwr_project_creator'],
    package_dir={'': 'src'},
    scripts=['scripts/lwr_create_pkg']
)

setup(**d)

# from setuptools import setup,find_packages
# from lwr_project_creator.pkg_creator import __version__
#
# setup(name='lwr_project_creator',
#       install_requires=['distribute'],
#       version=__version__,
#       description='LWR project generator for the KUKA LWR4+ at ISIR',
#       author='Antoine Hoarau',
#       author_email='hoarau.robotics@gmail.com',
#       url='https://github.com/kuka-isir/lwr_project_creator',
#       requires=['gtk'],
#       license="GPL",
#       scripts=["lwr_create_pkg"],
#       packages=find_packages(),
#       include_package_data=True,
#      )

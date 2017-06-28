#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

# Allow trove classifiers in previous python versions
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

from amdtemp import __version__ as version

def requireModules(moduleNames=None):
    import re
    if moduleNames is None:
        moduleNames = []
    else:
        moduleNames = moduleNames

    commentPattern = re.compile(r'^\w*?#')
    moduleNames.extend(
        filter(lambda line: not commentPattern.match(line),
            open('requirements.txt').readlines()))

    return moduleNames

setup(
    name='amdtemp',
    version=version,

    author='Micael Bergeron',
    author_email='micaelbergeron@gmail.com',

    description='amdtemp',
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers'
    ],

    entry_points = {
        'console_scripts': ['amdtemp = amdtemp.amdtemp:main']
    },

    packages=find_packages(exclude=['test*']),

    install_requires=requireModules([
        'anyconfig',
        'statsd',
        'toml'
    ]),

    test_suite='amdtemp'
)

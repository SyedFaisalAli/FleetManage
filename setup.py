import os
from setuptools import setup, find_packages

setup(
    name='netassist',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'netassist=netmcp.server:main',
        ],
    },
    package_data={
        'netassist': ['static/**/*']
    }
)
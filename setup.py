# -*- coding:utf-8 -*-
import os

from setuptools import find_packages, setup

from setup_commands.clean import CleanCommand
from setup_commands.protoc import ProtocCommand
from setup_commands.pylint import PylintCommand

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


with open('README.md') as fh:
    README = fh.read()


setup(
    name='schematics-proto3',
    use_scm_version=True,
    description='Schematics extension for handling protobuf 3 messages.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/mlga/schematics-proto3',
    author='mlga',
    author_email='github@mlga.io',
    license='MIT',
    keywords='protobuf schematics validation serialization input',
    setup_requires=[
        'pytest-runner~=5.1',
        'setuptools_scm~=3.3',
    ],
    install_requires=[
        'schematics~=2.1',
        'protobuf~=3.9',
    ],
    tests_require=[
        'pytest~=5.0',
        'pytest-cov~=2.7',
        'pytest-html~=1.20',
    ],
    extras_require={
        'develop': [
            'pylint~=2.3',
            'pytest~=5.0',
            'pytest-cov~=2.7',
            'pytest-html~=1.20',
            'Sphinx==3.0.1',
            'sphinx-rtd-theme==0.4.3',
        ],
    },
    packages=find_packages(exclude=['tests*', 'examples*']),
    include_package_data=True,
    platforms='any',
    zip_safe=False,
    cmdclass={
        'pylint': PylintCommand,
        'clean': CleanCommand,
        'protoc': ProtocCommand,
    },
    python_requires='>=3.7',
)

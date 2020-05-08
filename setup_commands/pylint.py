# -*- coding:utf-8 -*-
import distutils
import subprocess
import sys


class PylintCommand(distutils.cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'Run pyint linter.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        command = [
            'pylint', '--rcfile=toolscfg/pylintrc',
            # Those three are only cluttering the results, will be fixed some day.
            '--disable', 'missing-module-docstring',
            '--disable', 'missing-function-docstring',
            '--disable', 'missing-class-docstring',
            '--disable', 'fixme',
            'schematics_proto3',
        ]

        self.announce(f'Running command: {" ".join(command)}', level=distutils.log.INFO)

        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as ex:
            sys.exit(ex.returncode)

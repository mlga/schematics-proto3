# -*- coding:utf-8 -*-
import distutils
import subprocess
import sys


class ProtocCommand(distutils.cmd.Command):
    """A custom command to clean build / test artifacts."""

    description = 'Compile protoc definitions.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        commands = (
            ['protoc', '-I', '.', '--python_out', '.', 'tests/schematics_proto3_tests.proto'],
        )

        for command in commands:
            self.announce(f'Running command: {" ".join(command)}', level=distutils.log.INFO)
            try:
                subprocess.check_call(command)
            except subprocess.CalledProcessError as ex:
                sys.exit(ex.returncode)

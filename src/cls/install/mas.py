# -*- coding: utf-8 -*-

import sys
import traceback

from macdaily.cmd.install import InstallCommand
from macdaily.core.mas import MasCommand
from macdaily.util.tools.misc import date
from macdaily.util.tools.print import print_info, print_scpt
from macdaily.util.tools.script import sudo

if sys.version_info[:2] <= (3, 4):
    import subprocess32 as subprocess
else:
    import subprocess


class MasInstall(MasCommand, InstallCommand):

    def _parse_args(self, namespace):
        self._force = namespace.get('force', False)

        self._quiet = namespace.get('quiet', False)
        self._verbose = namespace.get('verbose', False)
        self._yes = namespace.get('yes', False)

        self._install_opts = namespace.get('install', str()).split()

    def _proc_install(self, path):
        text = f'Installing specified {self.desc[1]}'
        print_info(text, self._file, redirect=self._qflag)

        argv = [path, 'install']
        if self._force:
            argv.append('--force')
        argv.extend(self._install_opts)
        argv.append('')

        for package in self._var__temp_pkgs:
            try:
                int(package)
            except ValueError:
                argv[1] = 'lucky'
            argv[-1] = package
            print_scpt(' '.join(argv), self._file, redirect=self._qflag)
            if sudo(argv, self._file, self._password, timeout=self._timeout,
                    redirect=self._qflag, verbose=self._vflag):
                self._fail.append(package)
            else:
                self._pkgs.append(package)
        del self._var__temp_pkgs

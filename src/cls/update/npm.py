# -*- coding: utf-8 -*-

import os
import traceback

from macdaily.cmd.update import UpdateCommand
from macdaily.core.npm import NpmCommand
from macdaily.util.const import bold, reset
from macdaily.util.misc import date, print_info, print_scpt, print_text, sudo

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


class NpmUpdate(NpmCommand, UpdateCommand):

    def _parse_args(self, namespace):
        self._no_cleanup = namespace.pop('no_cleanup', False)

        self._all = namespace.pop('all', False)
        self._quiet = namespace.pop('quiet', False)
        self._verbose = namespace.pop('verbose', False)
        self._yes = namespace.pop('yes', False)

        self._logging_opts = namespace.pop('logging', str()).split()
        self._update_opts = namespace.pop('update', str()).split()

    def _check_pkgs(self, path):
        text = f'Listing installed {self.desc[1]}'
        print_info(text, self._file, redirect=self._vflag)

        argv = [path, 'list', '--global', '--parseable']
        args = ' '.join(argv)
        print_scpt(args, self._file, redirect=self._vflag)
        with open(self._file, 'a') as file:
            file.write(f'Script started on {date()}\n')
            file.write(f'command: {args!r}\n')

        try:
            proc = subprocess.check_output(argv, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print_text(traceback.format_exc(), self._file, redirect=self._vflag)
            _real_pkgs = set()
        else:
            context = proc.decode()
            print_text(context, self._file, redirect=self._vflag)

            _list_pkgs = list()
            for line in context.strip().split('\n'):
                _, name = os.path.split(line)
                _list_pkgs.append(name)
            _real_pkgs = set(_list_pkgs)
        finally:
            with open(self._file, 'a') as file:
                file.write(f'Script done on {date()}\n')

        text = 'Checking existence of specified packages'
        print_info(text, self._file, redirect=self._vflag)

        _temp_pkgs = list()
        _lost_pkgs = list()
        for package in self._packages:
            if package in _real_pkgs:
                _temp_pkgs.append(package)
            else:
                _lost_pkgs.append(package)
        self._lost.extend(_lost_pkgs)

        self._tmp_real_pkgs = set(_real_pkgs)
        self._tmp_lost_pkgs = set(_lost_pkgs)
        self._tmp_temp_pkgs = set(_temp_pkgs)

    def _check_list(self, path):
        argv = [path, 'outdated']
        argv.extend(self._logging_opts)
        argv.append('--no-parseable')
        argv.append('--no-json')
        argv.append('--global')

        text = f'Checking outdated {self.desc[1]}'
        print_info(text, self._file, redirect=self._vflag)

        args = ' '.join(argv)
        print_scpt(args, self._file, redirect=self._vflag)
        with open(self._file, 'a') as file:
            file.write(f'Script started on {date()}\n')
            file.write(f'command: {args!r}\n')

        try:
            proc = subprocess.check_output(argv, stderr=subprocess.DEVNULL)
        except subprocess.SubprocessError:
            print_text(traceback.format_exc(), self._file, redirect=self._vflag)
            self._tmp_temp_pkgs = set()
        else:
            context = proc.decode()
            print_text(context, self._file, redirect=self._vflag)

            _temp_pkgs = list()
            for line in context.strip().split('\n')[1:]:
                name, _, want, _ = line.split(maxsplit=3)
                _temp_pkgs.append(f'{name}@{want}')
            self._tmp_temp_pkgs = set(_temp_pkgs)
        finally:
            with open(self._file, 'a') as file:
                file.write(f'Script done on {date()}\n')

    def _proc_update(self, path):
        argv = [path, 'install']
        if self._quiet:
            argv.append('--quiet')
        if self._verbose:
            argv.append('--verbose')
        argv.extend(self._update_opts)
        argv.append('--global')

        text = f'Upgrading outdated {self.desc[1]}'
        print_info(text, self._file, redirect=self._qflag)

        argc = ' '.join(argv)
        for package in self._tmp_temp_pkgs:
            args = f'{argc} {package}'
            print_scpt(args, self._file, redirect=self._qflag)
            if sudo(args, self._file, askpass=self._askpass,
                    timeout=self._timeout, redirect=self._qflag):
                self._fail.append(package)
            else:
                self._pkgs.append(package)
        del self._tmp_temp_pkgs

# -*- coding: utf-8 -*-

import os
import shutil
import sys
import traceback

from macdaily.cmd.update.command import UpdateCommand
from macdaily.util.colours import blush, bold, flash, purple, red, reset, under
from macdaily.util.tools import script

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


class NpmUpdate(UpdateCommand):

    @property
    def mode(self):
        return 'npm'

    @property
    def name(self):
        return 'Node.js'

    @property
    def desc(self):
        return ('node module', 'node modules')

    def _check_exec(self):
        self.__exec_path = shutil.which('npm')
        flag = (self.__exec_path is None)
        if flag:
            print(f'macdaily-update: {blush}{flash}npm{reset}: command not found', file=sys.stderr)
            print(f'macdaily-update: {red}npm{reset}: you may download Node.js from '
                  f'{purple}{under}https://nodejs.org/{reset}\n')
        return flag

    def _parse_args(self, namespace):
        self._all = namespace.pop('all', False)
        self._cleanup = namespace.pop('cleanup', True)
        self._quiet = namespace.pop('quiet', False)
        self._show_log = namespace.pop('show_log', False)
        self._verbose = namespace.pop('verbose', False)

        self._logging_opts = namespace.pop('logging', str()).split()
        self._update_opts = namespace.pop('update', str()).split()

    def _loc_exec(self):
        self._exec = {self.__exec_path}
        del self.__exec_path

    def _check_pkgs(self, path):
        args = [path, 'list', '--global', '--parseable']
        try:
            proc = subprocess.check_output(args, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            _real_pkgs = set()
        else:
            _list_pkgs = list()
            for line in proc.decode().split('\n'):
                _, name = os.path.split(line)
                _list_pkgs.append(name)
            _real_pkgs = set(_list_pkgs)

        _temp_pkgs = list()
        _lost_pkgs = list()
        for package in self._packages:
            if package in _real_pkgs:
                _temp_pkgs.append(package)
            else:
                _lost_pkgs.append(package)
        self._lost.extend(_lost_pkgs)

        self.__real_pkgs = set(_real_pkgs)
        self.__lost_pkgs = set(_lost_pkgs)
        self.__temp_pkgs = set(_temp_pkgs)

    def _check_list(self, path):
        args = [path, 'outdated', '--global']
        args.extend(self._logging_opts)
        args.append('--no-parseable')
        args.append('--no-json')

        self._log.write(f'+ {" ".join(args)}\n')
        try:
            proc = subprocess.check_output(args, stderr=subprocess.DEVNULL, timeout=self._timeout)
        except subprocess.SubprocessError:
            self._log.write(traceback.format_exc())
            self.__temp_pkgs = set()
        else:
            context = proc.decode()
            self._log.write(context)

            _temp_pkgs = list()
            for line in context.split('\n')[1:]:
                name, _, want, _ = line.split(maxsplit=3)
                _temp_pkgs.append(f'{name}@{want}')
            self.__temp_pkgs = set(_temp_pkgs)
        finally:
            self._log.write('\n')

    def _proc_update(self, path):
        args = [path, 'install']
        if self._quiet:
            args.append('--quiet')
        if self._verbose:
            args.append('--verbose')
        args.extend(self._update_opts)

        argc = ' '.join(args)
        for package in self.__temp_pkgs:
            argv = f'{argc} {package}'
            script(['echo', '-e', f'\n+ {bold}{argv}{reset}'], self._log.name)
            if script(f"yes {self._password} | sudo --stdin --prompt='' {argv}",
                      self._log.name, shell=True, timeout=self._timeout):
                self._fail.append(package)
            else:
                self._pkgs.append(package)
            self._log.write('\n')
        del self.__temp_pkgs

    def _proc_cleanup(self):
        if self._cleanup():
            return

        args = ['npm', 'cleanup']
        if self._verbose:
            args.append('--verbose')
        if self._quiet:
            args.append('--quiet')
        argv = ' '.join(args)
        script(['echo', '-e', f'\n+ {bold}{argv}{reset}'], self._log.name)

        def _cleanup(args):
            if self._verbose:
                args.append('--verbose')
            if self._quiet:
                args.append('--quiet')
            argv = ' '.join(args)
            script(['echo', '-e', f'++ {argv}'], self._log.name)
            script(f'yes {self._password} | sudo --stdin --prompt="" {argv}', self._log.name, shell=True)

        for path in self._exec:
            _cleanup([path, 'dedupe', '--global'])
            _cleanup([path, 'cache', 'clean', '--force'])

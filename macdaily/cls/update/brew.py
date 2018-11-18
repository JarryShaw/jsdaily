# -*- coding: utf-8 -*-

import sys
import time
import traceback

from macdaily.cmd.update import UpdateCommand
from macdaily.core.brew import BrewCommand
from macdaily.util.misc import (date, make_stderr, print_info, print_scpt,
                                print_text, run)

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


class BrewUpdate(BrewCommand, UpdateCommand):

    def _parse_args(self, namespace):
        self._force = namespace.get('force', False)
        self._merge = namespace.get('merge', False)
        self._no_cleanup = namespace.get('no_cleanup', False)

        self._all = namespace.get('all', False)
        self._quiet = namespace.get('quiet', False)
        self._verbose = namespace.get('verbose', False)
        self._yes = namespace.get('yes', False)

        self._logging_opts = namespace.get('logging', str()).split()
        self._update_opts = namespace.get('update', str()).split()

    def _check_list(self, path):
        if self._brew_renew is None or \
                time.time() - self._brew_renew >= 300:
            self._proc_renew(path)
            self._brew_renew = time.time()

        text = 'Checking outdated {}'.format(self.desc[1])
        print_info(text, self._file, redirect=self._vflag)

        argv = [path, 'outdated']
        if self._quiet:
            argv.append('--quiet')
        if self._verbose:
            argv.append('--verbose')
        argv.extend(self._logging_opts)

        args = ' '.join(argv)
        print_scpt(args, self._file, redirect=self._vflag)
        with open(self._file, 'a') as file:
            file.write('Script started on {}\n'.format(date()))
            file.write('command: {!r}\n'.format(args))

        stderr = make_stderr(self._vflag, sys.stderr)
        try:
            proc = subprocess.check_output(argv, stderr=stderr)
        except subprocess.SubprocessError:
            print_text(traceback.format_exc(), self._file, redirect=self._vflag)
            self._var__temp_pkgs = set()
        else:
            context = proc.decode()
            print_text(context, self._file, redirect=self._vflag)

            _temp_pkgs = list()
            for line in filter(None, context.strip().split('\n')):
                _temp_pkgs.append(line.split(maxsplit=1)[0])
            self._var__temp_pkgs = set(_temp_pkgs)
        finally:
            with open(self._file, 'a') as file:
                file.write('Script done on {}\n'.format(date()))

    def _proc_update(self, path):
        text = 'Upgrading outdated {}'.format(self.desc[1])
        print_info(text, self._file, redirect=self._qflag)

        argv = [path, 'upgrade']
        if self._quiet:
            argv.append('--quiet')
        if self._verbose:
            argv.append('--verbose')
        argv.extend(self._update_opts)

        argv.append('')
        for package in self._var__temp_pkgs:
            argv[-1] = package
            print_scpt(' '.join(argv), self._file, redirect=self._qflag)
            if run(argv, self._file, timeout=self._timeout,
                   redirect=self._qflag, verbose=self._vflag):
                self._fail.append(package)
            else:
                self._pkgs.append(package)
        del self._var__temp_pkgs

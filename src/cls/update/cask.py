# -*- coding: utf-8 -*-

import os
import textwrap
import time
import traceback

from macdaily.cmd.update import UpdateCommand
from macdaily.core.cask import CaskCommand
from macdaily.util.const import bold, length, reset
from macdaily.util.misc import date, print_info, print_scpt, print_text, run

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


class CaskUpdate(CaskCommand, UpdateCommand):

    def _parse_args(self, namespace):
        self._exhaust = namespace.pop('exhaust', False)
        self._force = namespace.pop('force', False)
        self._greedy = namespace.pop('greedy', False)
        self._merge = namespace.pop('merge', False)
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

        argv = [path, 'cask', 'list']
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
            _real_pkgs = set(context.split())
            print_text(context, self._file, redirect=self._vflag)
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
        if (self._brew_renew is None or
                time.time() - self._brew_renew >= 300):
            self._proc_renew(path)
            self._brew_renew = time.time()

        if self._exhaust:
            return self._exhaust_check(path)

        text = f'Checking outdated {self.desc[1]}'
        print_info(text, self._file, redirect=self._vflag)

        argv = [path, 'cask', 'outdated']
        if self._quiet:
            argv.append('--quiet')
        if self._verbose:
            argv.append('--verbose')
        if self._greedy:
            argv.append('--greedy')
        argv.extend(self._logging_opts)

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
            for line in context.strip().split('\n'):
                _temp_pkgs.append(line.split(maxsplit=1)[0])
            self._tmp_temp_pkgs = set(_temp_pkgs)
        finally:
            with open(self._file, 'a') as file:
                file.write(f'Script done on {date()}\n')

    def _exhaust_check(self, path):
        text = f'Checking outdated {self.desc[1]} exclusively'
        print_info(text, self._file, redirect=self._vflag)

        argv = ['brew', 'cask', 'outdated', '--exhaust']
        if self._quiet:
            argv.append('--quiet')
        if self._verbose:
            argv.append('--verbose')
        argv.extend(self._logging_opts)
        print_scpt(' '.join(argv), self._file, redirect=self._vflag)

        text = f'Listing installed {self.desc[1]}'
        print_info(text, self._file, redirect=self._vflag)

        argv = [path, 'cask', 'list']
        args = ' '.join(argv)
        print_scpt(args, self._file, redirect=self._vflag)
        with open(self._file, 'a') as file:
            file.write(f'Script started on {date()}\n')
            file.write(f'command: {args!r}\n')

        try:
            proc = subprocess.check_output(argv, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print_text(traceback.format_exc(), self._file, redirect=self._vflag)
            _list_pkgs = set()
        else:
            context = proc.decode()
            _list_pkgs = set(context.split())
            print_text(context, self._file, redirect=self._vflag)
        finally:
            with open(self._file, 'a') as file:
                file.write(f'Script done on {date()}\n')

        text = f'Fetching Homebrew prefix'
        print_info(text, self._file, redirect=self._vflag)

        argv = [path, '--prefix']
        args = ' '.join(argv)
        print_scpt(args, self._file, redirect=self._vflag)
        with open(self._file, 'a') as file:
            file.write(f'Script started on {date()}\n')
            file.write(f'command: {args!r}\n')

        fail = False
        try:
            proc = subprocess.check_output(argv, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print_text(traceback.format_exc(), self._file, redirect=self._vflag)
            self._tmp_temp_pkgs = set()
            fail = True
        else:
            context = proc.decode()
            print_text(context, self._file, redirect=self._vflag)
            prefix = context.strip()
        finally:
            with open(self._file, 'a') as file:
                file.write(f'Script done on {date()}\n')
        if fail:
            return

        text = f'Checking versions of installed {self.desc[1]}'
        print_info(text, self._file, redirect=self._vflag)

        _temp_pkgs = list()
        for cask in _list_pkgs:
            argv = [path, 'cask', 'info', cask]
            args = ' '.join(argv)
            print_scpt(args, self._file, redirect=self._vflag)
            with open(self._file, 'a') as file:
                file.write(f'Script started on {date()}\n')
                file.write(f'command: {args!r}\n')

            try:
                proc = subprocess.check_output(argv, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                print_text(traceback.format_exc(), self._file, redirect=self._vflag)
            else:
                context = proc.decode()
                print_text(context, self._file, redirect=self._vflag)

                version = context.split(maxsplit=2)[1]
                installed = os.path.join(prefix, 'Caskroom', cask, version)
                if os.path.isdir(installed):
                    _temp_pkgs.append(cask)
            finally:
                with open(self._file, 'a') as file:
                    file.write(f'Script done on {date()}\n')

        self._tmp_temp_pkgs = set(_temp_pkgs)
        max_len = len(max(_temp_pkgs, key=lambda s: len(s)))
        context = os.linesep.join(textwrap.wrap('    '.join(
            map(lambda s: s.ljust(max_len), self._tmp_temp_pkgs)), length))
        print_scpt(f'{path} cask outdated list', self._file, redirect=self._vflag)
        print_text(context, self._file, redirect=self._vflag)

    def _proc_update(self, path):
        text = f'Upgrading outdated {self.desc[1]}'
        print_info(text, self._file, redirect=self._qflag)

        argv = [path, 'cask', 'upgrade']
        if self._quiet:
            argv.append('--quiet')
        if self._verbose:
            argv.append('--verbose')
        if self._greedy:
            argv.append('--greedy')
        if self._exhaust:
            argv.append('--exhaust')
        argv.extend(self._update_opts)

        argv.append('')
        for package in self._tmp_temp_pkgs:
            argv[-1] = package
            print_scpt(' '.join(argv), self._file, redirect=self._qflag)
            if run(argv, self._file, redirect=self._qflag, timeout=self._timeout):
                self._fail.append(package)
            else:
                self._pkgs.append(package)
        del self._tmp_temp_pkgs

# -*- coding: utf-8 -*-

import abc
import os
import re
import sys

from macdaily.util.colours import bold, green, red, reset, yellow
from macdaily.util.tools import script


class Command(metaclass=abc.ABCMeta):
    """Base command.

    Process
    ~~~~~~~

    1. check executable
        1. if none exits, exit
        2. else continue
    2. parse options and packages
        1. merge package specification in options
        2. extract command line options
        3. if no package specifications and ``all`` flag NOT set, exit
        4. else continue
    3. locate executables
    4. run command-specified processors
        1. for each executable
            1. command-specified logging process (optional)
                1. fetch packages for main process
                2. if found package specifications, provide trivial did-you-mean function
                3. else continue
            2. ask for comfirmation on main process
                1. if cancelled, exit
                2. else continue
            3. command-specified main process
                1. run main process for each package
                2. run checkout process (optional)
        2. run cleanup process (optional)

    Properties
    ~~~~~~~~~~

    - ``cmd`` -- ``str``, command type
    - ``act`` -- ``tuple<str>``, command actions
        0. verb
        1. verb (past participle)
        2. adjective
    - ``job`` -- ``tuple<str>``, command jobs
        0. noun (singular)
        1. noun (plural)
    - ``name`` -- ``str``, command name (full name)
    - ``mode`` -- ``str``, command mode (acronym)
    - ``time`` -- ``float`` / ``None``, Homebrew renew timestamp
    - ``desc`` -- ``tuple<str>``, command description
        0. singular
        1. plural
    - ``packages`` -- ``set<str>``, process succeeded packages
    - ``failed`` -- ``set<str>``, process failed packages
    - ``notfound`` -- ``set<str>``, unknown packages (not found in registry)

    """
    @property
    @abc.abstractmethod
    def cmd(self):
        return NotImplemented

    @property
    @abc.abstractmethod
    def act(self):
        """verb, past participle, adjective"""
        return (NotImplemented, NotImplemented, NotImplemented)

    @property
    @abc.abstractmethod
    def job(self):
        """noun singular, noun plural"""
        return (NotImplemented, NotImplemented)

    @property
    @abc.abstractmethod
    def name(self):
        return NotImplemented

    @property
    @abc.abstractmethod
    def mode(self):
        return NotImplemented

    @property
    def time(self):
        return self._brew_renew

    @property
    @abc.abstractmethod
    def desc(self):
        """singular, plural"""
        return (NotImplemented, NotImplemented)

    @property
    def packages(self):
        return set(self._pkgs)

    @property
    def failed(self):
        return set(self._fail)

    @property
    def notfound(self):
        return set(self._lost)

    def __init__(self, args, filename, timeout, password, disk_dir, brew_renew):
        """Initialisation.

        Args:

        - ``args`` -- ``argparse.Namespace``
        - ``filename`` -- ``str``, real path of log file
        - ``timeout`` -- ``int``, timeout interval for main process
        - ``password`` -- ``str``, ``sudo`` password
        - ``disk_dir`` -- ``str``, real root path of archive directory
        - ``brew_renew`` -- ``float``, Homebrew renew timestamp

        """
        if self._check_exec():
            return

        self._timeout = timeout
        self._password = password
        self._disk_dir = disk_dir
        self._brew_renew = brew_renew
        with open(filename, 'a', 1) as self._log:
            flag = self._pkg_args(args)
            if flag:
                self._loc_exec()
                self._run_proc()
            else:
                script(['echo', '-e', f'macdaily-{self.cmd}: {yellow}{self.mode}{reset}: '
                        f'no {bold}{self.desc[1]}{reset} to {self.act[0]}'], filename)

    @abc.abstractmethod
    def _check_exec(self):
        """Return if no executable found."""
        return True

    def _pkg_args(self, args):
        """Return if there's packages for main process."""
        self._args = args
        namespace = vars(args)

        self._merge_packages(namespace)
        self._parse_args(namespace)

        return (self._packages or self._all)

    def _merge_packages(self, namespace):
        temp_pkg = list()
        args_pkg = namespace.pop(f'{self.mode}_pkgs', list())
        for pkgs in args_pkg:
            temp_pkg.extend(filter(None, pkgs.split(',')))
        self._packages = set(temp_pkg)

    @abc.abstractmethod
    def _parse_args(self, namespace):
        self._all = False
        self._quiet = False
        self._yes = False

    @abc.abstractmethod
    def _loc_exec(self):
        self._exec = set()

    @abc.abstractmethod
    def _run_proc(self):
        self._pkgs = list()
        self._fail = list()
        self._lost = list()
        for path in self._exec:
            self.__lost_pkgs = set()
            self.__real_pkgs = set()
            self.__temp_pkgs = set()
            self._check_confirm()
            self._did_you_mean()
        self._proc_cleanup()

    def _check_confirm(self):
        job = self.job[1] if len(self.__temp_pkgs) else self.job[0]
        bold_pkgs = f'{reset}, {bold}'.join(self.__temp_pkgs)
        script(['echo', '-e', f'\nmacdaily-{self.cmd}: {green}{self.mode}{reset}: '
                f'{self.desc[0]} {job} available for {bold}{bold_pkgs}{reset}'], self._log.name)
        if self._yes or self._quiet:
            return
        while True:
            ans = input(f'Would you like to {self.act[0]}? (y/N)')
            if re.match(r'[yY]', ans):
                break
            elif re.match(r'[nN]', ans):
                script(['echo', '-e', f'macdaily-{self.cmd}: {yellow}{self.mode}{reset}: '
                        f'{self.desc[0]} {job} postponed due to user cancellation'], self._log.name)
                self.__temp_pkgs = set()
                break
            else:
                print('Invalid input.')

    def _did_you_mean(self):
        for package in self.__lost_pkgs:
            pattern = rf'.*{package}.*'
            matches = f'{reset}, {bold}'.join(filter(lambda s: re.match(pattern, s, re.IGNORECASE), self.__real_pkgs))
            print(f'macdaily-{self.cmd}: {red}{self.mode}{reset}: '
                  f'no available {self.desc[0]} with the name {bold}{package!r}{reset}', file=sys.stderr)
            print(f'macdaily-{self.cmd}: {yellow}{self.mode}{reset}: '
                  f'did you mean any of the following {self.desc[1]}: {bold}{matches}{reset}?')
        del self.__lost_pkgs
        del self.__real_pkgs

    def _proc_cleanup(self):
        pass

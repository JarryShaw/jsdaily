# -*- coding: utf-8 -*-

import abc
import shutil
import sys

from macdaily.cls.command import Command
from macdaily.util.const import flash, purple_bg, red, red_bg, reset, under


class ApmCommand(Command):

    @property
    def mode(self):
        return 'apm'

    @property
    def name(self):
        return 'Atom Package Manager'

    @property
    def desc(self):
        return ('Atom plug-in', 'Atom plug-ins')

    def _check_exec(self):
        self.__exec_path = (shutil.which('apm'), shutil.which('apm-beta'))
        flag = (self.__exec_path == (None, None))
        if flag:
            print(f'macdaily-update: {red_bg}{flash}apm{reset}: command not found', file=sys.stderr)
            print(f'macdaily-update: {red}apm{reset}: you may download Atom from '
                  f'{purple_bg}{under}https://atom.io{reset}')
        return flag

    def _pkg_args(self, namespace):
        flag = super()._pkg_args(namespace)

        # if ``beta`` not set, ``apm`` is the only executable
        if not self._beta and self.__exec_path[0] is None:
            return True
        return flag

    @abc.abstractmethod
    def _parse_args(self, namespace):
        super()._parse_args(namespace)
        self._beta = namespace.pop('beta', False)

    def _loc_exec(self):
        if self._beta:
            self._exec = set(filter(None, self.__exec_path))
        else:
            self._exec = {self.__exec_path[0]}
        del self.__exec_path
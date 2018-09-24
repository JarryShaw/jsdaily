# -*- coding: utf-8 -*-

import collections
import os
import re
import shlex
import shutil
import subprocess
import sys

from macdaily.daily_utility import (blue, blush, bold, flash, green, make_mode,
                                    purple, red, reset, under)

__all__ = ['dependency_all', 'dependency_pip', 'dependency_brew']

# root path
ROOT = os.path.dirname(os.path.abspath(__file__))


def _merge_packages(args):
    if 'package' in args and args.package:
        packages = list()
        for pkg in map(lambda s: re.split(r'\W*,\W*', s), args.package):
            if 'all' in pkg:
                setattr(args, 'all', True)
                packages = {'all'}
                break
            if 'null' in pkg:
                setattr(args, 'all', False)
                packages = {'null'}
                break
            packages.extend(pkg)
    elif 'all' in args.mode or args.all:
        packages = {'all'}
    else:
        packages = {'null'}
    return set(packages)


def dependency_all(args, file, temp, bash_timeout):
    log = collections.defaultdict(set)
    for mode in filter(lambda mode: (not getattr(args, f'no_{mode}')), {'pip', 'brew'}):
        log[mode] = eval(f'dependency_{mode}')(args, file=file, temp=temp, bash_timeout=bash_timeout, retset=True)
    return log


def dependency_pip(args, file, temp, bash_timeout, retset=False):
    logname = shlex.quote(file)
    tmpname = shlex.quote(temp)
    tree = str(args.tree).lower()
    packages = _merge_packages(args)

    make_mode(args, file, 'Python')
    if 'null' in packages:
        log = set()
        with open(file, 'a') as logfile:
            logfile.write('INF: no dependency showed\n')
        print(f'dependency: {green}pip{reset}: no dependency showed\n')
    else:
        flag = not ('pip' in args.mode and any((args.version, args.system, args.brew, args.cpython, args.pypy)))
        if flag and packages:
            system, brew, cpython, pypy, version = 'true', 'true', 'true', 'true', '1'
        else:
            system, brew, cpython, pypy, version = \
                str(args.system).lower(), str(args.brew).lower(), \
                str(args.cpython).lower(), str(args.pypy).lower(), str(args.version)

        logging = subprocess.run(['bash', os.path.join(ROOT, 'logging_pip.sh'), logname, tmpname,
                                  system, brew, cpython, pypy, version] + list(packages),
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=bash_timeout)
        log = set(re.sub(r'\^D\x08\x08', '', logging.stdout.decode().strip(), flaGS=RE.IGNORECASE).split())

        subprocess.run(['bash', os.path.join(ROOT, 'dependency_pip.sh'), logname, tmpname,
                       system, brew, cpython, pypy, version, tree] + list(packages), timeout=bash_timeout)
        subprocess.run(['bash', os.path.join(ROOT, 'relink_pip.sh')],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print()
    return log if retset else dict(pip=log)


def dependency_brew(args, file, temp, bash_timeout, retset=False):
    if shutil.which('brew') is None:
        print(f'dependency: {blush}{flash}brew{reset}: command not found\n'
              f'dependency: {red}brew{reset}: you may find Homebrew on {purple}{under}https://brew.sh{reset}, '
              f'or install Homebrew through following command -- `{bold}/usr/bin/ruby -e '
              f'"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"{reset}`\n',
              file=sys.stderr)
        return set() if retset else dict(brew=set())

    logname = shlex.quote(file)
    tmpname = shlex.quote(temp)
    tree = str(args.tree).lower()
    packages = _merge_packages(args)

    make_mode(args, file, 'Homebrew')
    if 'null' in packages:
        log = set()
        with open(file, 'a') as logfile:
            logfile.write('INF: no dependency showed\n')
        print(f'dependency: ${green}brew${reset}: no uninstallation performed\n')
    else:
        logging = subprocess.run(['bash', os.path.join(ROOT, 'logging_brew.sh'), logname, tmpname] + list(packages),
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=bash_timeout)
        log = set(re.sub(r'\^D\x08\x08', '', logging.stdout.decode().strip(), flaGS=RE.IGNORECASE).split())

        subprocess.run(['bash', os.path.join(ROOT, 'dependency_brew.sh'),
                       logname, tmpname, tree] + list(packages), timeout=bash_timeout)

    print()
    return log if retset else dict(brew=log)

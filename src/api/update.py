# -*- coding: utf-8 -*-

import datetime
import os
import sys
import traceback
import uuid

from macdaily.cli.update import parse_args
from macdaily.cls.update.apm import ApmUpdate
from macdaily.cls.update.brew import BrewUpdate
from macdaily.cls.update.cask import CaskUpdate
from macdaily.cls.update.gem import GemUpdate
from macdaily.cls.update.mas import MasUpdate
from macdaily.cls.update.npm import NpmUpdate
from macdaily.cls.update.pip import PipUpdate
from macdaily.cls.update.system import SystemUpdate
from macdaily.cmd.config import parse_config
from macdaily.util.const import (__version__, bold, green, pink, purple, red,
                                 reset, under, yellow)
from macdaily.util.misc import make_description, print_misc, print_text, record

try:
    import pathlib2 as pathlib
except ImportError:
    import pathlib

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


def update(argv):
    # parse args & config
    args = parse_args(argv)
    config = parse_config()

    # fetch current time
    today = datetime.datetime.today()
    logdate = datetime.date.strftime(today, r'%y%m%d')
    logtime = datetime.date.strftime(today, r'%H%M%S')

    # mkdir for logs
    logpath = pathlib.Path(os.path.join(config['Path']['logdir'], logdate))
    logpath.mkdir(parents=True, exist_ok=True)

    # prepare command paras
    filename = os.path.join(logpath, f'{logtime}-{uuid.uuid4()!s}.log')
    timeout = config['Miscellanea']['timeout']
    askpass = config['Miscellanea']['askpass']
    disk_dir = config['Path']['arcdir']
    brew_renew = None

    # record program status
    text = f'{bold}{green}|🚨|{reset} {bold}Running MacDaily version {__version__}{reset}'
    print_text(text, filename, redirect=args.quiet)
    record(filename, args, today, config, redirect=(not args.verbose))

    cmd_list = list()
    for mode in {'apm', 'brew', 'cask', 'gem', 'mas', 'npm', 'pip', 'system'}:
        # skip disabled commands
        if (not config['Mode'].get(mode, False)) or getattr(args, f'no_{mode}', False):
            text = f'macdaily-update: {yellow}{mode}{reset}: command disabled'
            print_text(text, filename, redirect=(not args.verbose))
            continue

        # update package specifications
        packages = getattr(args, f'{mode}_pkgs', list())
        namespace = getattr(args, mode, dict())
        if not (packages or namespace or args.all):
            text = f'macdaily-update: {yellow}{mode}{reset}: nothing to upgrade'
            print_text(text, filename, redirect=(not args.verbose))
            continue
        namespace['packages'].extend(packages)

        # run command
        cmd_cls = globals()[f'{mode.capitalize()}Update']
        command = cmd_cls(namespace, filename, timeout, askpass, disk_dir, brew_renew)

        # record command
        cmd_list.append(command)
        brew_renew = command.time

    text = f'{bold}{green}|📖|{reset} {bold}MacDaily report of update command{reset}'
    print_text(text, filename, redirect=args.quiet)
    for command in cmd_list:
        desc = make_description(command)
        pkgs = f'{reset}{bold}, {green}'.join(command.packages)
        miss = f'{reset}{bold}, {yellow}'.join(command.notfound)
        ilst = f'{reset}{bold}, {pink}'.join(command.ignored)
        fail = f'{reset}{bold}, {red}'.join(command.failed)

        if pkgs:
            flag = (len(pkgs) == 1)
            text = f'Upgraded following {under}{desc(flag)}{reset}{bold}: {green}{pkgs}{reset}'
        else:
            text = f'No {under}{desc(False)}{reset}{bold} upgraded'
        print_misc(text, filename)

        if fail:
            flag = (len(fail) == 1)
            text = f'Upgrade of following {under}{desc(flag)}{reset}{bold} failed: {red}{fail}{reset}'
        else:
            verb, noun = ('s', '') if len(fail) == 1 else ('', 's')
            text = f'All {under}{desc(False)}{reset}{bold} upgrade{noun} succeed{verb}'
        print_misc(text, filename, redirect=(not args.verbose))

        if ilst:
            flag = (len(ilst) == 1)
            text = f'Ignored updates of following {under}{desc(flag)}{reset}{bold}: {pink}{ilst}{reset}'
        else:
            text = f'No {under}{desc(False)}{reset}{bold} ignored'
        print_misc(text, filename, redirect=(not args.verbose))

        if miss:
            flag = (len(miss) == 1)
            text = f'Following {under}{desc(flag)}{reset}{bold} not found: {yellow}{miss}{reset}'
        else:
            text = f'Hit all {under}{desc(False)}{reset}{bold} specifications'
        print_misc(text, filename, redirect=(not args.verbose))

    if len(cmd_list) == 0:
        text = f'macdaily: {purple}update{reset}: no packages upgraded'
        print_text(text, filename, redirect=(not args.verbose))

    if args.show_log:
        try:
            subprocess.check_call(['open', '-a', '/Applications/Utilities/Console.app', filename])
        except subprocess.CalledProcessError:
            with open(filename, 'a') as file:
                file.write(traceback.format_exc())
            print(f'macdaily: {red}update{reset}: cannot show log file {filename!r}', file=sys.stderr)

    mode_lst = [command.mode for command in cmd_list]
    mode_str = ', '.join(mode_lst) if mode_lst else 'null'
    text = (f'{bold}{green}|🍺|{reset} {bold}MacDaily successfully performed update process '
            f'for {mode_str} package managers{reset}')
    print_text(text, filename, redirect=args.quiet)
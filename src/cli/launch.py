# -*- coding: utf-8 -*-

import argparse
import sys

from macdaily.util.const import __version__, bold, reset


def get_launch_parser():
    #######################################################
    # Launch CLI
    #   * options
    #       - optional arguments
    #       - specification arguments
    #       - general arguments
    #       - miscellaneous arguments
    #   * packages
    #######################################################

    parser = argparse.ArgumentParser(prog='macdaily-launch',
                                     description='MacDaily Dependency Launch Helper',
                                     usage='macdaily launch [options] <prog-selection> ...',
                                     epilog='aliases: init')
    parser.add_argument('-V', '--version', action='version', version=__version__)

    spec_group = parser.add_argument_group(title='specification arguments')
    spec_group.add_argument('program', nargs='*', metavar='PROG',
                            help=(f"helper program to launch, choose from `{bold}askpass{reset}', "
                                  f"`{bold}confirm{reset}' and `{bold}daemons{reset}'"))

    genl_group = parser.add_argument_group(title='general arguments')
    genl_group.add_argument('-a', '--all', action='store_true',
                            help=(f"launch all help programs, i.e. `{bold}askpass{reset}', "
                                  f"`{bold}confirm{reset}' and `{bold}daemons{reset}'"))
    genl_group.add_argument('-q', '--quiet', action='store_true',
                            help='run in quiet mode, with no output information')
    genl_group.add_argument('-v', '--verbose', action='store_true',
                            help='run in verbose mode, with detailed output information')

    return parser


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # main parser process
    main_parser = get_launch_parser()
    main_args = main_parser.parse_args(argv)

    return main_args

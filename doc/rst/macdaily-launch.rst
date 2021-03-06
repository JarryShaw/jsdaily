===============
macdaily-launch
===============

---------------------------------
MacDaily Dependency Launch Helper
---------------------------------

:Version: v2019.8.4
:Date: August 07, 2019
:Manual section: 8
:Author:
    Jarry Shaw, a newbie programmer, is the author, owner and maintainer
    of *MacDaily*. Please contact me at *jarryshaw@icloud.com*.
:Copyright:
    *MacDaily* is licensed under the **Apple Open Source License**.

SYNOPSIS
========

macdaily **launch** [*options*] <*prog-selection*> ...

aliases: **init**

DESCRIPTION
===========

*MacDaily* depends on several homemade helper programs, i.e. *askpass*,
*confirm* and *daemons*. *MacDaily* ``launch`` command will help initialise
and launch these helper programs.

OPTIONS
=======

optional arguments
------------------

-h, --help         show this help message and exit
-V, --version      show program's version number and exit

specification arguments
-----------------------

:PROG:             helper program to launch, choose from *askpass*,
                   *confirm* and *daemons*

general arguments
-----------------

-a, --all          launch all help programs, i.e. *askpass*,
                    *confirm* and *daemons*
-q, --quiet        run in quiet mode, with no output information
-v, --verbose      run in verbose mode, with detailed output information
-n, --no-cleanup   do not run cleanup process
-l, --show-log     open log in *Console.app* upon completion of command

SEE ALSO
========

* *askpass* helper programs

  * ``sudo(8)``
  * ``sudo.conf(5)``

* *confirm* helper programs

  * ``osascript(1)``
  * ``osalang(1)``

* *daemons* helper programs

  * ``launchctl(1)``
  * ``launchd.plist(5)``

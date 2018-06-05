#!/usr/bin/env python
#
#
"""
test_safenames.py
"""
from __future__ import print_function
import os
import errno
import shutil
from subprocess import call


def mkdirquiet(targetpath):
    """Make a directory called targetpath. Don't complain if it already exists.
    """
    try:
        os.mkdir(targetpath)
    except EnvironmentError as e:
        if e.errno != errno.EEXIST:
            raise


def main():
    tmpdir = '/tmp/test_safenames/'

    mkdirquiet(tmpdir)

    # , 'ends in space ', 'ends in space and tab \t']
    badnames = ['ends in tab\t']

    for fn in badnames:
        fn = tmpdir + fn
        open(fn, 'a').close()

    call(["./safenames.py", tmpdir, '--debug'])


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
#
#
"""
test_safenames.py
"""
import errno

# from __future__ import print_function
import os
import shutil
from pathlib import Path
from subprocess import call


def mkdirquiet(targetpath):
    try:
        os.mkdir(targetpath)
    except EnvironmentError as e:
        if e.errno != errno.EEXIST:
            raise


def rmtreequiet(targetpath):
    try:
        shutil.rmtree(targetpath)
    except EnvironmentError as e:
        if e.errno != errno.ENOENT:
            raise


def main():
    tmpdir = "/tmp/test_safenames/"

    rmtreequiet(tmpdir)
    mkdirquiet(tmpdir)

    # , 'ends in space ', 'ends in space and tab \t']
    # ,'| three <> illegals', 'ends in tab\t']
    badnames = ["|starts with illegal"]

    for fn in badnames:
        fn = tmpdir + fn
        open(fn, "a").close()

    exif_perl_module = Path(tmpdir + "Image::ExifTool::WritePDF.3pm")

    Path(exif_perl_module).touch()

    call(["./safenames.py", tmpdir, "--debug"])


# rmtreequiet(tmpdir)


if __name__ == "__main__":
    main()

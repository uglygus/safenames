#!/usr/bin/env python
#
#
"""
safenames.py
Walks a directory tree and tests each file and directory for cross platform legality.
Requires user confirmation before any changes are made.

Tested on Mac, Linux and OSX
"""

from __future__ import print_function

import os
import argparse
import sys
import re

try:
    import tty
    import termios
except ImportError:
    # Probably Windows.
    try:
        import msvcrt
    except ImportError:
        raise ImportError('getch not available')
    else:
        getch = msvcrt.getch
else:
    def getch():
        """getch() -> key character

        Read a single keypress from stdin and return the resulting character.
        Nothing is echoed to the console. This call will block if a keypress
        is not already available, but will not wait for Enter to be pressed.

        If the pressed key was a modifier key, nothing will be detected; if
        it were a special function key, it may return the first character of
        of an escape sequence, leaving additional characters in the buffer.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if ch == '\x03':
            print('^C')
            sys.exit()
        return ch

bad_windows_chars = r':<>"\/|?*' + '\n' + '\r' + '\x7F'
for x in range(0, 31):
    bad_windows_chars += chr(x)

bad_linux_chars = "/" + "\00"
bad_mac_chars = ":" + "\00"
bad_ideas_chars = '\t'

bad_chars_all = bad_windows_chars + \
    bad_linux_chars + bad_mac_chars + bad_ideas_chars

# must be uppercase
BAD_WINDOWS_NAMES = ['CON', 'PRN', 'AUX', 'NUL', 'CLOCK$',
                     'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                     'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
                     '$ATTRDEF', '$BADCLUS', '$BITMAP', '$BOOT', '$LOGFILE', '$MFT', '$MFTMIRR',
                     'PAGEFILE.SYS', '$SECURE', '$UPCASE', '$VOLUME', '$EXTEND', '$EXTEND\$OBJID',
                     '$EXTEND\$QUOTA', '$EXTEND\$REPARSE',
                     ]


def is_bad_char(filename, charlist):
    for char in charlist:
        # print('char = ', char)
        if char in filename:
            print("illegal__%s__" % char, end='')
            return char

    return False


def ends_in_white_space(item):
    if item == item.rstrip():
        return False
    else:
        return True


def printable(char):

    if char is None:
        return ''
    if char == "\n":
        return "\\n"
    if char == "\r":
        return "\\r"
    if char == "\t":
        return "\\t"
    if char == "\003":
        return "^C"
    if char == "\000":
        return "\\000"
    if char == "\007":
        return "\\BEL"
    if ord(char) == 127:
        return '\DEL'
    if ord(char) <= 31:
        return '\\' + str(ord(char))

    return char


def type_newname(item, root):
    print(os.path.join(root, item))
    print('illegal Filename: ', item)
    subitem = item + '_legal'
    # noinspection PyCompatibility
    newname = raw_input('Enter new filename  default:[' + subitem + ']: ')

    if newname == '':
        newname = subitem

    print('newname=', newname)

    # overwrites silently if newname exists
    #rename_item(old, new)
    rename_item(os.path.join(root, item), os.path.join(root, newname))


def replace_bad_chars(filename, bad_chars):
    for c in bad_chars:
        filename.replace(c, '_')
    return filename


def name_exists(item):

    xxx, item_filename = os.path.split(item)

    if os.path.exists(item):
        print('"{}" already exists updating version.'.format(item_filename))
        root, ext = os.path.splitext(item)
        p = re.compile('\((\d+)\)\Z')
        m = p.findall(root)

        if m == []:
            new = root + ' (1)' + ext
            new = name_exists(new)

        else:
            version = m[0]
            old_version = '(' + version + ')'
            version = int(version) + 1
    #        print('version=',version)
            new_version = '(' + str(version) + ')'

            root = root.replace(old_version, new_version)

            new = root + ext
        return new
    else:
        return item


def rename_item(old, new):

    new = name_exists(new)

    try:
        os.rename(old, new)
    except OSError as e:
        print ('OSError!', e)


def clean_item(item, root):
    """
    returns new filename or False if the file does not need to be cleaned
    """
    old = os.path.join(root, item)

    print(os.path.join(root, item))
    cleaned = False

    if item == "Icon\r":
        print("Icon\\r : Not Windows compatible but OSX system filename. Will not change.")
        return

    item_clean = item
    for c in bad_chars_all:
        item_clean = item_clean.replace(c, '_')

    if item_clean != item:
        item_clean = name_exists(os.path.join(root, item_clean))

        xxx, item_cleaned = os.path.split(item_clean)
#        print('xxx=', xxx, '\titem_cleaned2 = ', item_cleaned)

        item_clean = item_cleaned

        print('replace "{}" with "{}"?  (Y/n/t/x : Yes/no/type/delete): '.format(item, item_clean), end="")
        ch = getch()
        print(ch)

        if ch.lower() == 'y' or ch == '\r':
            new = os.path.join(root, item_clean)
            #print ('old=', old, '\nnew=', new)
            rename_item(old, new)
            # print('renamed!')
            cleaned = item_clean

        if ch.lower() == 'x':
            os.unlink(os.path.join(root, item))

        if ch.lower() == 't':
            new_name = raw_input("new filename: ")
            new = os.path.join(root, new_name)
            #print ('old=', old, '\nnew=', new)
            rename_item(old, new)

    if ends_in_white_space(item):
        print('item ends in whitespace "{}"'.format(item))
        print('replace ending white space?  (Y/n)?')

        # print('ch==',ch)
        item_stripped = item.rstrip()
        if item_stripped == '':
            item_stripped = "_"
            print('file "{}" is only only whitespace!'.format(item))

        print('replace with "_" (Y/n/t/x : Yes/no/type/delete)')
        ch = getch()
        print(ch)

        if ch.lower() == 'x':
            os.unlink(os.path.join(root, item))

        if ch.lower() == 't':
            new_name = raw_input("new filename: ")
            new = os.path.join(root, new_name)
            #print ('old=', old, '\nnew=', new)
            rename_item(old, new)
            cleaned = new

        if ch.lower() == 'y' or ch == '\r':

            print('renaming "{}" --> "{}"'.format(item, item_stripped))
            rename_item(os.path.join(root, item),
                        os.path.join(root, item_stripped))
            cleaned = item_stripped

    return cleaned


def main():
    parser = argparse.ArgumentParser(
        description="catch and correct filenames that are not cross compatible")
    parser.add_argument("dir", help='directory to clean')
    parser.parse_args()
    args = parser.parse_args()

    for directory in [args.dir]:
        for root, dirs, files in os.walk(directory, topdown=False):

            all_items = dirs + files

            for item in all_items:
                if item.upper() in BAD_WINDOWS_NAMES:
                    type_newname(item, root)

                item = clean_item(item, root)
                while item:
                    item = clean_item(item, root)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
#
#
'''
safenames.py
Walks a directory tree and tests each file and directory for cross platform legality.
Requires user confirmation before any changes are made.
'''

from __future__ import print_function

import os
import argparse
import sys

try:
    import tty
    import termios
except ImportError:
    # Probably Windows.
    try:
        import msvcrt
    except ImportError:
        # FIXME what to do on other platforms?
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

badWindowsChars = r':<>"\/|?*' + '\n' + '\r' + '\x7F'
for x in range(0, 31):
    badWindowsChars + chr(x)

badLinuxChars = "/" + "\00"
badMacChars = ":" + "\00"
badPersonalChars = '\t'

badChars = badWindowsChars + badLinuxChars + badMacChars + badPersonalChars

# must be uppercase
badWindowsNames = ['CON', 'PRN', 'AUX', 'NUL', 'CLOCK$',
                   'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                   'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
                   '$ATTRDEF', '$BADCLUS', ',$BITMAP', '$BOOT', '$LOGFILE', '$MFT', '$MFTMIRR',
                   'PAGEFILE.SYS', '$SECURE', '$UPCASE', '$VOLUME', '$EXTEND', '$EXTEND\$OBJID',
                   '$EXTEND\$QUOTA', '$EXTEND\$REPARSE',
                   ]


def isBadChar(filename, charList):
    for char in charList:
        # print('char = ', char)
        if char in filename:
            print("illegal__%s__" % char, end='')
            return char

    return False


def endsInWhiteSpace(item):
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


def renameItem(item, root):
    print(os.path.join(root, item))
    print('illegal Filename: ', item)
    subItem = item + '_legal'
    newName = raw_input('Enter new filename  default:[' + subItem + ']: ')

    if newName == '':
        newName = subItem

    print('newName=', newName)

    # overwrites silently if newName exists
    os.rename(os.path.join(root, item), os.path.join(root, newName))


def cleanItem(item, root):
    print(os.path.join(root, item))
    cleaned = False

    if item == "Icon\r":
        print("Icon\\r : Not Windows compatible but OSX system filename. Will not change.")
        return

    wrongChar = isBadChar(item, badChars)
    if wrongChar:
        print('wrongChar = ', wrongChar)
        itemClean = item.replace(wrongChar, '_')
        print(item, ' --> ', itemClean)
        cleaned = itemClean

        print('replace \'' + printable(wrongChar) +
              '\' with \'_\'  (Y/n/x:delete file) ?')
        ch = getch()
        print('ch==' + printable(ch) + '==')
        if ch.lower() == 'y' or ch == '\r':
            os.rename(os.path.join(root, item), os.path.join(root, itemClean))
            cleaned = itemClean
        if ch.lower() == 'x':
            os.unlink(os.path.join(root, item))

        print('\n')

    if endsInWhiteSpace(item):
        print('directory ends in White==' + item + '==')
        print('replace ending white space?  (Y/n)?')
        ch = getch()
        # print('ch==',ch)
        itemStripped = item.rstrip()
        if ch.lower() == 'y' or ch == '\r':
            os.rename(os.path.join(root, item),
                      os.path.join(root, itemStripped))
            cleaned = itemStripped
        print('\n')
    return cleaned


def main():
    parser = argparse.ArgumentParser(
        description="catch and correct filenames that are not cross compatible")
    parser.add_argument("dir", help='directory to clean')
    parser.parse_args()
    args = parser.parse_args()

    for directory in [args.dir]:
        for root, dirs, files in os.walk(directory):
            for item in dirs:
                while cleanItem(item, root):
                    cleanItem(item, root)

            for item in files:
                if item.upper() in badWindowsNames:
                    renameItem(item, root)

                item = cleanItem(item, root)
                while item:
                    item = cleanItem(item, root)


if __name__ == '__main__':
    main()

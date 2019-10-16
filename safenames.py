#!/usr/bin/env python3

"""

safenames.py
Walks a directory tree and tests each file and directory for cross platform legality.
Requires user confirmation before any changes are made.

Tested on Mac, Linux and OSX

"""


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
                     'PAGEFILE.SYS', '$SECURE', '$UPCASE', '$VOLUME', '$EXTEND',
                     ]

BAD_IDEAS_NAMES = ['-']


commandline_args = None


def debug(message):
    """ Print debug messages. If debug is activated, otherwise do nothing. """
    global commandline_args
    if commandline_args.debug:
        print(message)


def is_bad_char(filename, charlist):
    """ Return true if filename contains a bad character from the charlist. """
    debug('is_bad_char({}, {})'.format(filename, charlist))
    for char in charlist:
        if char in filename:
            print("illegal__{}__".format(char))
            return char

    return False


def ends_in_white_space(item):
    """ Return true if the string ends in whitespace. """
    debug('ends_in_white_space(item={})'.format(item))
    if item == item.rstrip():
        return False
    else:
        return True


def printable(char):
    """ Return true is char is printable in the terminal. """

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
    """ manually type a new filename. """
    debug('type_newname(item={}, root={})'.format(item, root))

    print(os.path.join(root, item))
    print('illegal Filename: ', item)
    subitem = item + '_legal'
    newname = input('Enter new filename  default:[' + subitem + ']: ')

    if newname == '':
        newname = subitem

    print('newname=', newname)

    # FIX THIS!! overwrites silently if newname exists
    rename_item(os.path.join(root, item), os.path.join(root, newname))


def collapsewhite(filename):
    """ Returns filename with whitespace stripped and collapsed. """
    debug('collapsewhite(filename="{}")'.format(filename))
    filename = ' '.join(filename.split())
    debug('collapsewhite(filename="{}")'.format(filename))
    return filename


def replace_bad_chars(filename, bad_chars):
    """ Returns filename with bad characters replaced with underscores. """
    debug('replace_bad_chars(filename="{}" bad_chars="{}")'.format(
        filename, bad_chars))
    for c in bad_chars:
        if (c in filename):
            print('\tbad character "{}"'.format(printable(c)))
            filename = filename.replace(c, '_')
    debug('replace_bad_chars returning="{}"'.format(filename))
    return filename


def name_exists(item):
    """
    Returns new suggested name if name already exists.
    Appends a version number in parenthesis.
    ie. newfilename (1).txt
    """

    debug('name_exists(item={})'.format(item))
    xxx, item_filename = os.path.split(item)

    if os.path.exists(item):
        print('"{}" already exists updating version.'.format(item_filename))
        root, ext = os.path.splitext(item)
        p = re.compile('\((\d+)\)\Z')
        m = p.findall(root)

        if not m:
            new = root + ' (1)' + ext
            new = name_exists(new)

        else:
            version = m[0]
            old_version = '(' + version + ')'
            version = int(version) + 1
            new_version = '(' + str(version) + ')'

            root = root.replace(old_version, new_version)

            new = root + ext
        return new
    else:
        return item


def rename_item(old, new):
    """ Rename file. """
    debug('rename_item(old={}, new={})'.format(old, new))
    new = name_exists(new)
    print('old="' + old + '",  new="' + new)
    try:
        os.rename(old, new)
    except OSError as e:
        print('OSError!', e)


def clean_item(item, root):
    """
    Given a filename (item)
    Returns new filename with all corrections applied.
    """
    debug('clean_item(item={}, root={})'.format(item, root))
    old = os.path.join(root, item)

    if commandline_args.verbose:
        print(os.path.join(root, item))

    cleaned = item

    if item == "Icon\r":
        # - we should this back on if we add a --verbose flag
        # print('"Icon\\r" : Not Windows compatible but OSX system filename. Will not change.')
        return

    if ':' in item and (item.endswith('.abcdg') or item.endswith(
            '.abcdi') or item.endswith('.abcdp') or item.endswith('.abcds')):
            # - we should turn this back on if we add a --verbose flag
            # '"{}" contains an illegal colon but OSX Address Book file. Will not change.'.format(item))
        return

    if '.AppleDouble' in root:
        if '.Parent::EA' in item or '::EA::' in item or '::EA' in item:
            # - we should turn this back on if we add a --verbose flag
            # '"{}" contains an illegal colon but is an OSX Appledouble file. Will not change.'.format(item))
            return

    item_clean = item

    item_clean = replace_bad_chars(item_clean, bad_chars_all)

    if commandline_args.collapsewhite:
        item_clean = collapsewhite(item_clean)

    if item_clean != item:
        item_clean = name_exists(os.path.join(root, item_clean))

        xxx, item_clean = os.path.split(item_clean)

        print('{}/{}'.format(root, item)), end='', flush=True)
        print('replace "{}" with "{}"?  (Y/n/t/x : Yes/no/type/delete): '.format(item, item_clean), end='',  flush=True)

        ch = getch()
        print(ch)

        if ch.lower() == 'y' or ch == '\r':
            new = os.path.join(root, item_clean)
            # print ('old=', old, '\nnew=', new)
            rename_item(old, new)
            # print('renamed!')
            cleaned = item_clean

        if ch.lower() == 'x':
            os.unlink(os.path.join(root, item))

        if ch.lower() == 't':
            new_name = input("new filename: ")
            new = os.path.join(root, new_name)
            # print ('old=', old, '\nnew=', new)
            rename_item(old, new)

    fname, ext = os.path.splitext(item)

    if ends_in_white_space(fname):

        item_stripped = fname.rstrip()
        if item_stripped == '':
            item_stripped = "_"
            print('file "{}" is only whitespace!'.format(root))

        print('{}/{}'.format(root, fname))
        # , end='', flush=True)

        print('strip trailing whitespace? (Y/n/t/x : Yes/no/type/delete)', end='',  flush=True)

        ch = getch().lower()
        print(ch)

        if ch == 'x':
            os.unlink(os.path.join(root, item))

        if ch == 't':
            new_name = input("new filename: ")
            new = os.path.join(root, new_name)
            # print ('old=', old, '\nnew=', new)
            rename_item(old, new)
            cleaned = new

        if ch.lower() == 'y' or ch == '\r':
            print('renaming "{}" --> "{}"'.format(item, item_stripped + ext))
            rename_item(os.path.join(root, item),
                        os.path.join(root, item_stripped + ext))
            cleaned = item_stripped + ext

    return cleaned


def main():
    """ Do the main thing. """
    #    global log_debug
    global commandline_args

    parser = argparse.ArgumentParser(
        description="Catch and correct directory and filenames that are not cross compatible. ")
    parser.add_argument("dir", help='directory to clean')
    parser.add_argument('-c', '--collapsewhite', action='store_true',
                        help='collapse multple white spaces into one " " also trims any leading and trailing whitespace')
    parser.add_argument('--debug', action='store_true', help='more debug info')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='list everyfile as processed')

    commandline_args = parser.parse_args()

    if commandline_args.debug:
        commandline_args.verbose = True

    debug('commandline_args.verbose = {}'.format(commandline_args.verbose))
    debug('commandline_args.debug   = {}'.format(commandline_args.debug))

    for directory in [commandline_args.dir]:
        for root, dirs, files in os.walk(directory, topdown=False):

            all_items = dirs + files

            for item in all_items:
                if item.upper() in BAD_WINDOWS_NAMES:
                    type_newname(item, root)

                if item.upper() in BAD_IDEAS_NAMES:
                    type_newname(item, root)

                item_cleaned = clean_item(item, root)
                # while item:
                # item = clean_item(item, root)

                debug(
                    'item="{}", item_cleaned="{}"'.format(
                        item, item_cleaned))


if __name__ == '__main__':
    main()

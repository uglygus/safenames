#!/usr/bin/env python3

"""
safenames.py
Walks a directory tree and tests each file and directory for cross platform legality.
Requires user confirmation before any changes are made.

Tested on Mac and Linux under WSL but not Windows.
"""
import argparse
import os
import re
import sys

try:
    import termios
    import tty
except ImportError:
    # Probably Windows.
    try:
        import msvcrt
    except ImportError:
        raise ImportError("getch not available")
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

        if ch == "\x03":
            print("^C")
            sys.exit()
        return ch


BAD_WINDOWS_CHARS = r':<>"\/|?*' + "\n" + "\r" + "\x7F"
for x in range(0, 31):
    BAD_WINDOWS_CHARS += chr(x)

BAD_LINUX_CHARS = "/"
BAD_MAC_CHARS = ":"
BAD_IDEAS_CHARS = "\t"

BAD_CHARS_ALL = BAD_WINDOWS_CHARS + BAD_LINUX_CHARS + BAD_MAC_CHARS + BAD_IDEAS_CHARS

# must be uppercase
BAD_WINDOWS_NAMES = [
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "CLOCK$",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
    "$ATTRDEF",
    "$BADCLUS",
    "$BITMAP",
    "$BOOT",
    "$LOGFILE",
    "$MFT",
    "$MFTMIRR",
    "PAGEFILE.SYS",
    "$SECURE",
    "$UPCASE",
    "$VOLUME",
    "$EXTEND",
]

# not strictly prohibited but just terrible names for files
BAD_IDEAS_NAMES = ["-"]

commandline_args = None


def debug(message):
    """Print debug messages. If debug is activated, otherwise do nothing."""
    global commandline_args
    if commandline_args.debug:
        print(message)


def printable(char):
    """Return a printable version of the character."""

    if char is None:
        return ""
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
        return "\\DEL"
    if ord(char) <= 31:
        return "\\" + str(ord(char))

    return char


def type_newname(item, root):
    """manually type a new filename."""

    debug("type_newname(item={}, root={})".format(item, root))

    print(os.path.join(root, item))
    print("illegal filename: ", item)
    subitem = item + "_legal"
    newname = input("Enter new filename  default:[" + subitem + "]: ")

    if newname == "":
        newname = subitem

    print("newname=", newname)

    # FIX THIS!! overwrites silently if newname exists
    rename_item(os.path.join(root, item), os.path.join(root, newname))


def collapsewhite(filename):
    """Returns filename with whitespace stripped and collapsed."""

    messages = []

    debug('collapsewhite(filename="{}")'.format(filename))
    newfilename = " ".join(filename.split())
    if newfilename != filename:
        messages.append("collapsable whitespace")
    debug('collapsewhite(filename="{}")'.format(filename))
    return newfilename, messages


def replace_bad_chars(filename, bad_chars):
    """Returns filename with bad characters replaced with underscores."""

    messages = []

    debug('replace_bad_chars(filename="{}" bad_chars="{}")'.format(filename, bad_chars))
    for c in bad_chars:
        if c in filename:
            messages.append('bad character "{}"'.format(printable(c)))

            filename = filename.replace(c, "_")
    debug('replace_bad_chars returning="{}"'.format(filename))

    return filename, messages


def name_exists(item):
    """Returns new suggested name if name already exists.
    Appends a version number in parenthesis.
    ie. 'newfilename (1).txt'
    """

    debug("name_exists(item={})".format(item))
    item_filename = os.path.basename(item)

    if os.path.exists(item):
        print('"{}" already exists updating version.'.format(item_filename))
        root, ext = os.path.splitext(item)
        p = re.compile(r"\((\d+)\)$")
        m = p.findall(root)

        if not m:
            new = root + " (1)" + ext
            new = name_exists(new)

        else:
            version = m[0]
            old_version = "(" + version + ")"
            version = int(version) + 1
            new_version = "(" + str(version) + ")"

            root = root.replace(old_version, new_version)

            new = root + ext
        return new

    return item


def rename_item(old, new):
    """Rename file."""

    debug("rename_item(old={}, new={})".format(old, new))
    new = name_exists(new)
    # print('old="' + old + '",  new="' + new)
    try:
        os.rename(old, new)
    except OSError as e:
        print("OSError!", e)


def only_whitespace(fname):
    """tests if filename is whitespace only returns '_' as new filename.
    tests extension too.
    """
    debug("only_whitespace(fname={})".format(fname))

    messages = []

    file_nameonly, file_ext = os.path.splitext(fname)

    file_nameonly = file_nameonly.rstrip()
    if file_nameonly == "":
        filenameonly = "_"
        messages.append("filename is only whitespace")

    fname_stripped = file_nameonly + file_ext

    if fname_stripped != fname:
        messages.append("trailing whitespace")

    return fname_stripped, messages


def bad_windows_name(fname):
    """illegal windows names"""

    debug("bad_windows_name(fname={})".format(fname))
    messages = []

    if fname.upper() in BAD_WINDOWS_NAMES:
        messages.append(fname + " is a reserved name on Windows")
        fname = fname + "_legal"

    return fname, messages


def bad_ideas_name(fname):
    """catch names that you shouldn't be using regardless like '-'."""

    debug("bad_ideas_name(fname={})".format(fname))
    messages = []

    if fname.upper() in BAD_IDEAS_NAMES:
        messages.append(fname + " is a BAD idea for a filename")
        fname = fname + "_better_name"

    return fname, messages


def has_warning(item, root):
    """Returns True if the filename is a known system name and should not be changed.
    This list is incomplete and should be expanded.
    """

    debug("has_warning(item={}, root={})".format(item, root))
    messages = []

    if item == "Icon\r":
        messages.append(
            'WARNING: "Icon\\r" : Not Windows compatible but MacOS system filename. Will not change.'
        )
        return True, messages

    if item.startswith("Image::ExifTool") and item.endswith(".3pm"):
        messages.append("WARNING: ExifTool man pages have an illegal name - skipping")
        return True, messages

    print("item==", item)
    if item == "File::RandomAccess.3pm":
        messages.append("WARNING: ExifTool man pages have an illegal name - skipping")
        return True, messages

    if "/Photos Library.photoslibrary" in root:
        messages.append(
            'WARNING: "{}" is part of the MacOS Photos App Library. Will not change.'.format(
                item
            )
        )
        return True, messages

    if ":" in item and (
        item.endswith(".abcdg")
        or item.endswith(".abcdi")
        or item.endswith(".abcdp")
        or item.endswith(".abcds")
    ):
        messages.append(
            'WARNING: "{}" contains an illegal colon but MacOS Address Book file. Will not change.'.format(
                item
            )
        )
        return True, messages

    if ".AppleDouble" in root:
        if ".Parent::EA" in item or "::EA::" in item or "::EA" in item:
            messages.append(
                'WARNING: "{}" contains an illegal colon but is an MacOS Appledouble file. Will not change.'.format(
                    item
                )
            )
            return True, messages

    return False, messages


def ends_in_period(fname):
    """strips trailing period"""
    debug(f"ends_in_period(fname={fname})")

    messages = []

    file_nameonly, file_ext = os.path.splitext(fname)

    fname_stripped = file_nameonly.rstrip(".") + file_ext.rstrip(".")

    if fname_stripped != fname:
        messages.append("ends in a period")

    return fname_stripped, messages


def trailing_whitespace(fname):
    """Strips trailing whitespace."""
    debug("trailing_whitespace(fname={})".format(fname))

    messages = []

    file_nameonly, file_ext = os.path.splitext(fname)

    fname_stripped = file_nameonly.rstrip() + file_ext.rstrip()

    if fname_stripped != fname:
        messages.append("trailing whitespace")

    return fname_stripped, messages


def leading_whitespace(fname):
    """Strips leading whitespace."""
    debug("leading_whitespace(fname={})".format(fname))

    messages = []

    file_nameonly, file_ext = os.path.splitext(fname)

    fname_stripped = file_nameonly.lstrip() + file_ext.lstrip()

    if fname_stripped != fname:
        messages.append("leading whitespace")

    return fname_stripped, messages


def print_messages(messages):
    """messages is a list of lists. prints each item in each list"""
    for m in messages:
        if isinstance(m, list):
            for n in m:
                print("\t{}".format(n))
        else:
            print("\t{}".format(m))


def clean_item(item, root):
    """Given a filename (item)
    Returns new filename with all corrections applied.
    """
    debug("\nclean_item(item={}, root={})".format(item, root))

    old = os.path.join(root, item)

    messages = []

    if commandline_args.verbose:
        print(os.path.join(root, item))

    cleaned = item

    item_clean = item

    # item_clean, new_messages = perl_ExifTool_module(item_clean)
    # messages.append(new_messages)

    # print("messages == ", messages)
    #  input("after perl_exiftool_module...")

    # if len(messages[0]) == 0:
    #    print("messages are empty b/c this is not an EXIFTOOL module", item_clean)
    # only check this if the file is not an Image::ExifTool::... file
    item_clean, new_messages = replace_bad_chars(item_clean, BAD_CHARS_ALL)
    messages.append(new_messages)

    item_clean, new_messages = bad_windows_name(item_clean)
    messages.append(new_messages)

    item_clean, new_messages = only_whitespace(item_clean)
    messages.append(new_messages)

    item_clean, new_messages = trailing_whitespace(item_clean)
    messages.append(new_messages)

    item_clean, new_messages = leading_whitespace(item_clean)
    messages.append(new_messages)

    item_clean, new_messages = ends_in_period(item_clean)
    messages.append(new_messages)

    if commandline_args.collapsewhite:
        item_clean, new_messages = collapsewhite(item_clean)
        messages.append(new_messages)

    warn_bool, warn_str = has_warning(item, root)
    #     print('item=',item)
    #     print('warn_bool=', warn_bool)
    #     print('warn_str=', warn_str)

    messages.append(warn_str)
    #     if warn_bool == True:
    #         print_messages(messages)
    #         return

    if item_clean != item:

        print("\n{}".format(os.path.abspath(os.path.join(root, item))))

        print_messages(messages)

        if not warn_bool:
            print(
                'Replace "{}" with "{}"?  (Y/n/t/x : Yes/no/type/delete): y'.format(
                    item, item_clean
                ),
                end="",
                flush=True,
            )

            ch = getch()
            print(ch)

            if ch.lower() == "y" or ch == "\r":
                new = os.path.join(root, item_clean)
                # print ('old=', old, '\nnew=', new)
                rename_item(old, new)
                # print('renamed!')
                cleaned = item_clean

            if ch.lower() == "x":
                os.unlink(os.path.join(root, item))

            if ch.lower() == "t":
                new_name = input("new filename: ")
                new = os.path.join(root, new_name)
                # print ('old=', old, '\nnew=', new)
                rename_item(old, new)

    return cleaned


def check_for_case_only_dupes(all_items, root):
    """check if any of the file or dir names differ by case only and correct it"""

    # check for duplicates differing only by case
    all_items_casefold = [x.casefold() for x in all_items]

    dupes = []

    # print('all_items_casefold==',all_items_casefold)
    for item in all_items_casefold:
        if all_items_casefold.count(item) > 1:
            # print('duplicate', item)

            for x in all_items:
                if x.casefold() == item:
                    # print('DUPE=', x)
                    dupes.append(x)

    # print('dupes=', dupes)
    dupes_set = set(dupes)
    # convert the set to the list
    unique_dupes = list(dupes_set)
    if len(unique_dupes) > 0:
        print("WARNING: ", root, " contains duplicates differing by case:")
        for x in unique_dupes:
            print("\t", os.path.join(root, x))


def main():
    """Do the main thing."""

    global commandline_args

    # warnings need a couple settings
    # heed warnings and prevent user from making changes (default)
    # ignore warnings and allow user to make changes

    parser = argparse.ArgumentParser(
        description="Catch and correct directory and filenames that are not cross compatible. "
    )
    parser.add_argument(
        "input",
        nargs="*",
        default=None,
        help="accepts files and/or folders to be cleaned",
    )
    parser.add_argument(
        "-c",
        "--collapsewhite",
        action="store_true",
        help='collapse multple white spaces into one " " also trims any leading and trailing whitespace',
    )
    parser.add_argument("--debug", action="store_true", help="more debug info")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="list everyfile as processed"
    )

    commandline_args = parser.parse_args()

    if commandline_args.debug:
        commandline_args.verbose = True

    debug("commandline_args.verbose = {}".format(commandline_args.verbose))
    debug("commandline_args.debug   = {}".format(commandline_args.debug))

    if not commandline_args.input:
        parser.print_help()
        return 0

    debug('commandlines_arg ="{}"'.format(commandline_args.input))

    # process files and dirs
    for single_input in commandline_args.input:

        if not (os.path.isdir(single_input) or os.path.isfile(single_input)):
            print("ERROR: input is not a file or a directory: " + single_input)
            parser.print_help()
            return 0

        absinput = os.path.abspath(single_input)

        if os.path.isfile(absinput):
            root, item = os.path.split(absinput)
            debug('root="{}", item="{}"'.format(root, item))
            item_cleaned = clean_item(item, root)
            debug('item="{}", item_cleaned="{}"'.format(item, item_cleaned))

        if os.path.isdir(absinput):
            for root, dirs, files in os.walk(absinput, topdown=False):

                all_items = dirs + files

                # check for duplicates differing only by case
                check_for_case_only_dupes(all_items, root)

                # clean the items
                for item in all_items:
                    debug('item="{}"'.format(item))
                    item_cleaned = clean_item(item, root)
                    debug('item="{}", item_cleaned="{}"'.format(item, item_cleaned))

    return 0


if __name__ == "__main__":
    sys.exit(main())

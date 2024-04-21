# safenames.py


Walks a directory tree and tests each file and directory for cross platform legality.
Requires user confirmation before any changes are made.

# Usage

```
usage: safenames.py [-h] [--collapsewhite] [--debug] [-v] dir

Catch and correct directory and filenames that are not cross compatible.

positional arguments:
  dir              directory to clean

optional arguments:
  -h, --help       show this help message and exit
  --collapsewhite  collapse multple white spaces into one " " also trims any
                   leading and trailing whitespace)
  --debug          more debug info
  -v, --verbose    list everyfile as processed
```

## Strips Windows illegals

* Control characters `0x00–0x1f 0x7F`
* Reserved characters `/ ? < > \ : * | "`
* newline `\n`
* linefeed `\r` except for Icon\r files since those are OSX system files.
* trailing spaces
* illegal Windows filenames:

		`CON PRN AUX NUL CLOCK$`
		`COM1 COM2 COM3 COM4COM5 COM6 COM7 COM8 COM9`
		`LPT1 LPT2 LPT3 LPT4 LPT5 LPT6 LPT7 LPT8 LPT9`
		`$ATTRDEF $BADCLUS $BITMAP $BOOT $LOGFILE $MFT $MFTMIRR`
		`PAGEFILE.SYS $SECURE $UPCASE $VOLUME $EXTEND $EXTEND\$OJID`
		`$EXTEND\$QUOTA $EXTEND\$REPARSE`

## Strips Mac illegals

* Reserved characters `: 0x00`

## Strips Linux illegals

* Reserved characters `/ 0x00`

## Strips characters that are a bad idea

* tab `\t`

### corrects filename named simply hyphen '-'

* hyphen `-`

### Collapses whitespace
optionally with `--collapsewhite`  collapses multple white spaces into one " " also trims any leading and trailing whitespace

### Recognizes OSX system files and gives the option to skip them.
* Icon\r
* .AppleDouble[...]::EA::com.apple.quarantine
* *.abcdg (Addressbook file)
* *.abcdi (Addressbook file)
* *.abcdp (Addressbook file)
* *.abcds (Addressbook file)


# To do
* catch Windows anomolies periods and spaces only names not allowed
* catch windows files ending in period
* -v --verbose option
* -auto option
* -i --interactive option (currently default)
* --fill_char option to set fill char instead of defaulting to `_`
* option to delete the bad character instead of replacing with `_`
* leading '-' in filenames is a bad idea

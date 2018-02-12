# safefilenames.py


Walks a directory tree and tests each file and directory for cross platform legality.
Requires user confirmation before any changes are made.

### Strips Windows illegals

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
		`PAGEFILE.SYS $SECURE $UPCASE $VOLUME $EXTEND $EXTEND\\$OJID`
		`$EXTEND\\$QUOTA $EXTEND\\$REPARSE`

### Strips Mac illegals

* Reserved characters `: 0x00`

### Strips Linux illegals

* Reserved characters `/ 0x00`

### Strips characters that are a bad idea

* tab `\t`

## Usage

`safefilenames.py [-h] dir`

## Bugs

* When renaming a file if the new file already exists it will be silently overwritten.

## Todo
* catch Windows anomolies periods and spaces only names not allowed
* catch windows files ending in period
* -v --verbose option
* -auto option
* -i --interactive option (currently default)
* --fill_char `=` option to set fill char instead of defaulting to `_`
* option to delete the bad character instead of replacing with `_`

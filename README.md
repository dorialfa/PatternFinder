# PatternFinder
patternfinder is a fast commandline program for searching within binary files.

## Features
* Find apperances of patterns in specific files.
* Support in regex search.
* Super fast searches.
* Output your results to a file.
* No compailing, Python3.5+, any Operation System.

## Syntax
Usage: patternfinder.py -p <path to a pattern file written in JSON format> -f <binary_file> -o <outputfile> file to write results to (optional)

arguments:
* -h, --help 
  * show this help message and exit
* -p PATTERN, --pattern PATTERN
  * Path to a file containing a dictionary in JSON format with the hex strings you want to search for .
  *                        [+] NOTICE: regular expression are accepted too.
                        [+] Example for content of a file: {"1F8B0800":"Gzip","3037303...":"cpio"}
*  -f FILE, --file FILE
    * The binary file you want to search in.
*  -o OUTPUT, --output OUTPUT    [Optional]
    * Saves the results of the search to a file. If not chosen - print the results to stdout

## Example
./patternfinder.py -p ~/Desktop/pattern.json -f ~/Downloads/nexus2020.1.zip -o ~/Documents/PatternsFound.json

## Output
The output can be shown to your screen, or saved to a file.
It will be in JSON format, with the following categories in it:
- range : the location of the selected bytes.
- size : the size of the slscted pattern.
- 4_byte : wil show you the 4 first bytes of the pattern.
- type : will show you the type of the pattern, as written in the file you mentioned in -p.

## Examples for use-cases:
* Finding offsets of paddings in a binary file.
* Finding offsets of zip archives in a binary file.

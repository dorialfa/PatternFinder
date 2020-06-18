#!/usr/bin/env python
"""
patternfinder.py -p PATTERN -f FIle -o OUTPUT (optional)

examples:
./patternfinder.py -p ~/Desktop/pattern.json -f ~/Downloads/nexus2020.1.zip -o ~/Documents/PatternsFound.json

+Features: no compiling, fast, regex support, all operating systems.
+minimum python3.5 required

Writer:
Dori Alfandary 18/06/2020
"""
import argparse
import json
import re
import signal
import time
from argparse import RawTextHelpFormatter
from binascii import hexlify


class Arguments:
    """
    This class gets the arguments from the user.

    ...

    Attributes
    ----------
    description : str
        the description of the code.

    Methods
    -------
    get_args()
        gets the arguments from the user.

    """

    def __init__(self):
        """
        Parameters
        ----------
        description : str
            the description of the code.
        """
        self.description = 'patternfinder is a fast commandline program for searching within binary files.\nUsage: ' \
                           'patternfinder.py -p <path to a pattern file written in JSON format> -f <binary_file> -o ' \
                           '<outputfile> file to write results to (optional) '

    def get_args(self):
        """
        gets the arguments from the user. optional args:
        -p : path to a pattern file written in JSON format
        -f : path to the binary file to search in
        -o : path to a file where to output will be saved (optional)

        Returns
        -------
        NameSpace
            the arguments as a NameSpace with their values.
        """
        parser = argparse.ArgumentParser(description=self.description, formatter_class=RawTextHelpFormatter)
        parser.add_argument('-p', '--pattern', type=str, metavar='PATTERN',
                            help='Path to a file containing a dictionary in JSON format with the hex strings you want '
                                 'to search for.\n[+] NOTICE: '
                                 'regular expression are accepted too.\n[+] Example for content of a file: {'
                                 '"1F8B0800":"Gzip","3037303...":"cpio"}\n',
                            required=True)
        parser.add_argument('-f', '--file', type=str,
                            metavar='FILE', help='The binary file you want to search in.', required=True)
        parser.add_argument("-o", "--output", type=str, metavar="OUTPUT",
                            help="Saves the results of the search to a file. "
                                 "if not chosen - print the results to stdout")
        args = parser.parse_args()
        with open(args.pattern) as dict_file:
            try:
                args.pattern = json.load(dict_file)
            except json.decoder.JSONDecodeError:
                print("""ERROR: incorrect JSON Format! Maybe you used '' instead of "" ?""")
                exit()
        return args


class PatternFinder:
    """
    this class creates the search engine of the software.
    it gets a binary file and dict full of strings, and search for appearances of this strings in the file.

    ...

    Attributes
    ----------
    arguments : class
        the instance of the Arguments class, to gain the attributes of the user.
    path : str
        the path of the binary file.
    pattern_dict : str
        the dict that contains the hex strings/regular expressions to search for.
    file_read : int
        count how many data has been read, to calculate the offset correctly.
    read_size : int
        declares how much bytes to read every time. (defaults - 4096)
    patterns_found : list
        lists all the patterns the have been found in the file.

    Methods
    -------
    read_loop()
        while True, Read the binary file, 'read_size' at a time, then sends it to search() method.
        When the file ends, calls the parser() method and breaks the loop.

    search(buffer)
        gets data, search in it a pattern from the pattern_dict, using regex.
        if found, save it to a list (patterns_found) in JSON format.

    parser()
        uses the patterns found, adds it together to a JSON format, and prints it.

    """

    def __init__(self):
        """
        Parameters
        ----------
        self.arguments : class
        the instance of the Arguments class, to gain the attributes of the user.
        self.path : str
            the path of the binary file.
        self.pattern_dict : str
            the dict that contains the hex strings/regular expressions to search for.
        self.file_read : int
            count how many data has been read, to calculate the offset correctly.
        self.read_size : int
            declares how much bytes to read every time. (defaults - 4096)
        self.patterns_found : list
            lists all the patterns the have been found in the file.

        Methods
        -------
        Runs the read_loop() methods when called.
        """
        self.arguments = Arguments()
        self.path = self.arguments.get_args().file
        self.pattern_dict = self.arguments.get_args().pattern
        self.file_read = 0
        self.read_size = 4096
        self.patterns_found = []
        self.read_loop()

    def read_loop(self):
        """
        while True, Read the binary file, 'read_size' at a time, then sends it to search() method.
        When the file ends, calls the parser() method and breaks the loop.

        returns : None.
        """
        with open(self.path, "rb") as bin_file:
            print(f"[+] Started searching in {self.path} - Be Patient!")
            while True:
                buffer = hexlify(bin_file.read(4096))  # hexlify - Make the file readable with no /x in it.
                self.search(buffer.decode())
                if not buffer:  # When the file ends.
                    self.parser()
                    break

    def search(self, buffer):
        """
        gets data, search in it a pattern from the pattern_dict, using regex.
        if found, save it to a list (patterns_found) in JSON format - the lists include of:
        the byte range of the pattern, the size of it, the 4 first bytes of it, and the type of it.

        returns : None

        Parameters
        ----------
        buffer : str
            the data the method searches in.
        """
        for pattern in self.pattern_dict:
            regex_pattern = re.compile(pattern)  # Compile the regex pattern - fastest way.
            result = re.search(regex_pattern, buffer)  # Searches for the pattern in the current buffer.

            if result is not None:  # Pattern Exists in buffer
                offset = result.start() + self.file_read  # calculates the offset.
                success_output = {'range': (offset, offset + len(pattern)), 'size': len(pattern),
                                  '4_byte': result.group()[:4], 'type': self.pattern_dict[pattern]}
                self.patterns_found.append(success_output)
        self.file_read += self.read_size  # adds the amount of file read to the file_read.

    def parser(self):
        """
        Uses the patterns found, adds it together to a JSON format, and prints it.
        If the user chose to save to file - saves instead to printing to screen.

        returns: None
        """
        json_output = {"results": self.patterns_found}
        if self.arguments.get_args().output:
            with open(self.arguments.get_args().output, "w") as output_file:
                json.dump(json_output, output_file, indent=1)
            print(f"[+] File Saved to {self.arguments.get_args().output}")
        else:
            print(json.dumps(json_output, indent=1))


def main():
    """
    the main function.
    starts a signal listen for CTRL+C (SIGINT).
    creates in instance of PatternFinder.
    counts the runtime of the function.
    """
    start = time.time()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    finder = PatternFinder()
    print("\n[+] Finished in {:.3f} seconds".format(time.time() - start))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A command-line client for using a HFST automaton to tokenise running text
"""

import libhfst
from argparse import ArgumentParse
from sys import stderr, stdin, stdout, exit

def main():
    a = ArgumentParser(description="HFST corpus handlings")
    a.add_argument('inputs', metavar='INFILE', type=open, nargs='*',
            help="Files to process with corpus tool")
    a.add_argument('--output', '-o', metavar='OFILE', 
            type=argparse.FileType('w'), help="store result in OFILE")
    a.add_argument('--tokeniser', '-t', type=append, metavar='TFILE',
            help="Pre-process input stream with automata from TFILE")
    a.add_argument('--orthography', '-o', type=append, metavar="XFILE",
            help="pre-process tokens with automata from XFILE "
            "if not recognised")
    a.add_argument('--error-model', '-e', type=append, metavar='EFILE',
            help="extract more guesses through EFILE if not recognised")
    a.add_argument('--guesser', '-g', type=append, metavar="GFILE",
            help="finally use guesser GFILE instead if not recognised")
    a.add_argument("--verbose", '-v', type=store_true,
            help="print verbosely while processing")
    opts = a.parse_args()
    tokenisers = list()
    for tokeniserfile in opts.tokeniser:
        if opts.verbose:
            print("Reading from", tokeniserfile)
        tokeniserstream = libhfst.HfstInputStream(tokeniserfile)
        t = libhfst.HfstTransducer(tokeniserstream)
        if opts.verbose:
            print("Read tokeniser", t.get_property('name'))
        tokenisers.append(t)
    if len(tokenisers) == 0:
        print("Using Unicode tokeniser with character classes")
        tokeniserstream = libhfst.HfstInputStream("tokeniser-unicode.openfst.hfst")
        t = libhfst.HfstTransducer(tokeniserStream)
        tokenisers.append(t)
    if len(inputs) == 0:
        if opts.verbose:
            print("Reading corpus data from <stdin>")
        inputs.append(stdin)
    for inputfile in inputs:
        for line in inputfile:
            for tokeniser in tokenisers:
                if tokeniser.get_type() == libhfst.TROPICAL_OPENFST_TYPE:
                    pathmaton = libhfst.HfstTransducer(line, hfst_tokeniser,
                            libhfst.TROPICAL_OPENFST_TYPE)
                    tokenisation = pathmaton.compose(tokeniser).extract_paths_fd()
                    paths = libhfst.detokenize_paths(tokenisation)
                    if len(paths) > 1:
                        print("Ambiguous tokenisation", file=stderr)
                    elif len(paths) == 1:
                        tokens = paths.split("@TOKEN@")
                        for token in tokens:
                            print(token)
                    else:
                        print("No tokens", file=stderr)
                else:
                    print("Not impl !OFST", file=stderr)
    exit(0)


    


if __name__ == '__main__':
    main()

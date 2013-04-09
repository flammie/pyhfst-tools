#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A command-line client for using a HFST automaton to tokenise running text
"""

import libhfst
from argparse import ArgumentParser, FileType
from sys import stderr, stdin, stdout, exit

def main():
    a = ArgumentParser(description="HFST corpus handlings")
    a.add_argument('inputs', metavar='INFILE', type=open,
            nargs='*', help="Files to process with corpus tool")
    a.add_argument('--output', '-o', metavar='OFILE', 
            type=FileType('w'), help="store result in OFILE")
    a.add_argument('--tokeniser', '-t', action='append', metavar='TFILE',
            help="Pre-process input stream with automata from TFILE")
    a.add_argument("--verbose", '-v', action='store_true',
            help="print verbosely while processing")
    opts = a.parse_args()
    tokenisers = list()
    if not opts.tokeniser:
        if opts.verbose:
            print("Using Unicode tokeniser with character classes")
        tokeniserstream = libhfst.HfstInputStream("tokeniser-unicode.openfst.hfst")
        t = libhfst.HfstTransducer(tokeniserstream)
        tokenisers.append(t)
    else:
        for tokeniserfile in opts.tokeniser:
            if opts.verbose:
                print("Reading from", tokeniserfile)
            tokeniserstream = libhfst.HfstInputStream(tokeniserfile)
            t = libhfst.HfstTransducer(tokeniserstream)
            if opts.verbose:
                print("Read tokeniser", t.get_property('name'))
            tokenisers.append(t)
    print(opts.inputs, len(opts.inputs))
    if len(opts.inputs) < 1:
        if opts.verbose:
            print("Reading corpus data from <stdin>")
        opts.inputs = [stdin]
    if opts.verbose:
        print("Creating UTF-8 character tokeniser for HFST")
    hfst_tokeniser = libhfst.HfstTokenizer()
    for inputfile in opts.inputs:
        for line in inputfile:
            for tokeniser in tokenisers:
                if tokeniser.get_type() == libhfst.TROPICAL_OPENFST_TYPE:
                    pathmaton = libhfst.HfstTransducer(line, hfst_tokeniser,
                            libhfst.TROPICAL_OPENFST_TYPE)
                    tokenisation = libhfst.extract_paths_fd(pathmaton.compose(tokeniser))
                    paths = libhfst.detokenize_paths(tokenisation)
                    if len(paths) > 1:
                        print("Ambiguous tokenisation", file=stderr)
                    elif len(paths) == 1:
                        tokens = paths[0].output.split("@TOKEN@")
                        for token in tokens:
                            print(token)
                    else:
                        print("No tokens", file=stderr)
                else:
                    print("Not impl !OFST", file=stderr)
    exit(0)


    


if __name__ == '__main__':
    main()

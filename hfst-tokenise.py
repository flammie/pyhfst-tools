#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A command-line client for using a HFST automaton to tokenise running text
"""

import libhfst
from argparse import ArgumentParser, FileType
from sys import stderr, stdin, stdout, exit

def take_greedy_lrlm_tokens(paths):
    if len(paths) > 1:
        tokenlength = 0
        goodpaths = set(paths)
        position = 0
        while len(goodpaths) > 1:
            longest = position
            for path in paths:
                tokenlength = path.output.find("@TOKEN@", position)
                if tokenlength == -1:
                    tokenlenght = len(path.output)
                if tokenlength > longest:
                    longest = tokenlength
                    goodpaths = set([path])
                elif tokenlength == longest:
                    goodpaths.add(path)
            position = longest
        return goodpaths.pop().output.split("@TOKEN@")
    elif len(paths) == 1:
        return paths[0].output.split("@TOKEN@")
    else:
        return None


def main():
    a = ArgumentParser(
            description="Tokeniser for plain text data using HFST automata. "
            "Takes a text stream input and outputs TSV token stream where "
            "one line is one token. Tokens should include white-space tokens,"
            "but this decision is solely up to output of used automata. "
            "Some automata may be able to parse non-plain marked up text.",
            epilog="If INFILE or OFILE is omitted, standard streams will be "
            "used.\n"
            "If DISAMB is omitted, greedy LRLM will be used.")
    a.add_argument('inputs', metavar='INFILE', type=open,
            nargs='*', help="Files to process with corpus tool")
    a.add_argument('--output', '-o', metavar='OFILE',
            type=FileType('w'), help="store result in OFILE")
    a.add_argument('--tokeniser', '-t', action='append', metavar='TFILE',
            help="Pre-process input stream with automata from TFILE")
    a.add_argument('--disambiguation', '-d', metavar='DISAMB', 
            choices=['LRLM'], default='LRLM',
            help="use DISAMB tactic to select from multiple paths")
    a.add_argument("--verbose", '-v', action='store_true',
            help="print verbosely while processing")
    opts = a.parse_args()
    tokenisers = list()
    if not opts.output:
        if opts.verbose:
            print("printing output to stdout, disabling verbose", stderr)
            opts.verbose = False
        opts.output = stdout
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
    if len(opts.inputs) < 1:
        if opts.verbose:
            print("Reading corpus data from <stdin>")
        opts.inputs = [stdin]
    if opts.verbose:
        print("Creating UTF-8 character tokeniser for HFST")
    hfst_tokeniser = libhfst.HfstTokenizer()
    for inputfile in opts.inputs:
        print("# hfst-tokenise.py TSV token stream 1", file=opts.output)
        print("# From input file", inputfile, file=opts.output)
        print("# Next line is a header line", file=opts.output)
        print("Token", file=opts.output)
        for line in inputfile:
            line = line.strip('\n')
            could_tokenise = False
            for tokeniser in tokenisers:
                if tokeniser.get_type() == libhfst.TROPICAL_OPENFST_TYPE:
                    pathmaton = libhfst.HfstTransducer(line, hfst_tokeniser,
                            libhfst.TROPICAL_OPENFST_TYPE)
                    tokenisation = libhfst.extract_paths_fd(pathmaton.compose(tokeniser))
                    paths = libhfst.detokenize_paths(tokenisation)
                    tokens = None
                    if opts.disambiguation == 'LRLM':
                        tokens = take_greedy_lrlm_tokens(paths)
                    else:
                        print("What is this DISAMB?", opts.disambiguation,
                                file=stderr)
                    if tokens:
                        for token in tokens:
                            print(token.replace('@_EPSILON_SYMBOL_@', ''))
                        could_tokenise = True
                        break
                    else:
                        if opts.verbose:
                            print("Got no tokens with FOO using",
                                    opts.disambiguation)
                else:
                    print("Not impl !OFST", file=stderr)
                    exit(2)
            if not could_tokenise:
                for token in line.split():
                    print(token, file=opts.output)
            print("\\n", file=opts.output)
    exit(0)


    


if __name__ == '__main__':
    main()

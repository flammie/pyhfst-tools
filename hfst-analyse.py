#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A command-line client for using HFST automata to analyse a TSV token stream
"""

import libhfst
from argparse import ArgumentParser, FileType
from sys import stderr, stdin, stdout, exit

import unicodedata

def try_analyse(analyser, token):
    titlecased = False
    untitlecased = False
    uppercased = False
    lowercased = False
    res = libhfst.detokenize_paths(analyser.lookup_fd(token))
    if len(res) == 0:
        if token[0].isupper():
            res = libhfst.detokenize_paths(analyser.lookup_fd(token[0].lower() + token[1:]))
            untitlecased = True
        else:
            res = libhfst.detokenize_paths(analyser.lookup_fd(token[0].upper() + token[1:]))
            titlecased = True
    if len(res) == 0:
        if token.isupper():
            res = libhfst.detokenize_paths(omorfi.lookup_fd(token.lower()))
            lowercased = True
    if len(res) == 0:
        if token.islower():
            res = libhfst.detokenize_paths(omorfi.lookup_fd(token.upper()))
            uppercased = True
    if lowercased:
        for r in res:
            r.output = r.output + '[CASECHANGE=TOLOWER]'
    elif uppercased:
        for r in res:
            r.output = r.output + '[CASECHANGE=TOUPPER]'
    elif untitlecased:
        for r in res:
            r.output = r.output + '[CASECHANGE=DOWNFIRST]'
    elif titlecased:
        for r in res:
            r.output = r.output + '[CASECHANGE=UPFIRST]'
    return res

def fallback_analyse(token):
    analysis = '[WORD_ID=' + token + ']'
    if len(token) == 1:
        analysis += '[GUESS=UNICODE]'
        analysis += '[UCD_NAME=' + unicodedata.name(token[0], 'INVALID') + ']'
        analysis += '[UCD_CATEGORY=' + unicodedata.category(token[0]) + ']'
    elif len(token) == 0:
        analysis += '[GUESS=EMPTY][ERROR=EMPTYSTRINGISNOTATOKEN]'
    elif len(token) > 1:
        analysis += '[GUESS=NONE]'
    return analysis

def main():
    a = ArgumentParser(
            description="Analyser for TSV token data using HFST automata. "
            "Takes a TSV stream input and outputs TSV analysis stream where "
            "one column is one analysis.", 
            epilog="If INFILE or OFILE is omitted, standard streams will be "
            "used.")
    a.add_argument('inputs', metavar='INFILE', type=open,
            nargs='*', help="Files to process with corpus tool")
    a.add_argument('--output', '-o', metavar='OFILE',
            type=FileType('w'), help="store result in OFILE")
    a.add_argument('--analyser', '-a', action='append', metavar='AFILE',
            required=True, help="Analyse tokens with automaton AFILE")
    a.add_argument("--verbose", '-v', action='store_true',
            help="print verbosely while processing")
    opts = a.parse_args()
    analysers = list()
    for analyserfile in opts.analyser:
        if opts.verbose:
            print("Reading from", analyserfile)
        analyserstream = libhfst.HfstInputStream(analyserfile)
        t = libhfst.HfstTransducer(analyserstream)
        if opts.verbose:
            print("Read analyser", t.get_property('name'))
        analysers.append(t)
    if len(opts.inputs) < 1:
        if opts.verbose:
            print("Reading corpus data from <stdin>")
        opts.inputs = [stdin]
    for inputfile in opts.inputs:
        for line in inputfile:
            line = line.strip('\n')
            tokens = line.split('\t')
            for token in tokens:
                could_analyse = False
                for analyser in analysers:
                    analyses = try_analyse(analyser, token)
                    if len(analyses) > 0:
                        could_analyse = True
                        print(token, end='')
                        for analysis in analyses:
                            print("\t", analysis.output, end='', sep='')
                if not could_analyse:
                    analysis = fallback_analyse(token)
                    print(token, analysis, end='', sep='\t')
            print()
    exit(0)


    


if __name__ == '__main__':
    main()

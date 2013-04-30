#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A command-line client for using a HFST automaton to tokenise running text
"""

from argparse import ArgumentParser, FileType
from sys import stderr, stdin, stdout, exit
import re

def main():
    a = ArgumentParser(description="LEXC lexicon translator")
    a.add_argument('inputs', metavar='INFILE', type=open, nargs='*',
            help="Files to process with lexc tranlator")
    a.add_argument('--output', metavar='OUTFILE', type=FileType('w'),
            help="Resulting new lexicon")
    opts = a.parse_args()
    if len(opts.inputs) == 0:
        opts.inputs.append(stdin)
    if not opts.output:
        opts.output=stdout
    lexicons = dict()
    lexname = None
    for inputfile in opts.inputs:
        linen = 0
        for line in inputfile:
            linen += 1
            line = re.sub("!.*", "", line.strip())
            if not line or line == "":
                continue
            if line.startswith('LEXICON'):
                lexname = line.split()[1]
                if lexname in lexicons.keys():
                    print("Repeated lexicon", lexname, "on line", linen, "of",
                            inputfile)
                else:
                    lexicons[lexname] = dict()
            elif lexname:
                fields = line.split()
                if len(fields) <= 1:
                    print("Not enough spaces on line", linen, "file", inputfile)
                    continue
                morphstuff = '0'
                cont = '?'
                if fields[1].startswith(';'):
                    # lemma omitted
                    morphstuff = '0'
                    cont = fields[0]
                elif fields[2].startswith(';'):
                    # regular
                    morphstuff = fields[0]
                    cont = fields[1]
                elif fields[3].startswith(';'):
                    # glossed
                    morphstuff = fields[0]
                    cont = fields[2]
                else:
                    print("Semicolon in wrong place on line", linen, "file",
                            inputfile)
                    continue
                if morphstuff in lexicons[lexname].keys():
                    lexicons[lexname][morphstuff] += [cont]
                else:
                    lexicons[lexname][morphstuff] = [cont]
    for ln1,stuff1 in lexicons.items():
        for ln2,stuff2 in lexicons.items():
            if ln1 == ln2:
                continue
            if stuff1 == stuff2:
                print("Duplicate lexicon found:", ln1, ln2)
    for ln,stuff in lexicons.items():
        print("NEWLEXICON", ln, file=opts.output)
        for morph,conts in stuff.items():
            print(morph, "|".join(conts), ";", file=opts.output)
    exit(0)

    


if __name__ == '__main__':
    main()

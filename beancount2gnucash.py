#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path
from beancount import loader

LEDGER_FILENAME = "ledger_filename"

def main(ledger_filename):
    entries, errors, options = loader.load_file(ledger_filename)
    print(entries)
    pass

def parse_args():
    def filename(x):
        x = str(x)
        if not os.path.isfile(x):
            raise argparse.ArgumentTypeError("Given filename is not a file")
        return x
    parser = argparse.ArgumentParser()
    parser.add_argument(LEDGER_FILENAME, type=filename,
                        help="filename of beancount ledger file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args.ledger_filename)

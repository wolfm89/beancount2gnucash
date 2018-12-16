#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path
import csv
from collections import defaultdict
from difflib import get_close_matches
from beancount import loader, core

LEDGER_FILENAME = "ledger_filename"
GNUCASH_ACC_TYPES = {"BANK", "CASH", "ASSET",
                     "CREDIT", "LIABILITY", "STOCK", "MUTUAL",
                     "INCOME", "EXPENSE", "EQUITY",
                     "RECEIVABLE", "PAYABLE", "TRADING"}
ACC_HEADERS = {"type": "type", "full_name": "full_name", "name": "name", "code": "code",
               "description": "description", "color": "color", "notes": "notes",
               "commoditym": "commoditym", "commodityn": "commodityn", "hidden": "hidden",
               "tax": "tax", "place_holder": "place_holder"}


def main(ledger_filename):
    head, tail = os.path.split(ledger_filename)
    entries, errors, options = loader.load_file(ledger_filename)
    # for entry in entries:
    #     print(type(entry))
    export_accounts([entry for entry in entries if isinstance(
        entry, core.data.Open)], head, os.path.splitext(tail)[0])


def export_accounts(accounts, directory, basename):
    rows = []
    for account in accounts:
        # print(account)
        row = defaultdict(lambda: "")
        row[ACC_HEADERS["full_name"]] = account.account
        row[ACC_HEADERS["name"]] = account.account.split(":")[-1]
        row[ACC_HEADERS["type"]] = get_close_matches(
            account.account.split(":")[0].upper(), GNUCASH_ACC_TYPES, n=1)[0]
        row[ACC_HEADERS["commodityn"]] = account.currencies[0]
        rows.append(row)
    with open(basename + '_accounts.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(
            csvfile, ACC_HEADERS.values(), quoting=csv.QUOTE_ALL)
        for row in rows:
            writer.writerow(row)


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

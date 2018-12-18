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
    export_accounts([entry for entry in entries if isinstance(
        entry, core.data.Open)], head, os.path.splitext(tail)[0])
    export_transactions()


def export_transactions():
    pass


def export_accounts(accounts, directory, basename):
    def create_row(full_name, name, type, commodityn, place_holder):
        row = defaultdict(lambda: "")
        row[ACC_HEADERS["full_name"]] = full_name
        row[ACC_HEADERS["name"]] = name
        row[ACC_HEADERS["type"]] = type
        row[ACC_HEADERS["commodityn"]] = commodityn
        row[ACC_HEADERS["hidden"]] = "F"
        row[ACC_HEADERS["tax"]] = "F"
        row[ACC_HEADERS["place_holder"]] = place_holder
        return row

    rows = []
    for account in accounts:
        currency = account.currencies[0]
        parent = account.account.split(":")
        while len(parent) > 0:
            full_name = ":".join(parent)
            if any([full_name == row[ACC_HEADERS["full_name"]] for row in rows]):
                break
            matched_type = get_close_matches(
                parent[0].upper(), GNUCASH_ACC_TYPES, n=1)[0]
            row = create_row(full_name, parent[-1], matched_type, currency,
                             "T" if len(parent) == 1 else "F")
            rows.append(row)

            parent = parent[:-1]

    out_filename = basename + '_accounts.csv'
    with open(out_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(
            csvfile, ACC_HEADERS.values(), quoting=csv.QUOTE_ALL)
        for row in rows:
            writer.writerow(row)
    print("Written to " + out_filename)


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

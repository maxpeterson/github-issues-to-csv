#!python

import argparse

from github2csv import cards2csv


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Export GitHub Issues from Project Cards to a CSV file')
    parser.add_argument('project', help='Project id')
    parser.add_argument('-t', '--token', help='OAuth2 token', required=True)
    parser.add_argument('-o', '--outfile', help='Output file')
    parser.add_argument('-v', '--verbose', help='Print verbose output', action='store_true')

    args = vars(parser.parse_args())

    cards2csv(**args)

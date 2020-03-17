#!/usr/bin/env python3
#firefox_cli - cli interface to firefox

import argparse
import glob
import lz4.block
import os.path
import sys


def firefox_profiles_path():
    if os.name == 'nt':
        return os.path.expandvars('%APPDATA%\\Mozilla\\Firefox\\Profiles')
    else:
        return os.path.expandvars('$HOME/.mozilla/firefox')


def find_profile(name):
    profile_home = firefox_profiles_path()
    if name != None:
        profile = os.path.join(profile_home, name)
        if os.path.isdir(profile): return profile
    #Needs quite some upgrades
    profile = glob.glob(os.path.join(profile_home, '*.default-release'))[0]
    if os.path.isdir(profile): return profile


def extract(args):
    with open(args.file, 'rb') as f:
        b = f.read()
        if b[:8] == b'mozLz40\0':
            b = lz4.block.decompress(b[8:])
        sys.stdout.buffer.write(b)


def compress(args):
    content = sys.stdin.read()
    with open(args.file, 'wb') as f:
        f.write(b"mozLz40\0" + lz4.block.compress(content.encode('utf-8')))


def get_path(args):
    print(os.path.join(find_profile(args.profile), args.file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-P', '--profile')
    subparsers = parser.add_subparsers()
    parser_extract = subparsers.add_parser('extract')
    parser_extract.set_defaults(func=extract)
    parser_extract.add_argument('file')
    parser_compress = subparsers.add_parser('compress')
    parser_compress.set_defaults(func=compress)
    parser_compress.add_argument('file')
    parser_get_path = subparsers.add_parser('get_path')
    parser_get_path.set_defaults(func=get_path)
    parser_get_path.add_argument('file', nargs='?', default='')
    args = parser.parse_args()
    os.chdir(find_profile(args.profile))
    args.func(args)

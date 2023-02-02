#!/usr/bin/env python3
#firefox_cli - cli interface to firefox

import argparse
import configparser
import glob
import lz4.block
import os.path
import sys


def firefox_profiles_path():
    if os.name == 'nt':
        return os.path.expandvars('%APPDATA%\\Mozilla\\Firefox\\Profiles')
    elif sys.platform == 'darwin':
        return os.path.expandvars('$HOME/Library/Application Support/firefox')
    else:
        return os.path.expandvars('$HOME/.mozilla/firefox')


def get_path_from_profile(profile_home, profile):
    if profile.getboolean('IsRelative'):
        return os.path.join(profile_home, profile['Path'])
    else:
        return profile['Path']


def find_profile(name):
    profile_home = firefox_profiles_path()
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(profile_home, 'profiles.ini'))
    profiles = [cfg[x] for x in cfg.sections() if 'Name' in cfg[x]]
    installs = [cfg[x] for x in cfg.sections() if x.startswith('Install')]
    if name == None:
        if len(installs) == 0:
            if len(profiles) == 0:
                raise Exception("No profile found. Initialize one")
            if len(profiles) == 1:
                return get_path_from_profile(profile_home, profiles[0])
            else:
                for profile in profiles:
                    if not profile.getboolean('Default'): continue
                    return get_path_from_profile(profile_home, profile)
                raise Exception("No default profile found. Specify a profile")
        elif len(installs) == 1:
            return os.path.join(profile_home, installs[0]['Default'])
        else:
            raise Exception("Multiple Install sections. Specify a profile")
    else:
        for profile in profiles:
            if profile['Name'] != name: continue
            return get_path_from_profile(profile_home, profile)
        raise Exception("Could not find specified profile.")


def extract(args):
    with open(os.path.join(find_profile(args.profile), args.file), 'rb') as f:
        b = f.read()
        if b[:8] == b'mozLz40\0':
            b = lz4.block.decompress(b[8:])
        sys.stdout.buffer.write(b)


def compress(args):
    content = sys.stdin.read()
    with open(os.path.join(find_profile(args.profile), args.file), 'wb') as f:
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
    args.func(args)

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
    if profile.getboolean('IsRelative', fallback=False):
        return os.path.join(profile_home, profile['Path'])
    elif 'Path' in profile:
        return profile['Path']
    elif 'Default' in profile:
        return os.path.join(profile_home, profile['Default'])


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
                return profiles[0]
            else:
                for profile in profiles:
                    if not profile.getboolean('Default'): continue
                    return profile
                raise Exception("No default profile found. Specify a profile")
        elif len(installs) == 1:
            return installs[0]
        else:
            raise Exception("Multiple Install sections. Specify a profile")
    else:
        for profile in profiles:
            if profile['Name'] != name: continue
            return profile
        raise Exception("Could not find specified profile.")


def get_profile_path(name, file=None):
    return os.path.join(
        get_path_from_profile(firefox_profiles_path(), find_profile(name)),
        file if file else '')


def extract(args):
    with open(get_profile_path(args.profile, args.file), 'rb') as f:
        b = f.read()
        if b[:8] == b'mozLz40\0':
            b = lz4.block.decompress(b[8:])
        sys.stdout.buffer.write(b)


def compress(args):
    content = sys.stdin.read()
    with open(get_profile_path(args.profile, args.file), 'wb') as f:
        f.write(b"mozLz40\0" + lz4.block.compress(content.encode('utf-8')))


def get_path(args):
    print(get_profile_path(args.profile, args.file))


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

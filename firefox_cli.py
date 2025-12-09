#!/usr/bin/env python3
# firefox_cli - cli interface to firefox

from argparse import ArgumentParser, Namespace
from configparser import ConfigParser, SectionProxy
from typing import Optional, cast
from pathlib import Path
import lz4.block  # type: ignore
import os.path
import sys
import shutil


browser_profile_dirs: dict[str, dict[str, str]] = {
    "firefox": {
        "nt": "%APPDATA%\\Mozilla\\Firefox\\Profiles",
        "darwin": "$HOME/Library/Application Support/firefox",
        "unix": "$HOME/.mozilla/firefox",
    },
    "librewolf": {
        "nt": "%APPDATA%\\Librewolf\\Profiles",
        "darwin": "$HOME/Library/Application Support/librewolf",
        "unix": "$HOME/.mozilla/librewolf",
    },
}


def firefox_profiles_path(browser: str) -> Path:
    if os.name == "nt":
        platform = "nt"
    elif sys.platform == "darwin":
        platform = "darwin"
    else:
        platform = "unix"
    return Path(os.path.expandvars(browser_profile_dirs[browser][platform]))


def get_path_from_profile(
    profile_home: Path, profile: SectionProxy
) -> Optional[Path]:
    if profile.getboolean("IsRelative", fallback=False):
        return profile_home.joinpath(profile["Path"])
    elif "Path" in profile:
        return Path(profile["Path"])
    elif "Default" in profile:
        return profile_home.joinpath(profile["Default"])
    return None


def find_profile(browser: str, name: Optional[str]) -> SectionProxy:
    profile_config = firefox_profiles_path(browser).joinpath("profiles.ini")
    if not profile_config.is_file():
        raise Exception("No profiles found. Initialize your browser")
    cfg = ConfigParser()
    cfg.read(profile_config)

    profiles = [cfg[x] for x in cfg.sections() if "Name" in cfg[x]]
    installs = [cfg[x] for x in cfg.sections() if x.startswith("Install")]
    if name is None:
        if len(installs) == 0:
            if len(profiles) == 0:
                raise Exception("No profile found. Initialize one")
            if len(profiles) == 1:
                return profiles[0]
            else:
                for profile in profiles:
                    if not profile.getboolean("Default"):
                        continue
                    return profile
                raise Exception("No default profile found. Specify a profile")
        elif len(installs) == 1:
            return installs[0]
        else:
            raise Exception("Multiple Install sections. Specify a profile")
    else:
        for profile in profiles:
            if profile["Name"] != name:
                continue
            return profile
        raise Exception("Could not find specified profile.")


def get_profile_path(
    browser: str, name: Optional[str], file: Optional[str] = None
) -> Path:
    profile_path = get_path_from_profile(
        firefox_profiles_path(browser), find_profile(browser, name)
    )
    if profile_path is None:
        raise Exception("Could not find profile path")
    return profile_path.joinpath(file if file else "")


def remove_profile(args: Namespace) -> None:
    profile_home = firefox_profiles_path(args.browser)
    profile_path = get_path_from_profile(
        profile_home, find_profile(args.browser, args.profile)
    )
    if profile_path is None:
        raise Exception("Could not find profile path")

    cfg = ConfigParser()
    cfg.optionxform = lambda option: option  # type: ignore
    cfg.read(profile_home.joinpath("profiles.ini"))
    for section in cfg.sections():
        if profile_path == get_path_from_profile(profile_home, cfg[section]):
            cfg.remove_section(section)
    with open(os.path.join(profile_home, "profiles.ini"), "w") as f:
        cfg.write(f, space_around_delimiters=False)
    shutil.rmtree(profile_path)


def extract(args: Namespace) -> None:
    with open(
        get_profile_path(args.browser, args.profile, args.file), "rb"
    ) as f:
        b = f.read()
        if b[:8] == b"mozLz40\0":
            b = lz4.block.decompress(b[8:])
        sys.stdout.buffer.write(b)


def compress(args: Namespace) -> None:
    content = sys.stdin.read()
    with open(
        get_profile_path(args.browser, args.profile, args.file), "wb"
    ) as f:
        f.write(b"mozLz40\0" + lz4.block.compress(content.encode("utf-8")))


def get_path(args: Namespace) -> None:
    print(get_profile_path(args.browser, args.profile, args.file))


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-P", "--profile")
    parser.add_argument(
        "-b",
        "--browser",
        default="firefox",
        choices=browser_profile_dirs.keys(),
    )
    subparsers = parser.add_subparsers()
    parser_get_path = subparsers.add_parser("remove_profile")
    parser_get_path.set_defaults(func=remove_profile)
    parser_extract = subparsers.add_parser("extract")
    parser_extract.set_defaults(func=extract)
    parser_extract.add_argument("file")
    parser_compress = subparsers.add_parser("compress")
    parser_compress.set_defaults(func=compress)
    parser_compress.add_argument("file")
    parser_get_path = subparsers.add_parser("get_path")
    parser_get_path.set_defaults(func=get_path)
    parser_get_path.add_argument("file", nargs="?", default="")
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

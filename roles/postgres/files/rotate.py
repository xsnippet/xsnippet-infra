#!/usr/bin/python

"""Rotate backup files in a given directory.

Implements a primitive FIFO backup rotation strategy by keeping N most recent backup files. The
order is defined by sorting the file names lexicographically: the files that appear later in
the sorted list are considered to be newer.
"""

import argparse
import dataclasses
import pathlib
import typing


@dataclasses.dataclass(order=True)
class Backup:
    path: pathlib.Path
    size: int


class Args(typing.Protocol):
    keep: int
    dir: pathlib.Path
    pattern: str
    no_dry_run: bool


def non_negative_int(str_value: str) -> int:
    value = int(str_value)
    if value < 0:
        raise argparse.ArgumentTypeError(f"Value must be non-negative: {value} < 0")

    return value


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-n",
        "--keep",
        required=True,
        type=non_negative_int,
        help="Keep this many most recent backup files",
    )
    parser.add_argument(
        "-d", "--dir", type=pathlib.Path, help="Path to the directory with backup files"
    )
    parser.add_argument(
        "-p",
        "--pattern",
        type=str,
        default="*",
        help="Only consider files that match this glob pattern",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually remove the rotated files",
    )

    namespace = parser.parse_args()
    return typing.cast(Args, namespace)


def rotate(
    dir: pathlib.Path,
    keep: int,
    pattern: str = "*",
) -> tuple[list[Backup], list[Backup]]:
    """Scan a directory and return a pair of lists: files to be kept, and files to be removed."""

    backups = sorted(
        (
            Backup(path=entry, size=entry.stat().st_size)
            for entry in dir.glob(pattern)
            if entry.is_file()
        ),
        reverse=True,
    )

    to_keep = backups[:keep]
    to_remove = backups[keep:]

    return (to_keep, to_remove)


def cleanup(to_keep: list[Backup], to_remove: list[Backup], *, dry_run: bool = True):
    """Delete old backup files and print disk space usage stats."""

    used_space = sum(backup.size for backup in to_keep)
    freed_space = sum(backup.size for backup in to_remove)

    if dry_run:
        print("Dry run. No changes will be made.\n")
    else:
        for backup in to_remove:
            backup.path.unlink()

    print(f"Used space: {len(to_keep)} files, {used_space} bytes")
    print(f"Freed space: {len(to_remove)} files, {freed_space} bytes")


def main():
    args = parse_args()

    to_keep, to_remove = rotate(args.dir, args.keep, args.pattern)
    cleanup(to_keep, to_remove, dry_run=not args.no_dry_run)


if __name__ == "__main__":
    main()

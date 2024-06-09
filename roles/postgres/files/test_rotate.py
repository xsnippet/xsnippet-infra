import pathlib
import subprocess

import pytest


EXPECTED_FILES = [
    "2024-06-27.tar.gz",
    "2024-06-28.tar.gz",
    "2024-06-29.tar.gz",
    "2024-06-30.tar.gz",
    "2024-07-01.tar.gz",
    "2024-07-02.tar.gz",
    "2024-07-03.tar.gz",
    "2024-07-08.tar.gz",
    "2024-07-09.tar.gz",
]


@pytest.fixture
def backups(tmp_path: pathlib.Path):
    for filename in EXPECTED_FILES:
        (tmp_path / filename).write_text(filename)

    assert sorted(item.name for item in tmp_path.glob("*")) == EXPECTED_FILES
    return tmp_path


@pytest.fixture
def no_backups(tmp_path: pathlib.Path):
    assert sorted(item.name for item in tmp_path.glob("*")) == []
    return tmp_path


def test_normal_invocation(backups: pathlib.Path):
    subprocess.check_call(
        ["rotate.py", "--no-dry-run", "--keep", "3", "--dir", backups]
    )
    assert sorted(item.name for item in backups.glob("*")) == [
        "2024-07-03.tar.gz",
        "2024-07-08.tar.gz",
        "2024-07-09.tar.gz",
    ]


def test_normal_invocation_is_idempotent(backups: pathlib.Path):
    subprocess.check_call(
        ["rotate.py", "--no-dry-run", "--keep", "3", "--dir", backups]
    )
    subprocess.check_call(
        ["rotate.py", "--no-dry-run", "--keep", "3", "--dir", backups]
    )
    subprocess.check_call(
        ["rotate.py", "--no-dry-run", "--keep", "3", "--dir", backups]
    )
    assert sorted(item.name for item in backups.glob("*")) == [
        "2024-07-03.tar.gz",
        "2024-07-08.tar.gz",
        "2024-07-09.tar.gz",
    ]


def test_dry_run_invocation(backups: pathlib.Path):
    subprocess.check_call(["rotate.py", "--keep", "3", "--dir", backups])
    assert sorted(item.name for item in backups.glob("*")) == EXPECTED_FILES


def test_keep_zero(backups: pathlib.Path):
    subprocess.check_call(
        ["rotate.py", "--no-dry-run", "--keep", "0", "--dir", backups]
    )
    assert sorted(item.name for item in backups.glob("*")) == []


def test_keep_negative(backups: pathlib.Path):
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call(
            ["rotate.py", "--no-dry-run", "--keep", "-1", "--dir", backups]
        )


def test_keep_more_than_files(backups: pathlib.Path):
    subprocess.check_call(
        ["rotate.py", "--no-dry-run", "--keep", "100", "--dir", backups]
    )
    assert sorted(item.name for item in backups.glob("*")) == EXPECTED_FILES


def test_keep_pattern(backups):
    subprocess.check_call(
        [
            "rotate.py",
            "--no-dry-run",
            "--keep",
            "1",
            "--dir",
            backups,
            "--pattern",
            "2024-06*tar.gz",
        ]
    )
    assert sorted(item.name for item in backups.glob("*")) == [
        "2024-06-30.tar.gz",
        "2024-07-01.tar.gz",
        "2024-07-02.tar.gz",
        "2024-07-03.tar.gz",
        "2024-07-08.tar.gz",
        "2024-07-09.tar.gz",
    ]


def test_keep_pattern_does_not_match_anything(backups):
    subprocess.check_call(
        [
            "rotate.py",
            "--no-dry-run",
            "--keep",
            "1",
            "--dir",
            backups,
            "--pattern",
            "2024-08*tar.gz",
        ]
    )
    assert sorted(item.name for item in backups.glob("*")) == EXPECTED_FILES

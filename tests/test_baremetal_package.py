# Copyright 2026 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

"""
Unit tests for the baremetal tar package contents.

These tests verify that the baremetal.tar produced by cd-baremtal.yaml contains
all required paths used by the OCI container (package/Dockerfile).

No Docker, Splunk, or network access required — runs anywhere with Python + GNU tar.
"""

import os
import re
import subprocess
import tarfile
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories syslog-ng.conf @include patterns resolve to (non-local/ ones must ship in the tar).
# if the file changes, update this list.
SYSLOG_NG_REQUIRED_DIRS = [
    "conf.d/conflib",
    "conf.d/destinations",
    "conf.d/enrich",
    "conf.d/log_paths/0",
    "conf.d/log_paths/2",
    "conf.d/plugin",
    "conf.d/sc4slib",
    "conf.d/sources",
]

# Files that must exist at the root of the extracted tar (i.e. in /etc/syslog-ng).
REQUIRED_TOP_LEVEL_FILES = [
    "syslog-ng.conf",
    "VERSION",
    "requirements.txt",
    "entrypoint.sh",
    "healthcheck.sh",
    "healthcheck.py",
    "source_ports_validator.py",
]

# Directories that must exist at root level.
REQUIRED_TOP_LEVEL_DIRS = [
    "pylib",
    "context_templates",
    "local_config",
    "test_parsers",
]

# These dirs must NOT appear at the top level — they belong under conf.d/.
# Their presence at root was the exact symptom of the v3.45.0 regression.
DIRS_THAT_MUST_NOT_BE_AT_ROOT = [
    "destinations",
    "enrich",
    "log_paths",
    "sources",
    "sc4slib",
    "plugin",
    "conflib",
]


def build_baremetal_tar(dest: str) -> None:
    """Replicate the exact tar commands from cd-baremtal.yaml."""
    cmds = [
        ["tar", "rvf", dest, "-C", "package/etc", "."],
        ["tar", "rvf", dest, "-C", ".", "pyproject.toml"],
        ["tar", "rvf", dest, "-C", ".", "poetry.lock"],
        ["tar", "rvf", dest, "-C", "package/sbin", "."],
        ["tar", "rvf", dest, "--transform", r"s,^\.,conf.d,", "-C", "package/shared/conf.d", "."],
        ["tar", "rvf", dest, "--transform", r"s,^\.,conf.d/conflib,", "-C", "package/shared/addons", "."],
        ["tar", "rvf", dest, "-C", "package/shared", "pylib"],
        ["tar", "rvf", dest, "-C", "package/shared", "context_templates"],
        ["tar", "rvf", dest, "-C", "package/shared", "local_config"],
        ["tar", "rvf", dest, "-C", "package/shared", "test_parsers"],
    ]
    for cmd in cmds:
        subprocess.run(cmd, cwd=REPO_ROOT, check=True, capture_output=True)


def is_gnu_tar() -> bool:
    result = subprocess.run(["tar", "--version"], capture_output=True, text=True)
    return "GNU tar" in result.stdout


def _collect_source_files(src_dir: str) -> set:
    return {
        os.path.relpath(os.path.join(r, f), src_dir)
        for r, _, files in os.walk(src_dir)
        for f in files
        if not f.endswith(".pyc") and "__pycache__" not in r
    }


# Fixtures — build once per test session
@pytest.fixture(scope="module")
def baremetal_tar(tmp_path_factory):
    if not is_gnu_tar():
        pytest.skip("GNU tar required (CI runs Ubuntu; use Docker locally)")

    tar_path = str(tmp_path_factory.mktemp("baremetal") / "baremetal.tar")
    req_path = os.path.join(REPO_ROOT, "package", "etc", "requirements.txt")
    if not os.path.exists(req_path):
        open(req_path, "w").close()

    build_baremetal_tar(tar_path)
    return tar_path


@pytest.fixture(scope="module")
def extracted_tar(baremetal_tar, tmp_path_factory):
    """Simulate: tar xf baremetal.tar -C /etc/syslog-ng"""
    extract_dir = str(tmp_path_factory.mktemp("extracted"))
    with tarfile.open(baremetal_tar) as tf:
        tf.extractall(extract_dir)
    return extract_dir


@pytest.fixture(scope="module")
def tar_paths(baremetal_tar):
    """Set of all entry names inside the tar."""
    with tarfile.open(baremetal_tar) as tf:
        return {m.name for m in tf.getmembers()}


# 1. Size sanity test — catches a completely empty package
def test_tar_size_indicates_parsers_are_present(baremetal_tar):
    """
    Because all parsers were missing.
    A correct package must be larger than 500KB.
    """
    size = os.path.getsize(baremetal_tar)
    assert size > 500_000, (
        f"Tar is only {size} bytes — parsers are almost certainly missing. "
        "Expected >500KB for a complete package."
    )


# 2. Required top-level files — things syslog-ng and the entrypoint need at boot
@pytest.mark.parametrize("filename", REQUIRED_TOP_LEVEL_FILES)
def test_required_file_present_after_extraction(extracted_tar, filename):
    """Each of these files is referenced by entrypoint.sh or syslog-ng.conf at startup."""
    full_path = os.path.join(extracted_tar, filename)
    assert os.path.isfile(full_path), (
        f"Required file '{filename}' is missing from the extracted package. "
        "A baremetal install would fail to start without it."
    )


@pytest.mark.parametrize("dirname", REQUIRED_TOP_LEVEL_DIRS)
def test_required_directory_present_after_extraction(extracted_tar, dirname):
    full_path = os.path.join(extracted_tar, dirname)
    assert os.path.isdir(full_path), (
        f"Required directory '{dirname}' is missing from the extracted package."
    )


# 3. syslog-ng.conf @include coverage — every non-local include dir must exist
@pytest.mark.parametrize("required_dir", SYSLOG_NG_REQUIRED_DIRS)
def test_syslog_ng_include_dir_exists(extracted_tar, required_dir):
    """
    syslog-ng.conf has @include directives for each of these directories.
    If any are missing, syslog-ng will fail to start on a baremetal install.
    """
    full_path = os.path.join(extracted_tar, required_dir)
    assert os.path.isdir(full_path), (
        f"Directory '{required_dir}' is referenced by an @include in syslog-ng.conf "
        "but is missing from the package. syslog-ng will refuse to start."
    )


def test_syslog_ng_include_dirs_are_not_empty(extracted_tar):
    """
    Each @include directory that ships in the tar must contain at least one .conf file.
    An empty directory means syslog-ng starts but has no parsers / destinations / log paths.
    """
    empty = []
    for required_dir in SYSLOG_NG_REQUIRED_DIRS:
        dir_path = os.path.join(extracted_tar, required_dir)
        if not os.path.isdir(dir_path):
            continue  # already caught by test_syslog_ng_include_dir_exists
        conf_files = [
            f for _, _, files in os.walk(dir_path)
            for f in files if f.endswith(".conf")
        ]
        if not conf_files:
            empty.append(required_dir)
    assert not empty, (
        f"These @include directories exist but contain no .conf files: {empty}. "
        "syslog-ng will start but silently have no parsers or routing."
    )


# 4. Addon test — every addon in shared/addons must land in conf.d/conflib
def test_every_addon_dir_present_in_conflib(extracted_tar):
    """
    package/shared/addons/<vendor>/ must map to conf.d/conflib/<vendor>/ in the tar.
    A missing vendor means all its log sources go unrecognised on a baremetal host.
    """
    addons_src = os.path.join(REPO_ROOT, "package", "shared", "addons")
    conflib_dst = os.path.join(extracted_tar, "conf.d", "conflib")

    src_vendors = {
        d for d in os.listdir(addons_src)
        if os.path.isdir(os.path.join(addons_src, d))
    }
    dst_vendors = {
        d for d in os.listdir(conflib_dst)
        if os.path.isdir(os.path.join(conflib_dst, d))
    }

    missing = src_vendors - dst_vendors
    assert not missing, (
        f"These vendor addon dirs are in shared/addons but missing from conf.d/conflib: "
        f"{sorted(missing)}"
    )


def test_every_addon_conf_file_present_in_conflib(extracted_tar):
    """
    File-level check: every .conf file inside shared/addons must appear under conf.d/conflib.
    Catches partial copies where the directory exists but files were not transferred.
    """
    addons_src = os.path.join(REPO_ROOT, "package", "shared", "addons")
    conflib_dst = os.path.join(extracted_tar, "conf.d", "conflib")

    src_files = _collect_source_files(addons_src)
    dst_files = _collect_source_files(conflib_dst)

    missing = {f for f in src_files if f.endswith(".conf")} - dst_files
    assert not missing, (
        f"These addon .conf files are missing from conf.d/conflib in the tar "
        f"({len(missing)} files): {sorted(missing)[:15]}"
    )


def test_conflib_has_expected_minimum_addon_count(extracted_tar):
    """
    Guard against silent truncation: conflib must have at least as many subdirectories
    as shared/addons (plus shared/conf.d/conflib which also merges in).
    """
    addons_src = os.path.join(REPO_ROOT, "package", "shared", "addons")
    conflib_dst = os.path.join(extracted_tar, "conf.d", "conflib")

    expected_min = sum(
        1 for d in os.listdir(addons_src)
        if os.path.isdir(os.path.join(addons_src, d))
    )
    actual = sum(
        1 for d in os.listdir(conflib_dst)
        if os.path.isdir(os.path.join(conflib_dst, d))
    )
    assert actual >= expected_min, (
        f"conf.d/conflib has {actual} subdirs but shared/addons has {expected_min}. "
        "Some addons were silently dropped."
    )


# 5. shared/conf.d must mirror conf.d/ in the tar
def test_conf_d_top_level_dirs_all_present(extracted_tar):
    """Every subdir of shared/conf.d must appear directly under conf.d/ in the tar."""
    conf_d_src = os.path.join(REPO_ROOT, "package", "shared", "conf.d")
    conf_d_dst = os.path.join(extracted_tar, "conf.d")

    src_dirs = {
        d for d in os.listdir(conf_d_src)
        if os.path.isdir(os.path.join(conf_d_src, d))
    }
    dst_dirs = {
        d for d in os.listdir(conf_d_dst)
        if os.path.isdir(os.path.join(conf_d_dst, d))
    }

    missing = src_dirs - dst_dirs
    assert not missing, (
        f"These conf.d subdirs from shared/conf.d are missing from the tar: {sorted(missing)}"
    )


def test_conf_d_conf_files_all_present(extracted_tar):
    """File-level check: every .conf in shared/conf.d must appear under conf.d/ in the tar."""
    conf_d_src = os.path.join(REPO_ROOT, "package", "shared", "conf.d")
    conf_d_dst = os.path.join(extracted_tar, "conf.d")

    src_files = {f for f in _collect_source_files(conf_d_src) if f.endswith(".conf")}
    dst_files = _collect_source_files(conf_d_dst)

    missing = src_files - dst_files
    assert not missing, (
        f"These conf.d .conf files are missing from the tar "
        f"({len(missing)} files): {sorted(missing)[:15]}"
    )


# 6. shared/ subdirs land at the correct root paths (Dockerfile layout parity)
@pytest.mark.parametrize("shared_subdir,tar_root", [
    ("pylib",             "pylib"),
    ("context_templates", "context_templates"),
    ("local_config",      "local_config"),
    ("test_parsers",      "test_parsers"),
])
def test_shared_subdir_file_count_matches_source(extracted_tar, shared_subdir, tar_root):
    """
    Every file in package/shared/<subdir> must appear at <tar_root>/ in the extracted package.
    This catches the case where a directory exists but its contents were not copied.
    """
    src = os.path.join(REPO_ROOT, "package", "shared", shared_subdir)
    dst = os.path.join(extracted_tar, tar_root)

    src_files = _collect_source_files(src)
    dst_files = _collect_source_files(dst)

    missing = src_files - dst_files
    assert not missing, (
        f"Files missing from {tar_root}/ in the tar ({len(missing)} files): "
        f"{sorted(missing)[:10]}"
    )


# 7. Regression guard — broken layout
@pytest.mark.parametrize("dirname", DIRS_THAT_MUST_NOT_BE_AT_ROOT)
def test_parser_dirs_not_leaked_to_root(extracted_tar, dirname):
    """
    Shared/conf.d content landed at the top level (e.g. ./destinations, ./enrich)
    because the --transform flag was missing. These dirs must only exist under conf.d/, never root.
    """
    leaked_path = os.path.join(extracted_tar, dirname)
    assert not os.path.exists(leaked_path), (
        f"'{dirname}' exists at the root of the extracted package — "
        "this is the v3.45.0 regression where conf.d content landed at the wrong path. "
        "Check the --transform flags in cd-baremtal.yaml."
    )


# 8. pylib integrity — Python modules that entrypoint.sh runs directly
@pytest.mark.parametrize("pyfile", [
    "parser_source_cache.py",  # called by entrypoint.sh on every startup
    "parser_vps_cache.py",
    "log_utils.py",
])
def test_critical_pylib_file_present(extracted_tar, pyfile):
    """
    entrypoint.sh sets PYTHONPATH=/etc/syslog-ng/pylib and calls parser_source_cache.py
    at startup. If these are missing the daemon exits immediately.
    """
    full_path = os.path.join(extracted_tar, "pylib", pyfile)
    assert os.path.isfile(full_path), (
        f"pylib/{pyfile} is missing. entrypoint.sh calls this file at startup — "
        "a baremetal install will exit immediately without it."
    )


# 9. syslog-ng.conf references VERSION — VERSION must be a non-empty file
def test_version_file_is_not_empty(extracted_tar):
    version_path = os.path.join(extracted_tar, "VERSION")
    assert os.path.isfile(version_path), "VERSION file is missing"
    content = open(version_path).read().strip()
    assert content, "VERSION file exists but is empty"
    assert re.match(r"^\d+\.\d+\.\d+", content), (
        f"VERSION file does not look like a semver string: '{content}'"
    )


# 10. No duplicate entries in the tar
def test_no_duplicate_tar_entries(baremetal_tar):
    """Duplicate entries in a tar cause unpredictable extraction — last write wins."""
    with tarfile.open(baremetal_tar) as tf:
        all_names = [m.name for m in tf.getmembers() if not m.isdir()]
    seen = {}
    duplicates = []
    for name in all_names:
        if name in seen:
            duplicates.append(name)
        seen[name] = True
    assert not duplicates, (
        f"Tar contains {len(duplicates)} duplicate entries. "
        f"First few: {duplicates[:10]}"
    )

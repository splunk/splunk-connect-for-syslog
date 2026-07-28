# Copyright 2026 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

"""
Verify the baremetal.tar built by cd-baremtal.yaml contains the correct layout.

Run in CI:   BAREMETAL_TAR=/tmp/baremetal.tar pytest tests/test_baremetal_package.py -v
Run locally: build the tar first (see docs/gettingstarted/byoe-rhel8.md), then set BAREMETAL_TAR.
"""

import os
import re
import tarfile
import pytest

pytestmark = pytest.mark.baremetal

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# @include dirs in syslog-ng.conf that must ship in the package (non-local/ only).
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

REQUIRED_TOP_LEVEL_FILES = [
    "syslog-ng.conf",
    "VERSION",
    "requirements.txt",
    "entrypoint.sh",
    "healthcheck.sh",
    "healthcheck.py",
    "source_ports_validator.py",
]

REQUIRED_TOP_LEVEL_DIRS = [
    "pylib",
    "context_templates",
    "local_config",
    "test_parsers",
]


def _collect_source_files(src_dir):
    return {
        os.path.relpath(os.path.join(r, f), src_dir)
        for r, _, files in os.walk(src_dir)
        for f in files
        if not f.endswith(".pyc") and "__pycache__" not in r
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def baremetal_tar():
    path = os.environ.get("BAREMETAL_TAR")
    if not path:
        pytest.fail(
            "BAREMETAL_TAR env var is not set. "
            "Build the tar first (see cd-baremtal.yaml), then re-run: "
            "BAREMETAL_TAR=/tmp/baremetal.tar pytest tests/test_baremetal_package.py"
        )
    if not os.path.isfile(path):
        pytest.fail(f"BAREMETAL_TAR points to a non-existent file: {path}")
    return path


@pytest.fixture(scope="module")
def extracted_tar(baremetal_tar, tmp_path_factory):
    extract_dir = str(tmp_path_factory.mktemp("extracted"))
    with tarfile.open(baremetal_tar) as tf:
        tf.extractall(extract_dir)
    return extract_dir


# ---------------------------------------------------------------------------
# 1. Required top-level paths
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filename", REQUIRED_TOP_LEVEL_FILES)
def test_required_file_present(extracted_tar, filename):
    assert os.path.isfile(os.path.join(extracted_tar, filename)), \
        f"Required file '{filename}' is missing from the package."


@pytest.mark.parametrize("dirname", REQUIRED_TOP_LEVEL_DIRS)
def test_required_directory_present(extracted_tar, dirname):
    assert os.path.isdir(os.path.join(extracted_tar, dirname)), \
        f"Required directory '{dirname}' is missing from the package."


# ---------------------------------------------------------------------------
# 2. syslog-ng.conf @include coverage
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("required_dir", SYSLOG_NG_REQUIRED_DIRS)
def test_syslog_ng_include_dir_exists(extracted_tar, required_dir):
    assert os.path.isdir(os.path.join(extracted_tar, required_dir)), \
        f"'{required_dir}' is in syslog-ng.conf @include but missing — syslog-ng will not start."


def test_syslog_ng_include_dirs_are_not_empty(extracted_tar):
    empty = [
        d for d in SYSLOG_NG_REQUIRED_DIRS
        if os.path.isdir(os.path.join(extracted_tar, d))
        and not any(
            f.endswith(".conf")
            for _, _, files in os.walk(os.path.join(extracted_tar, d))
            for f in files
        )
    ]
    assert not empty, f"@include dirs exist but contain no .conf files: {empty}"


# ---------------------------------------------------------------------------
# 3. Addon parity — shared/addons must land in conf.d/conflib
# ---------------------------------------------------------------------------

def test_every_addon_dir_present_in_conflib(extracted_tar):
    addons_src = os.path.join(REPO_ROOT, "package", "shared", "addons")
    conflib_dst = os.path.join(extracted_tar, "conf.d", "conflib")
    src = {d for d in os.listdir(addons_src) if os.path.isdir(os.path.join(addons_src, d))}
    dst = {d for d in os.listdir(conflib_dst) if os.path.isdir(os.path.join(conflib_dst, d))}
    missing = src - dst
    assert not missing, f"Addon dirs missing from conf.d/conflib: {sorted(missing)}"


def test_every_addon_conf_file_present_and_non_empty(extracted_tar):
    addons_src = os.path.join(REPO_ROOT, "package", "shared", "addons")
    conflib_dst = os.path.join(extracted_tar, "conf.d", "conflib")

    src_files = {f for f in _collect_source_files(addons_src) if f.endswith(".conf")}
    dst_files = _collect_source_files(conflib_dst)

    missing = src_files - dst_files
    assert not missing, \
        f"Addon .conf files missing from conf.d/conflib ({len(missing)}): {sorted(missing)[:15]}"

    empty = [
        f for f in src_files
        if os.path.getsize(os.path.join(conflib_dst, f)) == 0
    ]
    assert not empty, f"Addon .conf files are present but empty: {sorted(empty)[:10]}"


def test_conflib_subdir_count_not_less_than_addons(extracted_tar):
    addons_src = os.path.join(REPO_ROOT, "package", "shared", "addons")
    conflib_dst = os.path.join(extracted_tar, "conf.d", "conflib")
    expected_min = sum(1 for d in os.listdir(addons_src) if os.path.isdir(os.path.join(addons_src, d)))
    actual = sum(1 for d in os.listdir(conflib_dst) if os.path.isdir(os.path.join(conflib_dst, d)))
    assert actual >= expected_min, \
        f"conf.d/conflib has {actual} subdirs, shared/addons has {expected_min} — addons were dropped."


# ---------------------------------------------------------------------------
# 4. conf.d structure parity with shared/conf.d
# ---------------------------------------------------------------------------

def test_conf_d_dirs_all_present(extracted_tar):
    src = os.path.join(REPO_ROOT, "package", "shared", "conf.d")
    dst = os.path.join(extracted_tar, "conf.d")
    src_dirs = {d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d))}
    dst_dirs = {d for d in os.listdir(dst) if os.path.isdir(os.path.join(dst, d))}
    missing = src_dirs - dst_dirs
    assert not missing, f"conf.d subdirs missing from tar: {sorted(missing)}"


def test_conf_d_files_all_present(extracted_tar):
    src = os.path.join(REPO_ROOT, "package", "shared", "conf.d")
    dst = os.path.join(extracted_tar, "conf.d")
    src_files = {f for f in _collect_source_files(src) if f.endswith(".conf")}
    dst_files = _collect_source_files(dst)
    missing = src_files - dst_files
    assert not missing, \
        f"conf.d .conf files missing from tar ({len(missing)}): {sorted(missing)[:15]}"


# ---------------------------------------------------------------------------
# 5. shared/ subdirs land at correct root paths
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("shared_subdir,tar_root", [
    ("pylib",             "pylib"),
    ("context_templates", "context_templates"),
    ("local_config",      "local_config"),
    ("test_parsers",      "test_parsers"),
])
def test_shared_subdir_files_all_present(extracted_tar, shared_subdir, tar_root):
    src = os.path.join(REPO_ROOT, "package", "shared", shared_subdir)
    dst = os.path.join(extracted_tar, tar_root)
    missing = _collect_source_files(src) - _collect_source_files(dst)
    assert not missing, \
        f"Files missing from {tar_root}/ ({len(missing)}): {sorted(missing)[:10]}"


# ---------------------------------------------------------------------------
# 6. pylib files
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pyfile", [
    "parser_source_cache.py",
    "parser_vps_cache.py",
    "log_utils.py",
])
def test_critical_pylib_file_present(extracted_tar, pyfile):
    assert os.path.isfile(os.path.join(extracted_tar, "pylib", pyfile)), \
        f"pylib/{pyfile} is missing — entrypoint.sh will exit on startup."


# ---------------------------------------------------------------------------
# 7. VERSION is a valid semver string
# ---------------------------------------------------------------------------

def test_version_file_is_valid_semver(extracted_tar):
    path = os.path.join(extracted_tar, "VERSION")
    assert os.path.isfile(path), "VERSION file is missing"
    content = open(path).read().strip()
    assert re.match(r"^\d+\.\d+\.\d+", content), \
        f"VERSION does not look like semver: '{content}'"


# ---------------------------------------------------------------------------
# 8. No duplicate file entries in the tar
# ---------------------------------------------------------------------------

def test_no_duplicate_tar_entries(baremetal_tar):
    with tarfile.open(baremetal_tar) as tf:
        names = [m.name for m in tf.getmembers() if not m.isdir()]
    seen, duplicates = set(), []
    for name in names:
        if name in seen:
            duplicates.append(name)
        seen.add(name)
    assert not duplicates, \
        f"Tar has {len(duplicates)} duplicate entries: {duplicates[:10]}"

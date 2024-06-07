"""Test Version object and cast_version utility function."""

import pytest
from pydantic import ValidationError

from polus.tools.plugins._plugins.io import Version

GOOD_VERSIONS = [
    "1.2.3",
    "1.4.7-rc1",
    "4.1.5",
    "12.8.3",
    "10.2.0",
    "2.2.3-dev5",
    "0.3.4",
    "0.2.34-rc23",
]
BAD_VERSIONS = ["02.2.3", "002.2.3", "1.2", "1.0", "1.03.2", "23.3.03", "d.2.4"]


@pytest.mark.parametrize("ver", GOOD_VERSIONS, ids=GOOD_VERSIONS)
def test_version(ver):
    """Test Version pydantic model."""
    assert isinstance(Version(ver), Version)


@pytest.mark.parametrize("ver", BAD_VERSIONS, ids=BAD_VERSIONS)
def test_bad_version1(ver):
    """Test ValidationError is raised for invalid versions."""
    with pytest.raises(ValidationError):
        assert isinstance(Version(ver), Version)


MAJOR_VERSION_EQUAL = ["2.4.3", "2.98.28", "2.1.2", "2.0.0", "2.4.0"]
MINOR_VERSION_EQUAL = ["1.3.3", "7.3.4", "98.3.12", "23.3.0", "1.3.5"]
PATCH_EQUAL = ["12.2.7", "2.3.7", "1.7.7", "7.7.7", "7.29.7"]


@pytest.mark.parametrize("ver", MAJOR_VERSION_EQUAL, ids=MAJOR_VERSION_EQUAL)
def test_major(ver):
    """Test major version."""
    assert Version(ver).major == 2


@pytest.mark.parametrize("ver", MINOR_VERSION_EQUAL, ids=MINOR_VERSION_EQUAL)
def test_minor(ver):
    """Test minor version."""
    assert Version(ver).minor == 3


@pytest.mark.parametrize("ver", PATCH_EQUAL, ids=PATCH_EQUAL)
def test_patch(ver):
    """Test patch version."""
    assert Version(ver).patch == 7


def test_gt1():
    """Test greater than operator."""
    assert Version("1.2.3") > Version("1.2.1")


def test_gt2():
    """Test greater than operator."""
    assert Version("5.7.3") > Version("5.6.3")


def test_st1():
    """Test less than operator."""
    assert Version("5.7.3") < Version("5.7.31")


def test_st2():
    """Test less than operator."""
    assert Version("1.0.2") < Version("2.0.2")


def test_eq1():
    """Test equality operator."""
    assert Version("1.3.3") == Version("1.3.3")


def test_eq2():
    """Test equality operator."""
    assert Version("5.4.3") == Version("5.4.3")


def test_eq3():
    """Test equality operator."""
    assert Version("1.3.3") != Version("1.3.8")


def test_eq_str1():
    """Test equality with str."""
    assert Version("1.3.3") == "1.3.3"


def test_lt_str1():
    """Test equality with str."""
    assert Version("1.3.3") < "1.5.3"


def test_gt_str1():
    """Test equality with str."""
    assert Version("4.5.10") > "4.5.9"


def test_eq_no_str():
    """Test equality with non-string."""
    with pytest.raises(TypeError):
        assert Version("1.3.3") == 1.3


@pytest.mark.parametrize(
    "ver",
    [
        "1.0.0",
        "1.0.1",
        "1.2.4",
        "0.2.3",
        "12.2.3",
        "0.2.1-alpha",
        "1.2.3-beta",
        "1.10.0",
        "1.10.2-alpha+232",
        "0.4.1-rc.1",
        "12.21.23-beta.12",
        "1.10.12-alpha.1+2322",
    ],
    ids=[
        "1.0.0",
        "1.0.1",
        "1.2.4",
        "0.2.3",
        "12.2.3",
        "0.2.1-alpha",
        "1.2.3-beta",
        "1.10.0",
        "1.10.2-alpha+232",
        "0.4.1-rc.1",
        "12.21.23-beta.12",
        "1.10.12-alpha.1+2322",
    ],
)
def test_version_good_1(ver):
    """Test Correct Versions.

    Added after new regex implementation.
    """
    v = Version(ver)
    assert isinstance(v, Version)


@pytest.mark.parametrize(
    "ver",
    [
        "1.02.0",
        "1.0",
        "1.2.04",
        "04.2.3",
        "12.2.alpha",
        "0.2.1.alpha",
        "10",
    ],
    ids=[
        "1.02.0",
        "1.0",
        "1.2.04",
        "04.2.3",
        "12.2.alpha",
        "0.2.1.alpha",
        "10",
    ],
)
def test_version_bad_1(ver):
    """Test Incorrect Versions.

    Added after new regex implementation.
    """
    with pytest.raises(ValueError):
        Version(ver)


def test_prerelease_version_sort():
    """Test prerelease version sorting."""
    versions_sorted = [
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-alpha.beta",
        "1.0.0-beta",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
    ]

    versions_to_sort = [
        "1.0.0-beta",
        "1.0.0",
        "1.0.0-alpha.1",
        "1.0.0-alpha",
        "1.0.0-beta.2",
        "1.0.0-alpha.beta",
        "1.0.0-rc.1",
        "1.0.0-beta.11",
    ]
    versions_sorted = [Version(v) for v in versions_sorted]
    versions_to_sort = [Version(v) for v in versions_to_sort]
    assert sorted(versions_to_sort) == versions_sorted


@pytest.mark.parametrize(
    "ver",
    [("1.3.3-alpha+123", "1.3.3-alpha+223"), ("1.3.3-alpha+123", "1.3.3-alpha")],
    ids=["1.3.3-alpha+123", "1.3.3"],
)
def test_lt_build_metadata(ver):
    """Test precedence with build metadata.

    In this case, `assert not A < B` is used
    since we are not checking that B is greater or equal
    to A, but we are checking that A is not smaller than B.
    """
    assert not Version(ver[0]) < Version(ver[1])  # pylint: disable=C0117


@pytest.mark.parametrize(
    "ver",
    [
        "1.0.0",
        "1.0.1",
        "1.2.4",
        "0.2.3",
        "12.2.3",
        "0.2.1-alpha",
        "1.2.3-beta",
        "1.10.0",
        "1.10.2-alpha+232",
        "0.4.1-rc.1",
        "12.21.23-beta.12",
        "1.10.12-alpha.1+2322",
    ],
    ids=[
        "1.0.0",
        "1.0.1",
        "1.2.4",
        "0.2.3",
        "12.2.3",
        "0.2.1-alpha",
        "1.2.3-beta",
        "1.10.0",
        "1.10.2-alpha+232",
        "0.4.1-rc.1",
        "12.21.23-beta.12",
        "1.10.12-alpha.1+2322",
    ],
)
def test_le(ver):
    """Test less than or equal operator."""
    assert ver <= Version("12.21.23-beta.12")


@pytest.mark.parametrize(
    "ver",
    [
        "1.0.0",
        "12.2.3",
        "0.2.1-alpha",
        "1.2.3-beta",
        "1.10.0",
        "1.10.2-alpha+232",
        "12.21.23-beta.12",
    ],
    ids=[
        "1.0.0",
        "12.2.3",
        "0.2.1-alpha",
        "1.2.3-beta",
        "1.10.0",
        "1.10.2-alpha+232",
        "12.21.23-beta.12",
    ],
)
def test_le_str(ver):
    """Test less than or equal operator with strings."""
    assert ver <= "12.21.23-beta.12"


@pytest.mark.parametrize(
    "ver",
    [
        "12.21.23-charlie",
        "12.21.23-charlie.10",
        "15.0.2",
        "12.21.24-beta.12",
        "12.21.24",
        "13.0.0",
        "12.21.23-beta.12",
    ],
    ids=[
        "12.21.23-charlie",
        "12.21.23-charlie.10",
        "15.0.2",
        "12.21.24-beta.12",
        "12.21.24",
        "13.0.0",
        "12.21.23-beta.12",
    ],
)
def test_ge(ver):
    """Test less than or equal operator."""
    assert ver >= Version("12.21.23-beta.12")


@pytest.mark.parametrize(
    "ver",
    [
        "12.21.23-charlie",
        "12.21.23-charlie.10",
        "15.0.2",
        "12.21.24-beta.12",
        "12.21.24",
        "13.0.0",
        "12.21.23-beta.12",
    ],
    ids=[
        "12.21.23-charlie",
        "12.21.23-charlie.10",
        "15.0.2",
        "12.21.24-beta.12",
        "12.21.24",
        "13.0.0",
        "12.21.23-beta.12",
    ],
)
def test_ge_str(ver):
    """Test less than or equal operator with strings."""
    assert ver >= "12.21.23-beta.12"

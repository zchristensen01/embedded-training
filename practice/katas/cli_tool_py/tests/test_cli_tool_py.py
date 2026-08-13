"""tests/test_cli_tool_py.py — FROZEN. Not edited during a drill.

Write every case yourself. AI may write fixtures plumbing; it may not write a case.
"""
import pytest


# TODO: a fixture that builds the thing under test and tears it down even on failure.
@pytest.fixture
def subject():
    raise NotImplementedError("build the fixture")


def test_TODO_rename_me(subject):
    assert False, "write a real case"

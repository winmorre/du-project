import pytest


def pytest_configure(config):
    pass


def pytest_runtest_setup(item):
    test_markers = [mark for mark in item.iter_markers(name="human_only")]

    if test_markers:
        pytest.skip("test must only be run by humans")

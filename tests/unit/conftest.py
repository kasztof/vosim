import os
import pytest


@pytest.fixture
def test_data_path():
    return os.path.abspath("tests/test_data/network.csv")

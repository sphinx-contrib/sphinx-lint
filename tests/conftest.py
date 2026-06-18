from pathlib import Path

import pytest


@pytest.fixture
def fixture_dir():
    return Path(__file__).resolve().parent / "fixtures"

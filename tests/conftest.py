import os

import pytest
from dotenv import load_dotenv


def pytest_configure() -> None:
    load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "http://localhost:8000")

import pytest


def pytest_addoption(parser):
    parser.addoption("--base_url", action="store", default=None, help="Base URL to test against")


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base_url")

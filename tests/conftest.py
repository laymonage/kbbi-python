import pytest

from kbbi import KBBI


@pytest.fixture(scope="session")
def bin():
    return KBBI("bin")


@pytest.fixture(scope="session")
def quo_vadis():
    return KBBI("quo vadis?")


@pytest.fixture(scope="session")
def civitas_academica():
    return KBBI("civitas academica")


@pytest.fixture(scope="session")
def khayal():
    return KBBI("khayal")


@pytest.fixture(scope="session")
def semakin():
    return KBBI("semakin")


@pytest.fixture(scope="session")
def makin():
    return KBBI("makin")


@pytest.fixture(scope="session")
def keratabasa():
    return KBBI("keratabasa")


@pytest.fixture(scope="session")
def tampak():
    return KBBI("tampak")


@pytest.fixture(scope="session")
def menjadikan():
    return KBBI("menjadikan")


@pytest.fixture(scope="session")
def lampir():
    return KBBI("lampir")


@pytest.fixture(scope="session")
def kan():
    return KBBI("kan")


@pytest.fixture(scope="session")
def me_():
    return KBBI("me-")


@pytest.fixture(scope="session")
def _kan():
    return KBBI("-kan")


@pytest.fixture(scope="session")
def _lah():
    return KBBI("-lah")

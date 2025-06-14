# server/services/helper_test.py

import shutil
import pytest

from server.services.helper import is_docker_available, wait_for_influxdb
import logging

fixture_logger = logging.getLogger("fixture")
fixture_logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def test_docker_binary_exists():
    """
    Verify that the 'docker' binary is actually on PATH.
    If this fails, your environment truly doesn't have Docker installed.
    """
    assert shutil.which("docker"), "docker binary not found on PATH"


@pytest.mark.skipif(
    not shutil.which("docker"),
    reason="docker binary not on PATH; skipping availability check",
)
def test_is_docker_available_true():
    """
    On a machine with Docker installed _and_ the daemon running,
    is_docker_available() should return True.
    """
    assert is_docker_available() is True


@pytest.mark.skipif(
    not is_docker_available(),
    reason="docker binary not on PATH; skipping availability check",
)
def test_can_connect_to_influxdb():
    """
    Test that we can connect to InfluxDB.
    """
    assert wait_for_influxdb("http://localhost:50247", "test_token", "test_org") is True

# server/services/helper_test.py
import shutil
import subprocess
from influxdb_client import InfluxDBClient
import time
import logging


def is_docker_available() -> bool:
    """
    Returns True if the 'docker' CLI is present on PATH and
    `docker info` succeeds within 2s; otherwise False.
    """
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return False

    try:
        subprocess.run(
            [docker_bin, "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2,
            check=True,
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


def wait_for_influxdb(
    url: str,
    token: str,
    org: str,
    max_retries: int = 10,
    backoff_base: int = 2,
) -> bool:
    """
    Wait until InfluxDB’s health endpoint reports 'pass',
    using exponential back-off.
    """
    logger.info("Waiting for InfluxDB to be ready at %s", url)
    for attempt in range(1, max_retries + 1):
        logger.debug("Attempt %d/%d to connect to InfluxDB", attempt, max_retries)
        try:
            client = InfluxDBClient(url=url, token=token, org=org)
            health = client.ping()
            client.close()
            logger.debug("Health response: %s", health)
            if health:
                logger.info("InfluxDB is healthy!")
                return True
        except Exception as e:
            logger.warning(
                "Attempt %d failed (%s); retrying in %d seconds",
                attempt,
                e,
                backoff_base ** (attempt - 1),
            )
        time.sleep(backoff_base ** (attempt - 1))

    logger.error("Failed to connect to InfluxDB after %d attempts", max_retries)
    return False

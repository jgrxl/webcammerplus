import logging
import socket
import time
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def is_docker_available() -> bool:
    """Check if Docker is available and responsive on the system.

    Returns:
        True if Docker daemon is available and responsive, False otherwise
    """
    try:
        import docker

        client = docker.from_env(timeout=10)

        # Test connection with a simple ping
        ping_result = client.ping()
        if ping_result:
            logger.debug("Docker daemon is available and responsive")
            return True
        else:
            logger.warning("Docker daemon ping failed")
            return False

    except ImportError:
        logger.debug("Docker Python client not installed")
        return False
    except Exception as e:
        logger.debug(f"Docker not available: {e}")
        return False


def wait_for_influxdb(
    url: str, token: str, org: str, timeout: int = 30, check_interval: float = 1.0
) -> bool:
    """Wait for InfluxDB to become healthy with robust connection handling.

    This function implements exponential backoff and comprehensive error handling
    to reliably detect when InfluxDB is ready for connections.

    Args:
        url: InfluxDB URL (e.g., 'http://localhost:8086')
        token: Authentication token
        org: Organization name (used for validation)
        timeout: Maximum time to wait in seconds (default: 30)
        check_interval: Initial interval between checks in seconds (default: 1.0)

    Returns:
        True if InfluxDB becomes healthy within timeout, False otherwise

    Raises:
        ValueError: If required parameters are invalid
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")
    if not token or not token.strip():
        raise ValueError("Token cannot be empty")
    if not org or not org.strip():
        raise ValueError("Organization cannot be empty")
    if timeout <= 0:
        raise ValueError(f"Timeout must be positive, got {timeout}")
    if check_interval <= 0:
        raise ValueError(f"Check interval must be positive, got {check_interval}")

    url = url.strip().rstrip("/")
    health_url = f"{url}/health"

    # Setup session with retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    headers = {"Authorization": f"Token {token}"}

    logger.info(
        f"Waiting for InfluxDB at {url} to become healthy (timeout: {timeout}s)"
    )

    start_time = time.time()
    attempt = 0
    current_interval = check_interval

    while time.time() - start_time < timeout:
        attempt += 1

        try:
            logger.debug(f"Health check attempt {attempt} - {health_url}")

            response = session.get(health_url, headers=headers, timeout=5)

            if response.status_code == 200:
                try:
                    data = response.json()
                    status = data.get("status")

                    if status == "pass":
                        elapsed = time.time() - start_time
                        logger.info(
                            f"InfluxDB is healthy after {elapsed:.1f}s ({attempt} attempts)"
                        )
                        return True
                    else:
                        logger.debug(f"InfluxDB status: {status} (not yet healthy)")

                except ValueError as e:
                    logger.warning(
                        f"Invalid JSON response from InfluxDB health endpoint: {e}"
                    )

            else:
                logger.debug(f"Health check returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            logger.debug(f"Connection refused to {url} (attempt {attempt})")
        except requests.exceptions.Timeout:
            logger.debug(f"Timeout connecting to {url} (attempt {attempt})")
        except Exception as e:
            logger.warning(f"Unexpected error during health check: {e}")

        # Exponential backoff with jitter
        time.sleep(min(current_interval, 5.0))
        current_interval *= 1.2  # Gradual increase

    elapsed = time.time() - start_time
    logger.warning(
        f"InfluxDB health check timed out after {elapsed:.1f}s ({attempt} attempts)"
    )
    return False


def check_port_open(host: str, port: int, timeout: float = 5.0) -> bool:
    """Check if a TCP port is open and accepting connections.

    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Connection timeout in seconds

    Returns:
        True if port is open, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception as e:
        logger.debug(f"Port check failed for {host}:{port} - {e}")
        return False


def parse_database_url(url: str) -> Tuple[str, int, Optional[str]]:
    """Parse a database URL into components.

    Args:
        url: Database URL (e.g., 'http://localhost:8086')

    Returns:
        Tuple of (host, port, scheme)

    Raises:
        ValueError: If URL format is invalid
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")

    url = url.strip()

    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)

        if not parsed.hostname:
            raise ValueError(f"Invalid URL format: {url}")

        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 8086)
        scheme = parsed.scheme

        return host, port, scheme

    except Exception as e:
        raise ValueError(f"Failed to parse URL '{url}': {e}")


def wait_for_service(
    host: str, port: int, timeout: int = 30, check_interval: float = 1.0
) -> bool:
    """Wait for a network service to become available.

    Args:
        host: Service hostname or IP
        port: Service port number
        timeout: Maximum time to wait in seconds
        check_interval: Interval between checks in seconds

    Returns:
        True if service becomes available, False if timeout
    """
    logger.info(f"Waiting for service at {host}:{port} (timeout: {timeout}s)")

    start_time = time.time()
    attempt = 0

    while time.time() - start_time < timeout:
        attempt += 1

        if check_port_open(host, port):
            elapsed = time.time() - start_time
            logger.info(f"Service at {host}:{port} is available after {elapsed:.1f}s")
            return True

        logger.debug(f"Service check attempt {attempt} failed")
        time.sleep(check_interval)

    elapsed = time.time() - start_time
    logger.warning(f"Service at {host}:{port} not available after {elapsed:.1f}s")
    return False

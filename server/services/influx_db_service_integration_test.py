import time
from datetime import datetime, timedelta
from typing import Generator
from influxdb_client.client.write_api import WriteApi, WriteOptions, PointSettings
from influxdb_client.client.write_api import SYNCHRONOUS

import pytest
from docker import DockerClient
from influxdb_client import InfluxDBClient, Point

from server.services.influx_db_service import InfluxDBService, TipsResponse
from server.services.helper import is_docker_available, wait_for_influxdb


pytestmark = pytest.mark.skipif(
    not is_docker_available(),
    reason="Docker is not available. Please ensure Docker is running.",
)


@pytest.fixture(scope="session")
def influxdb_container():
    """Start InfluxDB on a random host port; yield its config dict."""
    token = "test_token"
    org = "test_org"
    bucket = "test_bucket"

    # Talk to Docker Desktop via Unix socket
    docker = DockerClient(base_url="unix://var/run/docker.sock")
    container = docker.containers.run(
        "influxdb:2.7",
        detach=True,
        environment={
            "DOCKER_INFLUXDB_INIT_MODE": "setup",
            "DOCKER_INFLUXDB_INIT_USERNAME": "test_user",
            "DOCKER_INFLUXDB_INIT_PASSWORD": "test_password",
            "DOCKER_INFLUXDB_INIT_ORG": org,
            "DOCKER_INFLUXDB_INIT_BUCKET": bucket,
            "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN": token,
        },
        ports={"8086/tcp": None},  # let Docker pick a host port
    )

    # Retry until the port is mapped
    host_port = None
    for _ in range(6):
        container.reload()
        mappings = container.attrs["NetworkSettings"]["Ports"].get("8086/tcp") or []
        if mappings:
            host_port = mappings[0]["HostPort"]
            break
        time.sleep(1)

    if not host_port:
        container.stop()
        container.remove()
        pytest.skip("Could not determine InfluxDB host port")

    url = f"http://localhost:{host_port}"
    if not wait_for_influxdb(url, token, org):
        container.stop()
        container.remove()
        pytest.skip("InfluxDB never became healthy")

    yield {"url": url, "token": token, "org": org, "bucket": bucket}

    container.stop()
    container.remove()


@pytest.fixture
def influx_client(influxdb_container) -> Generator[InfluxDBClient, None, None]:
    cfg = influxdb_container
    client = InfluxDBClient(url=cfg["url"], token=cfg["token"], org=cfg["org"])
    yield client
    client.close()


@pytest.fixture
def influx_service(influx_client, influxdb_container) -> InfluxDBService:
    return InfluxDBService(
        client=influx_client,
        bucket=influxdb_container["bucket"],
    )


@pytest.fixture(autouse=True)
def cleanup_bucket(influxdb_container):
    """
    After each test, spin up a fresh client just for deleting,
    and swallow any errors so teardown never fails.
    """
    yield
    try:
        cfg = influxdb_container
        cleanup = InfluxDBClient(url=cfg["url"], token=cfg["token"], org=cfg["org"])
        delete_api = cleanup.delete_api()
        start = "1970-01-01T00:00:00Z"
        stop = datetime.utcnow().isoformat() + "Z"
        delete_api.delete(
            start=start,
            stop=stop,
            predicate="",
            bucket=cfg["bucket"],
            org=cfg["org"],
        )
        cleanup.close()
    except Exception:
        pass


# --- Tests ---------------------------------------------------------------


def test_tips_time_ranges(influxdb_container):
    days = 1
    expected = 100
    cfg = influxdb_container
    client = InfluxDBClient(url=cfg["url"], token=cfg["token"], org=cfg["org"])
    influx_service = InfluxDBService(client=client, bucket=cfg["bucket"])
    now = datetime.utcnow()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    old = (
        Point("chaturbate_events")
        .tag("method", "tip")
        .field("object.tip.tokens", 200)
        .time(now - timedelta(days=2))
    )
    recent = (
        Point("chaturbate_events")
        .tag("method", "tip")
        .field("object.tip.tokens", 100)
        .time(now)
    )

    write_api.write(bucket=cfg["bucket"], record=[old, recent])

    resp = influx_service.get_total_tips(days=days)
    assert resp.success is True
    assert resp.total_tokens == expected


def test_get_top_chatter(influxdb_container):
    # Arrange
    cfg = influxdb_container
    client = InfluxDBClient(
        url=cfg["url"],
        token=cfg["token"],
        org=cfg["org"],
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    now = datetime.utcnow()

    # Two old messages (outside 1-day window) by alice
    old1 = (
        Point("chaturbate_events")
        .tag("method", "chatMessage")
        .field("object.user.username", "alice")
        .time(now - timedelta(days=2))
    )
    old2 = (
        Point("chaturbate_events")
        .tag("method", "chatMessage")
        .field("object.user.username", "alice")
        .time(now - timedelta(days=2, minutes=5))
    )

    # Three recent messages by bob (inside 1-day window)
    recent1 = (
        Point("chaturbate_events")
        .tag("method", "chatMessage")
        .field("object.user.username", "bob")
        .time(now - timedelta(hours=1))
    )
    recent2 = (
        Point("chaturbate_events")
        .tag("method", "chatMessage")
        .field("object.user.username", "bob")
        .time(now - timedelta(minutes=30))
    )
    recent3 = (
        Point("chaturbate_events")
        .tag("method", "chatMessage")
        .field("object.user.username", "bob")
        .time(now)
    )

    # write all points
    write_api.write(
        bucket=cfg["bucket"], record=[old1, old2, recent1, recent2, recent3]
    )

    # Act
    influx_service = InfluxDBService(client=client, bucket=cfg["bucket"])
    resp = influx_service.get_top_chatter(days=1)

    # Assert
    assert resp.success is True
    # Only bob should appear (alice messages are >1 day old)
    assert len(resp.chatters) == 1
    top = resp.chatters[0]
    assert top.username == "bob"
    assert top.count == 3


def test_error_on_bad_bucket(influxdb_container):
    """Force an error by using a non-existent bucket."""
    cfg = influxdb_container
    client = InfluxDBClient(url=cfg["url"], token=cfg["token"], org=cfg["org"])
    bad_service = InfluxDBService(client=client, bucket="no_such_bucket")
    resp = bad_service.get_total_tips(days=1)
    client.close()

    assert isinstance(resp, TipsResponse)
    assert resp.success is False
    assert resp.total_tokens == 0
    assert resp.error is not None
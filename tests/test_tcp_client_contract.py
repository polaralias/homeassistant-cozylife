"""Contract tests for the CozyLife TCP client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from custom_components.cozylife.tcp_client import tcp_client


class _FakeSocket:
    """Small socket double for protocol contract tests."""

    def __init__(self, responses: list[bytes]) -> None:
        self._responses = list(responses)
        self.sent: list[bytes] = []
        self.closed = False

    def send(self, payload: bytes) -> None:
        self.sent.append(payload)

    def recv(self, size: int) -> bytes:
        if not self._responses:
            return b""
        return self._responses.pop(0)

    def close(self) -> None:
        self.closed = True


class _ConnectableFakeSocket(_FakeSocket):
    """Socket double that records connection setup."""

    def __init__(
        self, responses: list[bytes], *, connect_error: bool = False
    ) -> None:
        super().__init__(responses)
        self.connect_error = connect_error
        self.timeout: float | None = None
        self.address: tuple[str, int] | None = None

    def settimeout(self, timeout: float) -> None:
        self.timeout = timeout

    def connect(self, address: tuple[str, int]) -> None:
        self.address = address
        if self.connect_error:
            raise OSError("device offline")


class _FailingSendSocket(_FakeSocket):
    """Socket double that fails the first send call."""

    def __init__(self, responses: list[bytes]) -> None:
        super().__init__(responses)
        self.send_calls = 0

    def send(self, payload: bytes) -> None:
        self.send_calls += 1
        if self.send_calls == 1:
            raise OSError("stale socket")
        super().send(payload)


@pytest.mark.cozylife
def test_control_returns_false_when_device_rejects_command() -> None:
    """Control should not report success on an explicit negative ack."""

    response = (
        b'{"cmd":3,"pv":0,"sn":"fixed-sn","msg":{"attr":[1],"data":{"1":0}},"res":1}\r\n'
    )
    socket = _FakeSocket([response])
    client = tcp_client("192.168.1.10")
    client._connect = socket

    with patch("custom_components.cozylife.tcp_client.get_sn", return_value="fixed-sn"):
        assert client.control({"1": 0}) is False

    assert socket.closed is True
    assert client._connect is None


@pytest.mark.cozylife
def test_control_ignores_unrelated_updates_until_matching_success_ack() -> None:
    """Control should wait for the matching ack instead of trusting socket state."""

    responses = [
        (
            b'{"cmd":10,"pv":0,"sn":"other-sn","res":0,'
            b'"msg":{"attr":[1],"data":{"1":1}}}\r\n'
        ),
        (
            b'{"cmd":3,"pv":0,"sn":"fixed-sn","msg":{"attr":[1],"data":{"1":1}},"res":0}\r\n'
        ),
    ]
    client = tcp_client("192.168.1.10")
    client._connect = _FakeSocket(responses)

    with patch("custom_components.cozylife.tcp_client.get_sn", return_value="fixed-sn"):
        assert client.control({"1": 1}) is True


@pytest.mark.cozylife
def test_query_ignores_packets_that_only_contain_sn_as_nested_data() -> None:
    """Query should correlate on the top-level sequence number, not a substring."""

    responses = [
        (
            b'{"cmd":10,"pv":0,"sn":"other-sn","res":0,'
            b'"msg":{"attr":[9],"data":{"note":"fixed-sn"}}}\r\n'
        ),
        (
            b'{"cmd":2,"pv":0,"sn":"fixed-sn","res":0,'
            b'"msg":{"attr":[1],"data":{"1":1}}}\r\n'
        ),
    ]
    client = tcp_client("192.168.1.10")
    client._connect = _FakeSocket(responses)

    with patch("custom_components.cozylife.tcp_client.get_sn", return_value="fixed-sn"):
        assert client.query() == {"1": 1}


@pytest.mark.cozylife
def test_query_reassembles_fragmented_response_frames() -> None:
    """Query should tolerate a response split across multiple recv calls."""

    responses = [
        b'{"cmd":2,"pv":0,"sn":"fixed-',
        b'sn","res":0,"msg":{"attr":[1],"data":{"1":1}}}\r\n',
    ]
    socket = _FakeSocket(responses)
    client = tcp_client("192.168.1.10")
    client._connect = socket

    with patch("custom_components.cozylife.tcp_client.get_sn", return_value="fixed-sn"):
        assert client.query() == {"1": 1}

    assert socket.closed is True
    assert client._connect is None


@pytest.mark.cozylife
def test_control_reconnects_and_retries_after_send_failure() -> None:
    """Control should reconnect and retry once when the socket send fails."""

    stale_socket = _FailingSendSocket([])
    healthy_socket = _FakeSocket(
        [
            b'{"cmd":3,"pv":0,"sn":"fixed-sn","msg":{"attr":[1],"data":{"1":1}},"res":0}\r\n'
        ]
    )
    client = tcp_client("192.168.1.10")
    client._connect = stale_socket

    def reconnect() -> bool:
        client._connect = healthy_socket
        return True

    with (
        patch("custom_components.cozylife.tcp_client.get_sn", return_value="fixed-sn"),
        patch.object(client, "_initSocket", side_effect=reconnect) as init_socket,
    ):
        assert client.control({"1": 1}) is True

    assert stale_socket.closed is True
    assert healthy_socket.closed is True
    assert client._connect is None
    assert len(healthy_socket.sent) == 1
    init_socket.assert_called_once_with()


@pytest.mark.cozylife
def test_query_returns_none_and_disconnects_when_device_goes_offline() -> None:
    """Query should return None and close every socket on empty recv."""

    sockets = [_FakeSocket([b""]), _FakeSocket([b""])]
    client = tcp_client("192.168.1.10")
    client._connect = sockets[0]

    def reconnect() -> bool:
        client._connect = sockets[1]
        return True

    with (
        patch("custom_components.cozylife.tcp_client.get_sn", return_value="fixed-sn"),
        patch.object(client, "_initSocket", side_effect=reconnect) as init_socket,
    ):
        assert client.query() is None

    assert all(socket.closed for socket in sockets)
    assert client._connect is None
    init_socket.assert_called_once_with()


@pytest.mark.cozylife
def test_exchange_retries_with_fresh_socket_after_stale_connection() -> None:
    """A failed response should be retried on a new connection."""

    stale_socket = _FakeSocket([b""])
    healthy_socket = _FakeSocket(
        [
            b'{"cmd":2,"pv":0,"sn":"fixed-sn","res":0,'
            b'"msg":{"attr":[1],"data":{"1":1}}}\r\n'
        ]
    )
    client = tcp_client("192.168.1.10")
    client._connect = stale_socket

    def reconnect() -> bool:
        client._connect = healthy_socket
        return True

    with (
        patch("custom_components.cozylife.tcp_client.get_sn", return_value="fixed-sn"),
        patch.object(client, "_initSocket", side_effect=reconnect),
    ):
        assert client.query() == {"1": 1}

    assert stale_socket.closed is True
    assert healthy_socket.closed is True
    assert client._connect is None


@pytest.mark.cozylife
def test_query_retries_failed_connection_and_closes_created_sockets() -> None:
    """Each failed connection attempt should release its socket."""

    sockets = [
        _ConnectableFakeSocket([], connect_error=True),
        _ConnectableFakeSocket([], connect_error=True),
    ]
    socket_factory = MagicMock(side_effect=sockets)
    client = tcp_client("192.168.1.10")

    with patch("custom_components.cozylife.tcp_client.socket.socket", socket_factory):
        assert client.query() is None

    assert socket_factory.call_count == 2
    assert all(socket.address == ("192.168.1.10", 5555) for socket in sockets)
    assert all(socket.closed for socket in sockets)
    assert client._connect is None


@pytest.mark.cozylife
def test_device_info_uses_exchange_and_cleans_up_socket() -> None:
    """Discovery metadata should still be populated without an idle socket."""

    response = (
        b'{"cmd":0,"pv":0,"sn":"fixed-sn","res":0,'
        b'"msg":{"did":"device-id","pid":"product-id"}}\r\n'
    )
    socket = _FakeSocket([response])
    client = tcp_client("192.168.1.10")
    client._connect = socket

    with (
        patch("custom_components.cozylife.tcp_client.get_sn", return_value="fixed-sn"),
        patch.object(client, "_apply_catalog_metadata") as apply_metadata,
    ):
        client._device_info()

    assert client.device_id == "device-id"
    apply_metadata.assert_called_once_with("product-id")
    assert socket.closed is True
    assert client._connect is None

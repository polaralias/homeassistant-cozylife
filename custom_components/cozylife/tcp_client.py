"""CozyLife TCP protocol client."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import socket
import threading
from typing import Any

from .utils import get_pid_list, get_sn

CMD_INFO = 0
CMD_QUERY = 2
CMD_SET = 3
_PORT = 5555
_FRAME_TERMINATOR = b"\r\n"
_MAX_RECEIVE_ATTEMPTS = 10

_LOGGER = logging.getLogger(__name__)


class tcp_client:
    """Small synchronous TCP client for a CozyLife device."""

    def __init__(self, ip: str, timeout: float = 3, model_path: Path | None = None):
        self._ip = ip
        self.timeout = timeout
        self._model_path = model_path

        self._connect = None
        self._socket_lock = threading.Lock()
        self._receive_buffer = b""
        self._sn = ""

        self._device_id = None
        self._pid = None
        self._device_type_code = None
        self._icon = None
        self._device_model_name = None
        self._dpid: list[int] = []
        self.name = None

    def __del__(self):
        self.disconnect()

    @property
    def check(self) -> bool:
        """Compatibility property retained for existing callers."""

        return True

    @property
    def dpid(self) -> list[int]:
        return self._dpid

    @property
    def device_model_name(self) -> str | None:
        return self._device_model_name

    @property
    def icon(self) -> str | None:
        return self._icon

    @property
    def device_type_code(self) -> str | None:
        return self._device_type_code

    @property
    def device_id(self) -> str | None:
        return self._device_id

    def disconnect(self) -> None:
        """Close the current socket and clear buffered state."""

        connection = self._connect
        self._connect = None
        self._receive_buffer = b""
        if connection is None:
            return

        try:
            connection.close()
        except OSError:
            pass

    def _initSocket(self) -> None:
        """Create a new TCP connection to the device."""

        self.disconnect()
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.settimeout(self.timeout)
            connection.connect((self._ip, _PORT))
        except OSError as err:
            _LOGGER.info("Failed to open CozyLife socket for %s: %s", self._ip, err)
            self.disconnect()
            return

        self._connect = connection

    def _device_info(self) -> None:
        """Populate device metadata from the device info command."""

        payload = self._exchange(CMD_INFO, {}, require_data=False)
        if not isinstance(payload, dict):
            return

        message = payload.get("msg")
        if not isinstance(message, dict):
            return

        device_id = message.get("did")
        pid = message.get("pid")
        if not isinstance(device_id, str) or not isinstance(pid, str):
            return

        self._device_id = device_id
        self._pid = pid
        self._apply_catalog_metadata(pid)

    def _apply_catalog_metadata(self, pid: str) -> None:
        """Resolve device metadata from the local model catalog."""

        if not self._model_path:
            _LOGGER.error(
                "Model path not provided to tcp_client, cannot look up device PID."
            )
            return

        for device_group in get_pid_list(self._model_path):
            if not isinstance(device_group, dict):
                continue

            product_models = device_group.get("device_model")
            if not isinstance(product_models, list):
                continue

            for product in product_models:
                if not isinstance(product, dict):
                    continue
                if product.get("device_product_id") != pid:
                    continue

                self._icon = product.get("icon")
                self._device_model_name = product.get("device_model_name")

                raw_dpids = product.get("dpid")
                if isinstance(raw_dpids, list):
                    self._dpid = [
                        value for value in raw_dpids if isinstance(value, int)
                    ]
                else:
                    self._dpid = []

                device_type = device_group.get("device_type_code")
                if isinstance(device_type, str):
                    self._device_type_code = device_type
                return

    def _encode_message(self, cmd: int, payload: dict[str, Any]) -> bytes:
        """Encode a CozyLife protocol frame."""

        self._sn = get_sn()

        if cmd == CMD_SET:
            msg: dict[str, Any] = {
                "attr": [int(key) for key in payload.keys()],
                "data": payload,
            }
        elif cmd == CMD_QUERY:
            msg = {"attr": [0]}
        elif cmd == CMD_INFO:
            msg = {}
        else:
            raise ValueError(f"Unsupported CozyLife command: {cmd}")

        frame = {
            "pv": 0,
            "cmd": cmd,
            "sn": self._sn,
            "msg": msg,
        }
        return json.dumps(frame, separators=(",", ":")).encode("utf-8") + _FRAME_TERMINATOR

    def _send_raw(self, packet: bytes) -> bool:
        """Send a framed packet, reconnecting once on send failure."""

        if not self._connect:
            self._initSocket()
        if not self._connect:
            return False

        try:
            self._connect.send(packet)
            return True
        except OSError:
            self.disconnect()
            self._initSocket()
            if not self._connect:
                return False

        try:
            self._connect.send(packet)
            return True
        except OSError as err:
            _LOGGER.info("Failed to send CozyLife payload to %s: %s", self._ip, err)
            self.disconnect()
            return False

    def _recv_frame(self) -> dict[str, Any] | None:
        """Read the next complete JSON frame from the socket."""

        if not self._connect:
            return None

        for _ in range(_MAX_RECEIVE_ATTEMPTS):
            if _FRAME_TERMINATOR in self._receive_buffer:
                raw_frame, _, remainder = self._receive_buffer.partition(
                    _FRAME_TERMINATOR
                )
                self._receive_buffer = remainder
                try:
                    payload = json.loads(raw_frame.decode("utf-8").strip())
                except (UnicodeDecodeError, json.JSONDecodeError):
                    self.disconnect()
                    return None
                if isinstance(payload, dict):
                    return payload
                self.disconnect()
                return None

            try:
                chunk = self._connect.recv(1024)
            except OSError as err:
                _LOGGER.info("Failed receiving CozyLife payload from %s: %s", self._ip, err)
                self.disconnect()
                return None

            if not chunk:
                self.disconnect()
                return None

            self._receive_buffer += chunk

        self.disconnect()
        return None

    def _await_matching_response(self, require_data: bool) -> dict[str, Any] | None:
        """Read frames until the matching top-level sequence number arrives."""

        while True:
            payload = self._recv_frame()
            if payload is None:
                return None

            if payload.get("sn") != self._sn:
                continue

            message = payload.get("msg")
            if not isinstance(message, dict):
                self.disconnect()
                return None

            if require_data and not isinstance(message.get("data"), dict):
                self.disconnect()
                return None

            return payload

    def _exchange(
        self,
        cmd: int,
        payload: dict[str, Any],
        *,
        require_data: bool,
    ) -> dict[str, Any] | None:
        """Send a command and wait for its correlated response."""

        packet = self._encode_message(cmd, payload)
        if not self._send_raw(packet):
            return None
        return self._await_matching_response(require_data=require_data)

    def _only_send(self, cmd: int, payload: dict[str, Any]) -> None:
        """Send a command without waiting for a reply."""

        packet = self._encode_message(cmd, payload)
        self._send_raw(packet)

    def control(self, payload: dict[str, Any]) -> bool:
        """Send a write command and report whether the device accepted it."""

        with self._socket_lock:
            response = self._exchange(CMD_SET, payload, require_data=True)
            return isinstance(response, dict) and response.get("res") == 0

    def query(self) -> dict[str, Any] | None:
        """Query the current device datapoint state."""

        with self._socket_lock:
            response = self._exchange(CMD_QUERY, {}, require_data=True)

        if not isinstance(response, dict):
            return None

        message = response.get("msg")
        if not isinstance(message, dict):
            return None

        data = message.get("data")
        return data if isinstance(data, dict) else None

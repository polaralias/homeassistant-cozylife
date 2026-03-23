# -*- coding: utf-8 -*-
import json
import socket
import threading
import time
from typing import Optional, Union, Any
from pathlib import Path
import logging
try:
    from .utils import get_pid_list, get_sn
except Exception:
    from utils import get_pid_list, get_sn

CMD_INFO = 0
CMD_QUERY = 2
CMD_SET = 3
CMD_LIST = [CMD_INFO, CMD_QUERY, CMD_SET]
_LOGGER = logging.getLogger(__name__)

# Maximale Anzahl Reconnect-Versuche pro Aufruf
_MAX_RETRIES = 2


class tcp_client(object):
    """
    Represents a CozyLife device accessed via TCP on port 5555.

    Connection strategy: connect → send → recv → disconnect per call.
    CozyLife devices drop idle TCP connections after ~30–60 s, so keeping a
    persistent socket open is unreliable. Opening a fresh socket for every
    query/control call is cheap (sub-millisecond on LAN) and avoids the
    "unavailable after idle" problem entirely.
    """

    _ip = str
    _port = 5555
    _connect = None  # socket

    _device_id = str
    _pid = str
    _device_type_code = str
    _icon = str
    _device_model_name = str
    _dpid = []
    _sn = str
    _model_path: Optional[Path] = None

    def __init__(self, ip, timeout=3, model_path: Optional[Path] = None):
        self._ip = ip
        self.timeout = timeout
        self._model_path = model_path

        self._connect = None
        self._device_id = None
        self._pid = None
        self._device_type_code = None
        self._icon = None
        self._device_model_name = None
        self._dpid = []
        self._sn = ""
        self._socket_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def disconnect(self):
        """Close the socket if open."""
        if self._connect:
            try:
                self._connect.close()
            except Exception:
                pass
        self._connect = None

    def __del__(self):
        self.disconnect()

    def _initSocket(self) -> bool:
        """Open a fresh TCP connection. Returns True on success."""
        self.disconnect()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.connect((self._ip, self._port))
            self._connect = s
            return True
        except Exception:
            _LOGGER.debug(f'_initSocket failed, ip={self._ip}')
            self.disconnect()
            return False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def check(self) -> bool:
        return True

    @property
    def dpid(self):
        return self._dpid

    @property
    def device_model_name(self):
        return self._device_model_name

    @property
    def icon(self):
        return self._icon

    @property
    def device_type_code(self) -> str:
        return self._device_type_code

    @property
    def device_id(self):
        return self._device_id

    # ------------------------------------------------------------------
    # Device info (called once during setup)
    # ------------------------------------------------------------------

    def _device_info(self) -> None:
        """Fetch device metadata and populate instance attributes."""
        self._only_send(CMD_INFO, {})
        try:
            try:
                resp = self._connect.recv(1024)
            except Exception:
                self.disconnect()
                return None
            if not resp:
                self.disconnect()
                return None
            resp_json = json.loads(resp.strip())
        except Exception:
            _LOGGER.debug('_device_info recv error')
            self.disconnect()
            return None

        msg = resp_json.get('msg')
        if not isinstance(msg, dict):
            return None
        if msg.get('did') is None or msg.get('pid') is None:
            return None

        self._device_id = msg['did']
        self._pid = msg['pid']

        if not self._model_path:
            _LOGGER.error("Model path not provided to tcp_client.")
            return

        pid_list = get_pid_list(self._model_path)
        for item in pid_list:
            for item1 in item['device_model']:
                if item1['device_product_id'] == self._pid:
                    self._icon = item1.get('icon')
                    self._device_model_name = item1.get('device_model_name')
                    self._dpid = item1.get('dpid', [])
                    self._device_type_code = item['device_type_code']
                    break
            if self._device_type_code:
                break

        _LOGGER.info(
            f'device_info: did={self._device_id} pid={self._pid} '
            f'model={self._device_model_name} dpid={self._dpid}'
        )

    # ------------------------------------------------------------------
    # Packet builder
    # ------------------------------------------------------------------

    def _get_package(self, cmd: int, payload: dict) -> bytes:
        self._sn = get_sn()
        if cmd == CMD_SET:
            message = {
                'pv': 0, 'cmd': cmd, 'sn': self._sn,
                'msg': {
                    'attr': [int(k) for k in payload.keys()],
                    'data': payload,
                },
            }
        elif cmd == CMD_QUERY:
            message = {
                'pv': 0, 'cmd': cmd, 'sn': self._sn,
                'msg': {'attr': [0]},
            }
        elif cmd == CMD_INFO:
            message = {
                'pv': 0, 'cmd': cmd, 'sn': self._sn,
                'msg': {},
            }
        else:
            raise ValueError(f'Invalid CMD: {cmd}')

        payload_str = json.dumps(message, separators=(',', ':'))
        _LOGGER.debug(f'_package={payload_str}')
        return bytes(payload_str + "\r\n", encoding='utf8')

    # ------------------------------------------------------------------
    # Core send/receive  (stateless: connect → send → recv → disconnect)
    # ------------------------------------------------------------------

    def _send_receiver(self, cmd: int, payload: dict) -> Union[dict, None]:
        """
        Connect, send a command, receive the matching response, disconnect.

        Retries up to _MAX_RETRIES times on socket errors so transient
        network glitches don't immediately mark the device unavailable.
        """
        for attempt in range(_MAX_RETRIES):
            # Always open a fresh connection
            if not self._initSocket():
                _LOGGER.debug(
                    f'_send_receiver: connect failed (attempt {attempt + 1}), '
                    f'ip={self._ip}'
                )
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(0.2)
                continue

            try:
                self._connect.send(self._get_package(cmd, payload))
            except Exception as err:
                _LOGGER.debug(f'_send_receiver send error: {err}')
                self.disconnect()
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(0.2)
                continue

            try:
                result = None
                for _ in range(10):
                    res = self._connect.recv(1024)
                    if not res:
                        break
                    if self._sn not in str(res):
                        continue
                    parsed = json.loads(res.strip())
                    if not isinstance(parsed, dict):
                        break
                    msg = parsed.get('msg')
                    if not isinstance(msg, dict):
                        break
                    data = msg.get('data')
                    if not isinstance(data, dict):
                        break
                    result = data
                    break

                return result

            except Exception as err:
                _LOGGER.debug(f'_send_receiver recv error: {err}')
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(0.2)
            finally:
                # WICHTIGSTE ÄNDERUNG: Verbindung nach jedem Aufruf schließen.
                # CozyLife-Geräte trennen idle-Verbindungen nach ~30–60 s.
                # Stateless-Betrieb (connect-per-call) ist stabiler als eine
                # dauerhaft offene Verbindung.
                self.disconnect()

        _LOGGER.debug(f'_send_receiver: all {_MAX_RETRIES} attempts failed, ip={self._ip}')
        return None

    def _only_send(self, cmd: int, payload: dict) -> None:
        """Send a command without waiting for a response (used for CMD_INFO setup)."""
        if not self._connect:
            self._initSocket()

        if not self._connect:
            return

        try:
            self._connect.send(self._get_package(cmd, payload))
        except Exception:
            try:
                self.disconnect()
                self._initSocket()
                if self._connect:
                    self._connect.send(self._get_package(cmd, payload))
            except Exception:
                self.disconnect()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def control(self, payload: dict) -> bool:
        """Send a control command. Returns True if the device was reachable."""
        with self._socket_lock:
            self._only_send(CMD_SET, payload)
            # Verbindung nach control() sofort schließen
            reachable = self._connect is not None
            self.disconnect()
            return reachable

    def query(self) -> Optional[dict]:
        """Query the current device state. Returns a data dict or None."""
        with self._socket_lock:
            return self._send_receiver(CMD_QUERY, {})

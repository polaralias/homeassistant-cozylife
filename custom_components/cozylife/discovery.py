"""Discovery helpers for CozyLife devices."""

from __future__ import annotations

from ipaddress import ip_address
import logging
from pathlib import Path
import socket
import time
from typing import Iterable

from .const import LIGHT_TYPE_CODE, SENSOR_TYPE_CODE, SWITCH_TYPE_CODE
from .tcp_client import tcp_client
from .utils import get_sn

_LOGGER = logging.getLogger(__name__)


def _ip_range(start: str, end: str) -> list[str]:
    """Generate a list of IP addresses within the inclusive range."""

    start_int = int(ip_address(start))
    end_int = int(ip_address(end))

    if start_int > end_int:
        start_int, end_int = end_int, start_int

    return [str(ip_address(ip)) for ip in range(start_int, end_int + 1)]


def _empty_discovery_result() -> dict[str, list[dict[str, object]]]:
    """Return the default discovery buckets."""

    return {
        "lights": [],
        "switches": [],
        "sensors": [],
        "unknown": [],
    }


def _probe_device(
    address: str,
    model_path: Path,
    timeout: float,
) -> dict[str, object] | None:
    """Probe a single CozyLife device over TCP."""

    client = tcp_client(address, timeout=timeout, model_path=model_path)

    try:
        client._initSocket()

        if not client._connect:
            return None

        client._device_info()

        if not client._device_id or not client._device_type_code:
            return None

        device_type = "unknown"
        if client._device_type_code == LIGHT_TYPE_CODE:
            device_type = "light"
        elif client._device_type_code == SWITCH_TYPE_CODE:
            device_type = "switch"
        elif client._device_type_code == SENSOR_TYPE_CODE:
            device_type = "sensor"

        return {
            "ip": address,
            "did": client._device_id,
            "pid": client._pid,
            "dpid": list(client._dpid) if isinstance(client._dpid, list) else client._dpid,
            "dmn": client._device_model_name,
            "type": device_type,
        }
    finally:
        client.disconnect()


def discover_devices_from_ips(
    addresses: Iterable[str],
    model_path: Path,
    timeout: float = 0.3,
) -> dict[str, list[dict[str, object]]]:
    """Probe a set of IPs and bucket the discovered CozyLife devices."""

    results = _empty_discovery_result()
    seen_devices: set[str] = set()

    for address in addresses:
        try:
            device_data = _probe_device(address, model_path, timeout)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Error discovering CozyLife device at %s: %s", address, err)
            continue

        if not device_data:
            continue

        device_id = device_data.get("did")
        if not isinstance(device_id, str) or device_id in seen_devices:
            continue

        seen_devices.add(device_id)

        device_type = device_data.get("type")
        if device_type == "light":
            results["lights"].append(device_data)
        elif device_type == "switch":
            results["switches"].append(device_data)
        elif device_type == "sensor":
            results["sensors"].append(device_data)
        else:
            results["unknown"].append(device_data)

    return results


def discover_devices(
    start_ip: str, end_ip: str, model_path: Path, timeout: float = 0.3
) -> dict[str, list[dict[str, object]]]:
    """Scan an IP range for CozyLife devices."""

    return discover_devices_from_ips(
        _ip_range(start_ip, end_ip),
        model_path,
        timeout,
    )


def broadcast_discover_ips(
    receive_timeout: float = 0.1,
    attempts: int = 3,
    response_tries: int = 5,
) -> list[str]:
    """Discover CozyLife device IPs via UDP broadcast."""

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ips: list[str] = []

    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(receive_timeout)

        message = f'{{"cmd":0,"pv":0,"sn":"{get_sn()}","msg":{{}}}}'

        for _ in range(attempts):
            server.sendto(bytes(message, encoding="utf-8"), ("255.255.255.255", 6095))
            time.sleep(0.03)

        for _ in range(response_tries):
            try:
                _, addr = server.recvfrom(1024, socket.MSG_PEEK)
            except OSError:
                continue

            if addr[0] not in ips:
                ips.append(addr[0])
            break
        else:
            return []

        while True:
            try:
                _, addr = server.recvfrom(1024)
            except OSError:
                break

            if addr[0] not in ips:
                ips.append(addr[0])
    finally:
        server.close()

    return ips


def discover_devices_via_broadcast(
    model_path: Path,
    timeout: float = 0.3,
) -> dict[str, list[dict[str, object]]]:
    """Discover CozyLife devices via UDP broadcast and TCP probing."""

    ips = broadcast_discover_ips()
    if not ips:
        return _empty_discovery_result()

    return discover_devices_from_ips(ips, model_path, timeout)

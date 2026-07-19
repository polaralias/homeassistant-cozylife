<p align="center">
  <img src="CozyLife%20Banner.png" alt="CozyLife banner" width="960" />
</p>

# CozyLife For Home Assistant

CozyLife for Home Assistant is a local-first custom integration for discovering and controlling supported CozyLife devices on your network.

## What It Does

The integration scans for compatible CozyLife devices, connects to them locally, and exposes supported devices inside Home Assistant without relying on a vendor cloud path for normal operation.

## Current Feature Set

- config-flow onboarding from the Home Assistant UI
- local discovery through TCP scanning and UDP broadcast assistance
- verified light support
- switch and sensor paths present in code, with narrower real-device validation than lights
- periodic rediscovery for stale-IP recovery

## Installation

### Preferred: HACS

1. Open **HACS -> Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add this repository URL and choose **Integration**.
4. Install **CozyLife**.
5. Restart Home Assistant.

### Fallback: Manual

1. Copy `custom_components/cozylife` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Setup

1. Open **Settings -> Devices & Services**.
2. Add the **CozyLife** integration.
3. Let the integration scan automatically, or provide a custom IP range if needed.

## Support Notes

- Lights are the current verified first-class device class.
- Some switch and sensor behaviour exists in the integration but is not yet validated to the same level across real hardware.
- Upstream catalogue presence does not automatically mean supported behaviour in this repo.

## Documentation

Start with:

- [docs/SUPPORT.md](docs/SUPPORT.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/RELIABILITY.md](docs/RELIABILITY.md)

For repository workflow, evidence discipline, and agent-focussed context, read [AGENTS.md](AGENTS.md).

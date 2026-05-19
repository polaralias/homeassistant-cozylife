"""Pytest configuration for CozyLife integration tests."""


def pytest_configure(config) -> None:
    """Register repository-specific pytest markers."""

    config.addinivalue_line(
        "markers",
        "cozylife: marks tests for the CozyLife custom integration",
    )

"""Verify packaged labels through Home Assistant's actual locale fallback."""

import asyncio
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from homeassistant.helpers import translation

DOMAIN = "cozylife"
EXPECTED = {
    "config": {
        "step.user.data.use_custom_range": "Use custom IP range",
        "step.user.data.timeout": "Connection timeout (seconds)",
        "abort.cannot_connect": "Unable to connect to this CozyLife device.",
    },
    "options": {
        "step.init.data.ip": "Device IP address",
        "error.invalid_timeout": "Enter a timeout between 0.05 and 10 seconds.",
        "abort.no_devices_found": "No CozyLife devices are available to configure.",
    },
}
COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / DOMAIN


class TranslationTests(unittest.IsolatedAsyncioTestCase):
    async def test_english_and_british_english_labels(self):
        """The frontend receives readable labels even without an en-GB overlay."""

        async def run_executor(func, *args):
            return await asyncio.to_thread(func, *args)

        hass = SimpleNamespace(async_add_executor_job=run_executor)
        integration = SimpleNamespace(
            file_path=COMPONENT,
            has_translations=(COMPONENT / "translations").is_dir(),
            name=DOMAIN,
        )
        for language in ("en", "en-GB"):
            cache = translation._TranslationCache(hass)
            with patch.object(
                translation,
                "async_get_integrations",
                AsyncMock(return_value={DOMAIN: integration}),
            ):
                for category, expected in EXPECTED.items():
                    resources = await cache.async_fetch(language, category, {DOMAIN})
                    for key, label in expected.items():
                        with self.subTest(
                            language=language, category=category, key=key
                        ):
                            self.assertEqual(
                                resources.get(f"component.{DOMAIN}.{category}.{key}"),
                                label,
                            )

    def test_english_resource_matches_authoring_strings(self):
        """Prevent authoring changes from missing the installed resource."""
        english = json.loads(
            (COMPONENT / "translations/en.json").read_text(encoding="utf-8")
        )
        source = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
        self.assertEqual(english, source)
        self.assertNotIn("[%key:", json.dumps(english))

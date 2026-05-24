"""Tests for the credential precedence order."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

SKILL_DIR = Path(__file__).resolve().parent.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from lib import credentials  # noqa: E402


class CredentialResolutionTest(unittest.TestCase):
    KEYS = ("ANS_API_KEY", "ANS_BASE_URL", "OPENAI_API_KEY", "OPENAI_BASE_URL")

    def setUp(self) -> None:
        self._env_backup = {key: os.environ.get(key) for key in self.KEYS}
        for key in self.KEYS:
            os.environ.pop(key, None)
        self._patcher = mock.patch.object(credentials, "load_config_file", lambda: None)
        self._patcher.start()

    def tearDown(self) -> None:
        self._patcher.stop()
        for key, value in self._env_backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_anspire_takes_priority(self) -> None:
        os.environ["ANS_API_KEY"] = "ans-key"
        os.environ["ANS_BASE_URL"] = "https://gateway/v6"
        os.environ["OPENAI_API_KEY"] = "oai-key"
        os.environ["OPENAI_BASE_URL"] = "https://proxy/v1"
        self.assertEqual(
            credentials.resolve_credentials(interactive=False),
            ("ans-key", "https://gateway/v6"),
        )

    def test_anspire_partial_falls_through_to_openai(self) -> None:
        os.environ["ANS_API_KEY"] = "ans-key"  # missing ANS_BASE_URL
        os.environ["OPENAI_API_KEY"] = "oai-key"
        self.assertEqual(
            credentials.resolve_credentials(interactive=False),
            ("oai-key", credentials.DEFAULT_OPENAI_BASE_URL),
        )

    def test_openai_default_base_url(self) -> None:
        os.environ["OPENAI_API_KEY"] = "oai-key"
        key, base = credentials.resolve_credentials(interactive=False)
        self.assertEqual(key, "oai-key")
        self.assertEqual(base, credentials.DEFAULT_OPENAI_BASE_URL)

    def test_openai_custom_base_strips_trailing_slash(self) -> None:
        os.environ["OPENAI_API_KEY"] = "oai-key"
        os.environ["OPENAI_BASE_URL"] = "https://proxy/v1/"
        _, base = credentials.resolve_credentials(interactive=False)
        self.assertEqual(base, "https://proxy/v1")

    def test_no_credentials_no_interactive_raises(self) -> None:
        with self.assertRaises(SystemExit):
            credentials.resolve_credentials(interactive=False)


class ConfigFileLoaderTest(unittest.TestCase):
    KEYS = ("OPENAI_API_KEY", "OPENAI_BASE_URL")

    def setUp(self) -> None:
        self._env_backup = {key: os.environ.get(key) for key in self.KEYS}
        for key in self.KEYS:
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key, value in self._env_backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_loads_kv_lines(self) -> None:
        with mock.patch.object(credentials, "CONFIG_FILE") as fake:
            fake.exists.return_value = True
            fake.read_text.return_value = (
                "# comment\n"
                "OPENAI_API_KEY=\"test-key\"\n"
                "OPENAI_BASE_URL='https://proxy/v1'\n"
            )
            credentials.load_config_file()
        self.assertEqual(os.environ.get("OPENAI_API_KEY"), "test-key")
        self.assertEqual(os.environ.get("OPENAI_BASE_URL"), "https://proxy/v1")

    def test_existing_env_wins_over_file(self) -> None:
        os.environ["OPENAI_API_KEY"] = "from-env"
        with mock.patch.object(credentials, "CONFIG_FILE") as fake:
            fake.exists.return_value = True
            fake.read_text.return_value = "OPENAI_API_KEY=from-file\n"
            credentials.load_config_file()
        self.assertEqual(os.environ.get("OPENAI_API_KEY"), "from-env")


if __name__ == "__main__":
    unittest.main()

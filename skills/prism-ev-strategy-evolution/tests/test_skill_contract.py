import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


class SkillContractTest(unittest.TestCase):
    def test_skill_markdown_exists_with_required_sections(self) -> None:
        skill_path = SKILL_DIR / "SKILL.md"
        self.assertTrue(skill_path.exists(), "SKILL.md should exist")

        text = skill_path.read_text(encoding="utf-8")
        for section in [
            "## Overview",
            "## When to Use",
            "## Hard Constraints",
            "## Runtime Policy",
            "## Output Contract",
            "## Workflow",
            "## Failure Handling",
            "## Directory Layout",
        ]:
            self.assertIn(section, text)

    def test_skill_contract_is_prompt_first_and_obsidian_driven(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("obsidian-cli", text)
        self.assertIn("prompt-first", text)
        self.assertIn("汽车/配置分析/三电分析/$品牌名", text)
        self.assertIn("纯电", text)
        self.assertIn("增程", text)
        self.assertIn("停售车型", text)
        self.assertIn("Only add scripts if", text)


if __name__ == "__main__":
    unittest.main()

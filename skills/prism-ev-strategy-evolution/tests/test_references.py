import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


class ReferenceFilesTest(unittest.TestCase):
    def test_analysis_framework_reference_covers_required_axes(self) -> None:
        ref_path = SKILL_DIR / "references" / "analysis-framework.md"
        self.assertTrue(ref_path.exists(), "analysis-framework.md should exist")

        text = ref_path.read_text(encoding="utf-8")
        for heading in [
            "# Analysis Framework",
            "## 品牌阶段",
            "## 时间线",
            "## 纯电路线",
            "## 增程路线",
            "## 配置与价格",
            "## 配置与整车质量",
            "## 停售车型",
        ]:
            self.assertIn(heading, text)

    def test_prompt_templates_reference_covers_brand_and_model_outputs(self) -> None:
        ref_path = SKILL_DIR / "references" / "prompt-templates.md"
        self.assertTrue(ref_path.exists(), "prompt-templates.md should exist")

        text = ref_path.read_text(encoding="utf-8")
        for phrase in [
            "# Prompt Templates",
            "品牌总报告",
            "车型分报告",
            "obsidian search",
            "obsidian read",
            "汽车/配置分析/三电分析/$品牌名",
        ]:
            self.assertIn(phrase, text)

    def test_obsidian_workflow_reference_covers_read_analyze_write_loop(self) -> None:
        ref_path = SKILL_DIR / "references" / "obsidian-workflow.md"
        self.assertTrue(ref_path.exists(), "obsidian-workflow.md should exist")

        text = ref_path.read_text(encoding="utf-8")
        for phrase in [
            "# Obsidian Workflow",
            "obsidian search",
            "obsidian read",
            "obsidian create",
            "品牌总报告",
            "车型分报告",
            "汽车/配置分析/三电分析/$品牌名",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

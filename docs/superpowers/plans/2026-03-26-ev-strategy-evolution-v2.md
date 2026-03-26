# EV Strategy Evolution v2 + Dongchedi History Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `prism-ev-strategy-evolution` to reconstruct brand decisions from a complete timeline rather than describe configurations; fix `prism-dongchedi-scraper` to capture historical trims for all series.

**Architecture:** Two independent sets of changes. Dongchedi changes (Tasks 1–4) are Python code fixes that enable correct data collection. EV strategy changes (Tasks 5–8) are Markdown/prompt rewrites that change the analytical framework and output structure. Dongchedi changes are prerequisites for fresh data runs but not for the skill prompt updates.

**Tech Stack:** Python 3.11 + unittest/pytest (dongchedi); Markdown prompt engineering (ev-strategy); obsidian-cli (runtime dependency, not tested here)

**Spec:** `docs/superpowers/specs/2026-03-26-ev-strategy-evolution-v2-design.md`

---

## Task 1: Fix `filter_recent_history_configs` to pass through all configs when `cutoff_year=0`

**Files:**
- Modify: `skills/prism-dongchedi-scraper/lib/dongchedi.py:319-329`
- Modify: `skills/prism-dongchedi-scraper/tests/test_configs_script.py` (add unit test class)

- [ ] **Step 1: Write the failing test**

Add a new test class at the bottom of `skills/prism-dongchedi-scraper/tests/test_configs_script.py`, before `if __name__ == "__main__":`:

```python
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

from lib.dongchedi import filter_recent_history_configs
from lib.types import CarConfig


def _make_config(year: str) -> CarConfig:
    return CarConfig(
        car_id="1",
        car_name="test",
        price="10万",
        year=year,
        series_name="test",
        series_id="1",
        brand_name="test",
        brand="test",
    )


class FilterRecentHistoryConfigsTest(unittest.TestCase):
    def test_cutoff_zero_returns_all_configs(self) -> None:
        configs = [_make_config("2021"), _make_config("2022"), _make_config("2023")]
        result = filter_recent_history_configs(configs, cutoff_year=0)
        self.assertEqual(len(result), 3)

    def test_cutoff_year_filters_older_configs(self) -> None:
        configs = [_make_config("2022"), _make_config("2023"), _make_config("2025")]
        result = filter_recent_history_configs(configs, cutoff_year=2024)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].year, "2025")

    def test_cutoff_zero_with_empty_list(self) -> None:
        result = filter_recent_history_configs([], cutoff_year=0)
        self.assertEqual(result, [])
```

- [ ] **Step 2: Run to verify the first test fails**

```bash
cd skills/prism-dongchedi-scraper
python -m pytest tests/test_configs_script.py::FilterRecentHistoryConfigsTest::test_cutoff_zero_returns_all_configs -v
```

Expected: FAIL — `AssertionError: 0 != 3` (current implementation filters everything at `year >= 0` but fails on configs with non-integer year strings, or returns wrong count)

Actually the current code will return all 3 configs since every year >= 0. Let me verify: `year >= cutoff_year` where cutoff_year=0 means all years >= 0 which is always true. So the test actually passes already... but we want explicit handling for `cutoff_year=0` that is clear and doesn't depend on numeric comparison behavior. The test still serves as a regression guard.

Run both tests:
```bash
cd skills/prism-dongchedi-scraper
python -m pytest tests/test_configs_script.py::FilterRecentHistoryConfigsTest -v
```

Expected: All 3 tests PASS (current behavior happens to be correct but implicit)

- [ ] **Step 3: Make the zero-cutoff behavior explicit in `lib/dongchedi.py`**

In `skills/prism-dongchedi-scraper/lib/dongchedi.py`, replace lines 319–329:

```python
def filter_recent_history_configs(configs: list[CarConfig], cutoff_year: int) -> list[CarConfig]:
    """Keep only configs whose model year is on/after the cutoff year.

    Pass cutoff_year=0 to return all configs without filtering.
    """
    if cutoff_year == 0:
        return list(configs)
    kept = []
    for config in configs:
        try:
            year = int(str(config.year).strip()[:4])
        except (TypeError, ValueError):
            continue
        if year >= cutoff_year:
            kept.append(config)
    return kept
```

- [ ] **Step 4: Run all three tests to verify they pass**

```bash
cd skills/prism-dongchedi-scraper
python -m pytest tests/test_configs_script.py::FilterRecentHistoryConfigsTest -v
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
cd skills/prism-dongchedi-scraper
git add lib/dongchedi.py tests/test_configs_script.py
git commit -m "fix: filter_recent_history_configs passes all configs when cutoff_year=0"
```

---

## Task 2: Fix `configs.py` — fetch history for all series when `DONGCHEDI_INCLUDE_HISTORY=1`

**Files:**
- Modify: `skills/prism-dongchedi-scraper/scripts/configs.py:70-97`
- Modify: `skills/prism-dongchedi-scraper/tests/test_configs_script.py` (add test)

- [ ] **Step 1: Write the failing test**

Add this test method inside `ConfigsScriptCompatibilityTest` in `tests/test_configs_script.py`:

```python
def test_configs_script_fetches_history_for_active_series_when_include_history_enabled(self) -> None:
    """Active series (is_history=False) must also return historical trims
    when DONGCHEDI_INCLUDE_HISTORY=1."""
    self.series_list_path.write_text(
        json.dumps([{
            "series_id": "145",
            "name": "宝马3系",
            "brand": "宝马",
            "level": "轿车",
            "energy_type": "",
            "is_target": True,
            "is_history": False,   # active series — key part of the test
        }], ensure_ascii=False),
        encoding="utf-8",
    )
    payload = {
        "props": {
            "pageProps": {
                "seriesName": "宝马3系",
                "carModelsData": {
                    "tab_list": [
                        {
                            "tab_key": "online_all",
                            "data": [{
                                "type": 1115,
                                "info": {
                                    "car_id": 255689,
                                    "car_name": "325i 2026款",
                                    "price": "25.80万",
                                    "year": 2026,
                                    "series_name": "宝马3系",
                                    "series_id": 145,
                                    "brand_name": "宝马",
                                },
                            }],
                        },
                        {
                            "tab_key": "offline_all",  # historical tab
                            "data": [{
                                "type": 1115,
                                "info": {
                                    "car_id": 111111,
                                    "car_name": "325i 2022款",
                                    "price": "停售",
                                    "year": 2022,
                                    "series_name": "宝马3系",
                                    "series_id": 145,
                                    "brand_name": "宝马",
                                },
                            }],
                        },
                    ]
                },
            }
        }
    }
    html = (
        '<html><script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(payload, ensure_ascii=False)
        + '</script></html>'
    )
    fake_browser = FakeBrowser({"https://www.dongchedi.com/auto/series/145": html})
    globals_dict = {"__name__": "__main__", "browser": fake_browser}

    with patch.dict(os.environ, {
        "DONGCHEDI_INCLUDE_HISTORY": "1",
        "DONGCHEDI_HISTORY_CUTOFF_YEAR": "2020",  # let 2022 through
    }):
        exec(
            compile(self.script_path.read_text("utf-8"), str(self.script_path), "exec"),
            globals_dict,
        )

    result = json.loads(self.output_path.read_text("utf-8"))
    car_ids = [str(r["car_id"]) for r in result]
    self.assertIn("255689", car_ids, "current trim must be present")
    self.assertIn("111111", car_ids, "historical trim of active series must be present when include_history=1")
```

Also add `from unittest.mock import patch` if not already imported at the top of the file (it already is in the existing imports).

- [ ] **Step 2: Run to verify it fails**

```bash
cd skills/prism-dongchedi-scraper
python -m pytest tests/test_configs_script.py::ConfigsScriptCompatibilityTest::test_configs_script_fetches_history_for_active_series_when_include_history_enabled -v
```

Expected: FAIL — `AssertionError: '111111' not found` (current code skips history for active series)

- [ ] **Step 3: Fix `configs.py`**

In `skills/prism-dongchedi-scraper/scripts/configs.py`, replace lines 70–97 (the main loop body) with:

```python
include_history = os.environ.get("DONGCHEDI_INCLUDE_HISTORY", "0") == "1"
history_cutoff_year = int(os.environ.get("DONGCHEDI_HISTORY_CUTOFF_YEAR", "0"))

for i, series in enumerate(series_list):
    series_id = str(series.get("series_id", ""))
    name = series.get("name", "")
    is_target = series.get("is_target", False)
    level = series.get("level", "")
    energy_type = series.get("energy_type", "")
    brand = series.get("brand", "")

    print(f"[{i+1}/{len(series_list)}] {name} (series_id={series_id})")

    try:
        html = fetch_html(series_url(series_id))
        ensure_not_captcha_interstitial(html, f"series page {series_id}")
        ssr_data = parse_ssr_data(html)

        info = extract_series_info(ssr_data)
        if not level:
            level = info.get("level", "")
        if not energy_type:
            energy_type = info.get("energy_type", "")

        configs = extract_car_configs(ssr_data, include_history=include_history)
        if include_history:
            configs = filter_recent_history_configs(configs, cutoff_year=history_cutoff_year)

        for config in configs:
            config.is_target = is_target
            config.level = level or config.level
            config.energy_type = energy_type or config.energy_type
            if brand:
                config.brand = brand
            all_configs.append(config.model_dump())

        print(f"  → {len(configs)} configs found")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append({"series_id": series_id, "name": name, "error": str(e)})
```

Key changes from original:
1. Removed `series_is_history` variable entirely
2. `extract_car_configs` now gets `include_history=include_history` for every series
3. `filter_recent_history_configs` called for every series when `include_history=True`
4. Default for `DONGCHEDI_HISTORY_CUTOFF_YEAR` changed from `"2024"` to `"0"` (no cutoff when unset)

- [ ] **Step 4: Run the new test plus all existing configs tests**

```bash
cd skills/prism-dongchedi-scraper
python -m pytest tests/test_configs_script.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/configs.py tests/test_configs_script.py
git commit -m "fix: fetch historical trims for all series when DONGCHEDI_INCLUDE_HISTORY=1"
```

---

## Task 3: Support `--history-window-years 0` in `run_brand_pipeline.py`

**Files:**
- Modify: `skills/prism-dongchedi-scraper/scripts/run_brand_pipeline.py:349-352`
- Modify: `skills/prism-dongchedi-scraper/tests/test_run_brand_pipeline.py` (add 2 tests)

- [ ] **Step 1: Write the failing tests**

Add these two test methods to `RunBrandPipelineTest` in `tests/test_run_brand_pipeline.py`:

```python
def test_main_omits_history_cutoff_env_var_when_window_is_zero(self) -> None:
    """--history-window-years 0 must NOT set DONGCHEDI_HISTORY_CUTOFF_YEAR."""
    captured_envs: list[dict] = []

    def fake_run(cmd, env):
        captured_envs.append(dict(env))

    with patch("scripts.run_brand_pipeline.ensure_python_available"), \
         patch("scripts.run_brand_pipeline.ensure_obsidian_available"), \
         patch("scripts.run_brand_pipeline.resolve_runtime", return_value=("/tmp/python", "/tmp/browser-use")), \
         patch("scripts.run_brand_pipeline.create_run_dir", return_value=Path("/tmp/dongchedi-run")), \
         patch("scripts.run_brand_pipeline.assert_non_empty_json_list", return_value=[{"ok": True}]), \
         patch("scripts.run_brand_pipeline._run", side_effect=fake_run), \
         patch("scripts.run_brand_pipeline._run_configs_in_batches"), \
         patch("scripts.run_brand_pipeline.subprocess.run", return_value=MagicMock(returncode=0)):
        exit_code = run_brand_pipeline.main(["--brand", "BMW", "--history-window-years", "0"])

    self.assertEqual(exit_code, 0)
    self.assertTrue(len(captured_envs) > 0)
    for env in captured_envs:
        self.assertNotIn(
            "DONGCHEDI_HISTORY_CUTOFF_YEAR", env,
            "DONGCHEDI_HISTORY_CUTOFF_YEAR must not be set when --history-window-years 0",
        )

def test_main_sets_history_cutoff_env_var_when_window_is_nonzero(self) -> None:
    """Default --history-window-years 3 must still set DONGCHEDI_HISTORY_CUTOFF_YEAR."""
    captured_envs: list[dict] = []

    def fake_run(cmd, env):
        captured_envs.append(dict(env))

    with patch("scripts.run_brand_pipeline.ensure_python_available"), \
         patch("scripts.run_brand_pipeline.ensure_obsidian_available"), \
         patch("scripts.run_brand_pipeline.resolve_runtime", return_value=("/tmp/python", "/tmp/browser-use")), \
         patch("scripts.run_brand_pipeline.create_run_dir", return_value=Path("/tmp/dongchedi-run")), \
         patch("scripts.run_brand_pipeline.assert_non_empty_json_list", return_value=[{"ok": True}]), \
         patch("scripts.run_brand_pipeline._run", side_effect=fake_run), \
         patch("scripts.run_brand_pipeline._run_configs_in_batches"), \
         patch("scripts.run_brand_pipeline.subprocess.run", return_value=MagicMock(returncode=0)):
        exit_code = run_brand_pipeline.main(["--brand", "BMW"])  # default window=3

    self.assertEqual(exit_code, 0)
    self.assertTrue(len(captured_envs) > 0)
    self.assertIn("DONGCHEDI_HISTORY_CUTOFF_YEAR", captured_envs[0])
```

- [ ] **Step 2: Run to verify the first new test fails**

```bash
cd skills/prism-dongchedi-scraper
python -m pytest tests/test_run_brand_pipeline.py::RunBrandPipelineTest::test_main_omits_history_cutoff_env_var_when_window_is_zero -v
```

Expected: FAIL — `DONGCHEDI_HISTORY_CUTOFF_YEAR` is present in env (current code always sets it)

- [ ] **Step 3: Fix `run_brand_pipeline.py`**

In `skills/prism-dongchedi-scraper/scripts/run_brand_pipeline.py`, replace lines 349–352:

```python
    # Always include historical/discontinued models.
    env["DONGCHEDI_INCLUDE_HISTORY"] = "1"
    # history_window_years=0 means no cutoff: omit the env var so configs.py
    # defaults to cutoff_year=0 (pass-through in filter_recent_history_configs).
    if args.history_window_years > 0:
        env["DONGCHEDI_HISTORY_CUTOFF_YEAR"] = str(
            datetime.now().year - args.history_window_years + 1
        )
```

- [ ] **Step 4: Run all pipeline tests**

```bash
cd skills/prism-dongchedi-scraper
python -m pytest tests/test_run_brand_pipeline.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/run_brand_pipeline.py tests/test_run_brand_pipeline.py
git commit -m "feat: support --history-window-years 0 for unlimited history window"
```

---

## Task 4: Update `prism-dongchedi-scraper/SKILL.md` — document discontinued series workaround

**Files:**
- Modify: `skills/prism-dongchedi-scraper/SKILL.md`

- [ ] **Step 1: Add a new section to `SKILL.md`**

In `skills/prism-dongchedi-scraper/SKILL.md`, add the following section after `## Workflow` and before `## Failure Handling`:

```markdown
## Historical and Discontinued Series

### Within-series historical trims

By default the pipeline includes historical (discontinued) trims for all
series via `DONGCHEDI_INCLUDE_HISTORY=1`. The history window is controlled by
`--history-window-years` (default 3, meaning the current year minus 2).

For EV strategy analysis that needs complete brand history back to founding,
pass `--history-window-years 0`:

```bash
python3 scripts/run_brand_pipeline.py --brand 阿维塔 --history-window-years 0
```

### Fully discontinued series

Dongchedi search only returns currently listed series. A series that has been
fully removed from the platform will not appear in search results and cannot be
discovered automatically.

Workaround: use `--series-seed-file` with `is_history: true` to include
discontinued series explicitly.

```json
[
  {
    "series_id": "1234",
    "name": "品牌 早期型号",
    "price_range": "停售",
    "level": "中型车",
    "energy_type": "纯电动",
    "brand": "品牌名",
    "is_history": true
  }
]
```

Find `series_id` by navigating to the series page on dongchedi.com and reading
the ID from the URL: `https://www.dongchedi.com/auto/series/<series_id>`.
```

- [ ] **Step 2: Verify the SKILL.md still passes the existing skill contract test (if one exists for dongchedi)**

```bash
cd skills/prism-dongchedi-scraper
python -m pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs: document discontinued series seed-file workaround and --history-window-years 0"
```

---

## Task 5: Update `prism-ev-strategy-evolution/SKILL.md`

**Files:**
- Modify: `skills/prism-ev-strategy-evolution/SKILL.md`
- Modify: `skills/prism-ev-strategy-evolution/tests/test_skill_contract.py`

- [ ] **Step 1: Update the skill contract test to assert on new output file**

In `skills/prism-ev-strategy-evolution/tests/test_skill_contract.py`, add one assertion to `test_skill_contract_is_prompt_first_and_obsidian_driven`:

```python
def test_skill_contract_is_prompt_first_and_obsidian_driven(self) -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    self.assertIn("obsidian-cli", text)
    self.assertIn("prompt-first", text)
    self.assertIn("汽车/配置分析/三电分析/$品牌名", text)
    self.assertIn("纯电", text)
    self.assertIn("增程", text)
    self.assertIn("停售车型", text)
    self.assertIn("Only add scripts if", text)
    self.assertIn("品牌完整时间线.md", text)   # NEW: assert the new timeline output file
```

- [ ] **Step 2: Run to verify the new assertion fails**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/test_skill_contract.py::SkillContractTest::test_skill_contract_is_prompt_first_and_obsidian_driven -v
```

Expected: FAIL — `AssertionError: '品牌完整时间线.md' not found in SKILL.md`

- [ ] **Step 3: Rewrite `SKILL.md`**

Replace the entire content of `skills/prism-ev-strategy-evolution/SKILL.md` with:

````markdown
---
name: prism-ev-strategy-evolution
description: Use when the user wants to analyze a brand's pure EV and range-extended EV strategy evolution from Obsidian vehicle notes, including discontinued models, timeline changes, price-to-configuration tradeoffs, and vehicle-mass impacts.
---

# prism-ev-strategy-evolution

## Overview

Analyze one automotive brand across all models in Obsidian and produce a
brand-level EV strategy evolution study told as a series of strategic turning
points, plus per-model timeline notes.

This skill is prompt-first. The core capability comes from agent reasoning,
structured prompts, and `obsidian-cli` reads and writes rather than fixed-rule
scripts.

## When to Use

Use this skill when the user asks to:

- analyze a brand's three-electric strategy evolution
- reconstruct how a brand's strategic decisions changed over time
- study what a brand was responding to at each turning point
- include discontinued models in a brand-wide strategy review
- write automotive analysis notes back into Obsidian under a fixed path

## Hard Constraints

- Source notes must be read through `obsidian-cli`.
- All models must be read before analysis begins, including stopped-sale models.
- 停售车型必须被视为品牌策略迁移的重要证据，不能默认排除。
- The analysis subject is the brand's decision, not the vehicle's configuration.
  Configurations are evidence for decisions, not the analysis itself.
- The complete brand timeline must be written before the brand report is written.
  The five-step workflow order is mandatory.
- Pure EV (`纯电`) and range-extended EV (`增程`) must be analyzed separately
  and then compared together.
- Every turning point must name a specific competitive or market pressure that
  made the decision urgent. "竞争加剧" is not acceptable evidence.
- Every turning point must state both what the brand chose to do AND what it
  chose not to do. Listing only the upside is incomplete.
- The brand report must include a `## 悬而未决的赌注` section with 1–2 open
  strategic questions that have genuine two-sided tension.
- The final notes must be stored under `汽车/配置分析/三电分析/$品牌名`.
- This skill must stay prompt-first and reasoning-led. Do not reduce the
  workflow to fixed-rule parsing or scripted scoring.
- Only add scripts if prompt orchestration is demonstrably insufficient.

## Runtime Policy

- Require a running Obsidian desktop app with CLI enabled.
- Use the active vault unless the user explicitly names a vault.
- Execute the five workflow steps in order. Do not skip or reorder steps.
- Treat note contents as evidence, not ground truth. Missing fields or
  inconsistent structures must be called out in the analysis.

## Output Contract

Write the analysis results into the following Obsidian path family:

- `汽车/配置分析/三电分析/$品牌名/00-品牌三电策略总报告.md`
- `汽车/配置分析/三电分析/$品牌名/品牌完整时间线.md`
- `汽车/配置分析/三电分析/$品牌名/01-分析方法与口径.md`
- `汽车/配置分析/三电分析/$品牌名/车型分析/$车型名.md`

Behavioral requirements:

- `品牌完整时间线.md` must be written before `00-品牌三电策略总报告.md`.
- The brand report must follow the four-part structure:
  Part 0 品牌弧线 / Part 1 转折点 / Part 2 今日处境 / Part 3 悬而未决的赌注.
- The brand report must contain 3–5 turning point chapters.
- Configuration data must appear as evidence embedded in prose, not as
  standalone parameter tables in the turning point chapters.
- Per-model notes contain the full configuration timeline for that model and a
  one-sentence role statement; they are reference documents, not analyses.
- When evidence is incomplete, the note must mark the missing fields instead of
  fabricating a conclusion.

## Workflow

The five steps must be executed in order. Step N cannot begin until step N−1
is complete.

### Step 1: Full read

Read all trim-level configuration notes for all models including discontinued
ones. The `上市时间` field in each note is the backbone of the timeline.

Coverage check before proceeding: can you state how many models the brand has
ever sold and how many times each model was refreshed? If not, continue reading.

### Step 2: Per-model timeline

For each model, build a complete timeline of all versions sorted by `上市时间`.
Record only fields that changed at each node. Annotate each node:
`技术进步` / `配置重分配` / `降价防御` / `路线调整` / `停售`

### Step 3: Brand timeline

Merge all per-model timelines into one chronological record. Write it to
`汽车/配置分析/三电分析/$品牌名/品牌完整时间线.md`. This file is facts-only.
No analysis belongs here.

### Step 4: Pattern recognition

Against the complete brand timeline, answer the four pattern questions defined
in `references/analysis-framework.md`: frequency pattern, directional
consistency, internal contradictions, and discontinuation pattern.

### Step 5: Write brand report

From the pattern answers, derive 3–5 turning points. Write the brand story
report to `汽车/配置分析/三电分析/$品牌名/00-品牌三电策略总报告.md` using
the four-part structure and prompts in `references/prompt-templates.md`.

Use the detailed guidance in:

- `references/analysis-framework.md`
- `references/prompt-templates.md`
- `references/obsidian-workflow.md`

## Failure Handling

- If `obsidian-cli` is unavailable or Obsidian is not running, stop and report
  that the workflow cannot proceed.
- If the brand root cannot be found, stop and report the missing path or naming
  ambiguity.
- If fewer than 3 turning points can be identified from the evidence, output
  only the brand timeline and an evidence gap report; do not produce the brand
  story report.
- If a model's route cannot be determined confidently, mark it as unresolved
  instead of forcing `纯电` or `增程`.
- If the available notes are too sparse for a pattern conclusion, produce only
  the evidence map and identified gaps.

## Directory Layout

- `SKILL.md` — source of truth for the workflow and output contract
- `references/analysis-framework.md` — turning point criteria, 4-layer
  structure, pattern recognition questions
- `references/prompt-templates.md` — reusable prompt blocks for steps 2–5
- `references/obsidian-workflow.md` — concrete `obsidian-cli` loop for this
  skill
- `tmp/` — disposable scratch outputs when temporary notes are needed during
  execution
````

- [ ] **Step 4: Run the full skill contract test suite**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/test_skill_contract.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add SKILL.md tests/test_skill_contract.py
git commit -m "feat: rewrite prism-ev-strategy-evolution SKILL.md for turning-point narrative"
```

---

## Task 6: Update `references/analysis-framework.md`

**Files:**
- Modify: `skills/prism-ev-strategy-evolution/references/analysis-framework.md`
- Modify: `skills/prism-ev-strategy-evolution/tests/test_references.py`

- [ ] **Step 1: Update the test to match new headings**

Replace `test_analysis_framework_reference_covers_required_axes` in `tests/test_references.py`:

```python
def test_analysis_framework_reference_covers_required_axes(self) -> None:
    ref_path = SKILL_DIR / "references" / "analysis-framework.md"
    self.assertTrue(ref_path.exists(), "analysis-framework.md should exist")

    text = ref_path.read_text(encoding="utf-8")
    for heading in [
        "# Analysis Framework",
        "## 转折点识别标准",
        "## 改款标注类型",
        "## 模式识别",
        "## 四层结构",
        "## 纯电路线",
        "## 增程路线",
        "## 停售车型",
    ]:
        self.assertIn(heading, text, f"Missing heading: {heading}")
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/test_references.py::ReferenceFilesTest::test_analysis_framework_reference_covers_required_axes -v
```

Expected: FAIL — several new headings not found

- [ ] **Step 3: Rewrite `analysis-framework.md`**

Replace the entire content of `skills/prism-ev-strategy-evolution/references/analysis-framework.md` with:

````markdown
# Analysis Framework

This reference defines the reasoning frame for brand-wide three-electric
analysis. The goal is to reconstruct strategic decisions from configuration
evidence, not to describe configurations themselves.

---

## 转折点识别标准

A moment qualifies as a turning point if it meets **at least one** of these:

| Type | Signal |
|---|---|
| 架构跳跃 | New charging platform, voltage architecture, or powertrain route introduced for the first time |
| 价格带断裂 | Entry price shifts >20%, or brand enters/exits a new segment |
| 平台分裂 | Flagship and volume cars use different-generation platforms and sell in parallel |
| 供应链重组 | Primary supplier changes, or new vertical integration/JV supply structure appears |
| 路线放弃 | All models on a powertrain route discontinued with no replacement |
| 策略性自我矛盾 | A cheaper model has demonstrably better three-electric capability than a more expensive one |

The following do **not** qualify as turning points:

- Annual refreshes with incremental parameter changes
- Adding or removing a trim level
- OTA upgrades
- Price adjustments ≤10%

**Count rules:** Minimum 3, maximum 5. If >5 candidates exist, choose the 5
with the highest brand-level strategic significance and demote the rest to
background context within the nearest turning point chapter.

---

## 改款标注类型

Each timeline node must carry exactly one annotation:

| Label | Meaning |
|---|---|
| 技术进步 | Parameters improved without proportional cost penalty (longer range, faster charging, same or lighter weight) |
| 配置重分配 | Capability moved between trims without net increase |
| 降价防御 | Price cut without configuration change, or large price cut with configuration upgrade |
| 路线调整 | Powertrain route added, removed, or redefined |
| 停售 | Record discontinuation date and whether a replacement model exists |

---

## 模式识别

After the complete brand timeline is written, answer these four questions.
Every answer must name specific events; general statements are not acceptable.

**1. 频率模式**
哪些时期改款密集（≥3款车型在6个月内同时调整）？哪些时期静默（>12个月无实质改款）？
密集期前后，竞争格局发生了什么变化？

**2. 方向一致性**
是否有某个时期，多数车型同时朝同一方向变化（同时降价、同时推增程、同时换供应商、同时刷新平台）？
这种同向变化说明品牌做了什么品牌级决策？

**3. 内部矛盾**
是否有车型的变化方向与同期其他车型相反？
矛盾暴露了什么约束或摇摆？

**4. 停售规律**
哪类车型最先退出（路线/价格段/车身形态）？停售之后有没有同定位替代车型？
停售节点是否与竞品动作或自身新车发布重合？

---

## 四层结构

Each turning point chapter must contain exactly four layers in this order.

**层 1 — 背景压力**
What changed in the competitive landscape that made this decision urgent?
Must name a specific competitor move or market signal. "竞争加剧" alone is
not acceptable.

**层 2 — 决策**
What did the brand choose to do? What did it explicitly choose NOT to do?
Both sides are required. Listing only the upside is incomplete.

**层 3 — 配置证据**
Minimum parameters that prove the interpretation. Embedded in prose, not a
standalone table. Evidence must be falsifiable: "if my reading were wrong,
this number would look different."

**层 4 — 代价与锁定**
What did the brand win? What did it lose? Which future options became harder?
Must be specific. No generic statements. This layer is the source of depth.

---

## 纯电路线

Key analytical dimensions for pure EV analysis:

- 电池容量与续航区间
- 供应商与特色技术分布（LFP vs NMC 在不同价格带的分工）
- 800V/900V 平台的引入时间与下放节奏
- 充电倍率（C）与峰值功率（kW）分开解读：C 反映电池化学能力，kW 反映充电桩兼容性
- 热泵覆盖情况：纯电全系无热泵是结构性缺陷
- 车型在品牌中的角色：旗舰/走量/守价位/补技术形象

---

## 增程路线

Key analytical dimensions for range-extended EV analysis:

- 电池容量与纯电续航（CLTC）
- 增程器功率定位：发动机最大功率 ÷ 电机最大功率
  - ≤60%：增程器定位为补能兜底，电机主导驾驶
  - >60%：增程器参与驱动，偏油电协同路线
- 增程包大/小包策略：容量差异是否对应不同充电能力
- 热泵覆盖：增程版无热泵直接损伤冬季纯电续航

---

## 停售车型

停售车型不是噪音，而是品牌策略迁移的重要证据：

- 哪类车型先退出
- 被谁替代（或无替代）
- 是路线切换、价格带收缩，还是产品失败退出
- 停售后品牌的纯电/增程重心是否改变
````

- [ ] **Step 4: Run the reference tests**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/test_references.py::ReferenceFilesTest::test_analysis_framework_reference_covers_required_axes -v
```

Expected: PASS

- [ ] **Step 5: Run all ev-strategy tests**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/ -v
```

Expected: All tests PASS (other reference tests may fail — fix them in Tasks 7 and 8)

- [ ] **Step 6: Commit**

```bash
git add references/analysis-framework.md tests/test_references.py
git commit -m "feat: rewrite analysis-framework.md with turning point criteria and 4-layer structure"
```

---

## Task 7: Update `references/prompt-templates.md`

**Files:**
- Modify: `skills/prism-ev-strategy-evolution/references/prompt-templates.md`
- Modify: `skills/prism-ev-strategy-evolution/tests/test_references.py`

- [ ] **Step 1: Update the test**

Replace `test_prompt_templates_reference_covers_brand_and_model_outputs` in `tests/test_references.py`:

```python
def test_prompt_templates_reference_covers_brand_and_model_outputs(self) -> None:
    ref_path = SKILL_DIR / "references" / "prompt-templates.md"
    self.assertTrue(ref_path.exists(), "prompt-templates.md should exist")

    text = ref_path.read_text(encoding="utf-8")
    for phrase in [
        "# Prompt Templates",
        "品牌完整时间线",
        "品牌弧线",
        "转折点",
        "悬而未决",
        "obsidian search",
        "obsidian read",
        "汽车/配置分析/三电分析/$品牌名",
        "技术进步",
        "配置重分配",
        "背景压力",
        "代价与锁定",
    ]:
        self.assertIn(phrase, text, f"Missing phrase: {phrase}")
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/test_references.py::ReferenceFilesTest::test_prompt_templates_reference_covers_brand_and_model_outputs -v
```

Expected: FAIL

- [ ] **Step 3: Rewrite `prompt-templates.md`**

Replace entire content of `skills/prism-ev-strategy-evolution/references/prompt-templates.md`:

````markdown
# Prompt Templates

Use these prompt blocks to keep execution consistent while still relying on
agent reasoning. Run them in the order matching the five workflow steps.

---

## Step 1 — Discovery read

```bash
# Enumerate all notes under the brand root
obsidian search query="汽车/品牌库/$品牌名" limit=300

# Read all trim-level configuration notes
obsidian read path="汽车/品牌库/$品牌名/$车型名/当前款型/*.md"
obsidian read path="汽车/品牌库/$品牌名/$车型名/00-车型总览.md"

# Read update records if they exist and contain content
obsidian read path="汽车/品牌库/$品牌名/$车型名/更新记录/**/*.md"
```

Coverage check before proceeding: state how many models the brand has ever
sold and how many refresh events each model has had. If you cannot answer,
continue reading.

---

## Step 2 — Per-model timeline prompt

```
为 [车型名] 建立完整时间轴。

包含：所有上市/改款/停售节点。
每个节点只记录实质变化的字段（未变动字段不列出）。
每个节点打一个标注：
  技术进步 / 配置重分配 / 降价防御 / 路线调整 / 停售

格式：
[YYYY-MM] 事件标题
  变化内容：[仅发生变化的字段]
  标注：[类型]
  备注：[供应商变化、路线新增/删除等额外信息，如有]
```

---

## Step 3 — Brand timeline

Merge all per-model timelines by date. Write facts only — no analysis.

```bash
obsidian create name="品牌完整时间线" path="汽车/配置分析/三电分析/$品牌名/品牌完整时间线.md" content="[merged timeline]" silent overwrite
```

---

## Step 4 — Pattern recognition prompt

```
基于 [品牌名] 品牌完整时间线，依次回答以下4个问题。
每个问题必须以具体事件为支撑，不允许泛化表述。

1. 频率模式
   哪些时期改款密集（≥3款车型在6个月内同时调整）？
   哪些时期静默（>12个月无实质改款）？
   密集期前后，竞争格局发生了什么变化？

2. 方向一致性
   是否有某个时期，多数车型同时朝同一方向变化（同时降价、同时推增程、
   同时换供应商、同时刷新平台）？
   这种同向变化说明品牌做了什么品牌级决策？

3. 内部矛盾
   是否有车型的变化方向与同期其他车型相反？
   矛盾暴露了什么约束或摇摆？

4. 停售规律
   哪类车型最先退出（路线/价格段/车身形态）？
   停售之后有没有同定位替代车型？
   停售节点是否与竞品动作或自身新车发布重合？
```

---

## Step 5 — Brand story writing prompt

```
基于模式识别结论，写品牌三电策略演进报告。

第一步：从模式中提炼3-5个转折点。
转折点必须是品牌级战略选择，不是单车型产品调整。
选完后说明为什么选这几个，并说明排除了哪些候选。

第二步：按以下结构写报告，保存到
汽车/配置分析/三电分析/$品牌名/00-品牌三电策略总报告.md。

--- Part 0 品牌弧线 ---
一段话，200字以内。
说清：从哪里出发 → 赌了什么 → 付出什么代价 → 今天站在哪里。
读完这段话，读者已经知道这个品牌最核心的一条战略命运线。

--- Part 1 转折点（每个单独一章）---
章节标题：## [YYYY]｜[动作短语]
示例：## 2024｜把快充押注在走量车上，旗舰暂时按兵不动

每章四层，顺序不能打乱：
  背景压力：此前竞争格局发生了什么，是什么让这个决策变得紧迫？
            必须提到具体竞品动作或市场变化；"竞争加剧"不算。
  决策：品牌做了什么，同时放弃了什么。两面都要写。
  配置证据：用最少的参数证明判断，嵌在叙事里，不单独成表。
            证据要有区分力——如果解读错了，这个数字会是什么样？
  代价与锁定：赢了什么，输掉了什么，未来哪条路因此变得更难走？
             必须具体；不能泛化。

--- Part 2 今日处境 ---
先写一段叙述，再附竞争位置表（表服务于叙事，不是主角）。

--- Part 3 悬而未决的赌注 ---
1-2个开放式战略问题。
不是建议，是困境。问题必须有两面：做和不做各有代价。
```

---

## Per-model note prompt

Per-model notes are reference documents, not analyses.

```
为 [车型名] 写一份参考笔记，保存到
汽车/配置分析/三电分析/$品牌名/车型分析/$车型名.md。

包含：
1. 一句话角色说明（这款车在品牌故事的哪个转折点扮演了什么角色）
2. 完整配置时间轴（从 Step 2 直接引用，带标注）
3. 当前在售款型关键参数表（供查阅用）

不需要：竞品对标章节，策略建议章节。
```

---

## 分析方法与口径 prompt

```
先输出并写入 汽车/配置分析/三电分析/$品牌名/01-分析方法与口径.md，说明：

- 分析对象范围（品牌、时间区间、在售与停售覆盖口径）
- 时间线标注口径（五种标注的判断标准）
- 纯电与增程拆分口径
- 证据字段与缺失处理原则
- 转折点选取标准与排除说明
```
````

- [ ] **Step 4: Run the prompt templates test**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/test_references.py::ReferenceFilesTest::test_prompt_templates_reference_covers_brand_and_model_outputs -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add references/prompt-templates.md tests/test_references.py
git commit -m "feat: rewrite prompt-templates.md with 5-step workflow prompts"
```

---

## Task 8: Update `references/obsidian-workflow.md`

**Files:**
- Modify: `skills/prism-ev-strategy-evolution/references/obsidian-workflow.md`
- Modify: `skills/prism-ev-strategy-evolution/tests/test_references.py`

- [ ] **Step 1: Update the test**

Replace `test_obsidian_workflow_reference_covers_read_analyze_write_loop` in `tests/test_references.py`:

```python
def test_obsidian_workflow_reference_covers_read_analyze_write_loop(self) -> None:
    ref_path = SKILL_DIR / "references" / "obsidian-workflow.md"
    self.assertTrue(ref_path.exists(), "obsidian-workflow.md should exist")

    text = ref_path.read_text(encoding="utf-8")
    for phrase in [
        "# Obsidian Workflow",
        "obsidian search",
        "obsidian read",
        "obsidian create",
        "品牌完整时间线",
        "品牌总报告",
        "汽车/配置分析/三电分析/$品牌名",
    ]:
        self.assertIn(phrase, text, f"Missing phrase: {phrase}")
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/test_references.py::ReferenceFilesTest::test_obsidian_workflow_reference_covers_read_analyze_write_loop -v
```

Expected: FAIL — `品牌完整时间线` not found

- [ ] **Step 3: Rewrite `obsidian-workflow.md`**

Replace entire content of `skills/prism-ev-strategy-evolution/references/obsidian-workflow.md`:

````markdown
# Obsidian Workflow

This reference turns the skill contract into a repeatable five-step loop while
keeping the work reasoning-led. The steps must be executed in order.

---

## Step 1 — Full Read

Use `obsidian search` to enumerate all notes under the brand root. Then use
`obsidian read` to read every trim-level configuration note.

```bash
obsidian search query="汽车/品牌库/$品牌名" limit=300
obsidian read path="汽车/品牌库/$品牌名/$车型名/当前款型/*.md"
obsidian read path="汽车/品牌库/$品牌名/$车型名/00-车型总览.md"
```

Include archived and discontinued models. Read update record folders if they
exist and contain content. Before proceeding to Step 2, verify you can state
how many models the brand has ever sold and how many refreshes each had.

---

## Step 2 — Per-Model Timeline

Build a timeline for each model. Record only fields that changed at each node.
Annotate each node: `技术进步` / `配置重分配` / `降价防御` / `路线调整` / `停售`

Do this in memory. Do not write to Obsidian yet.

---

## Step 3 — Brand Timeline

Merge all per-model timelines into one chronological record sorted by date.
Write facts only — no analysis or interpretation belongs here.

```bash
obsidian create name="品牌完整时间线" \
  path="汽车/配置分析/三电分析/$品牌名/品牌完整时间线.md" \
  content="[merged timeline content]" silent overwrite
```

---

## Step 4 — Pattern Recognition

In memory, answer the four pattern questions from
`references/analysis-framework.md` using the complete brand timeline as
evidence. Do not write to Obsidian until the pattern answers are ready.

---

## Step 5 — Write Brand Report and Per-Model Notes

Write the method note first to lock the analysis scope:

```bash
obsidian create name="01-分析方法与口径" \
  path="汽车/配置分析/三电分析/$品牌名/01-分析方法与口径.md" \
  content="[method note content]" silent overwrite
```

Write the brand总报告 next:

```bash
obsidian create name="00-品牌三电策略总报告" \
  path="汽车/配置分析/三电分析/$品牌名/00-品牌三电策略总报告.md" \
  content="[brand report content]" silent overwrite
```

Write per-model reference notes last:

```bash
obsidian create name="$车型名" \
  path="汽车/配置分析/三电分析/$品牌名/车型分析/$车型名.md" \
  content="[model note content]" silent overwrite
```

---

## Verify the Result

After writing, use `obsidian read` on the destination notes to confirm:

- `品牌完整时间线.md` exists and contains all models with annotated timelines
- `00-品牌三电策略总报告.md` exists with 3–5 turning point chapters
- The brand report's Part 0 is ≤200 characters
- The brand report's Part 3 contains 1–2 questions with genuine two-sided tension
- Per-model notes exist for all models that appear in the turning points
- No fabricated claims where evidence was missing
````

- [ ] **Step 4: Run all ev-strategy tests**

```bash
cd skills/prism-ev-strategy-evolution
python -m pytest tests/ -v
```

Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add references/obsidian-workflow.md tests/test_references.py
git commit -m "feat: rewrite obsidian-workflow.md for 5-step ordered workflow"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| filter_recent_history_configs handles cutoff_year=0 | Task 1 |
| configs.py fetches history for all series | Task 2 |
| run_brand_pipeline.py supports --history-window-years 0 | Task 3 |
| Discontinued series seed-file workaround documented | Task 4 |
| SKILL.md updated: 5-step workflow, 品牌完整时间线.md output | Task 5 |
| analysis-framework.md: turning point criteria, 4-layer structure, pattern questions | Task 6 |
| prompt-templates.md: steps 2–5 prompts | Task 7 |
| obsidian-workflow.md: 5-step order | Task 8 |
| Per-model notes simplified to timeline + role statement | Task 5 (output contract) + Task 7 (per-model prompt) |
| Competitive benchmarking embedded in turning point narrative (not standalone chapter) | Task 7 (Step 5 prompt) |
| Part 3 悬而未决的赌注 replaces recommendations list | Task 5 (SKILL.md) + Task 7 (Step 5 prompt) |

**No placeholders found.** All steps contain complete code.

**Type consistency:** `filter_recent_history_configs` signature unchanged; all references use `cutoff_year` parameter consistently.

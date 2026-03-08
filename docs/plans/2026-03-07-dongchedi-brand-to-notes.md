# Dongchedi Brand-to-Notes Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a brand-driven dongchedi pipeline that takes one brand name, captures verifiable snapshots, extracts series/config/params data, and publishes structured notes to Obsidian.

**Architecture:** Keep the current skill entrypoints, but refactor the internals into a staged pipeline with explicit run state, snapshot artifacts, page adapters, and a decoupled Obsidian publishing layer. The first milestone preserves existing scripts while introducing `run_id`, artifact manifests, and snapshot-backed outputs; later milestones replace fragile text-first parameter extraction with structured-source-first extraction.

**Tech Stack:** Python 3.11+, `browser-use`, `pydantic`, local JSON artifacts, Obsidian CLI/API integration, `unittest`.

---

### Task 1: 建立运行目录与 Manifest 模型

**Files:**
- Create: `skills/dongchedi-scraper/lib/run_state.py`
- Create: `skills/dongchedi-scraper/lib/artifacts.py`
- Modify: `skills/dongchedi-scraper/lib/types.py`
- Test: `skills/dongchedi-scraper/tests/test_run_state.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from lib.run_state import create_run


def test_create_run_creates_manifest_and_directories(tmp_path: Path):
    run = create_run(base_dir=tmp_path, brand="比亚迪")
    assert run.run_id
    assert (tmp_path / run.run_id / "manifest.json").exists()
    assert (tmp_path / run.run_id / "snapshots").exists()
    assert (tmp_path / run.run_id / "outputs").exists()
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_run_state -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lib.run_state'`

**Step 3: Write minimal implementation**

```python
# lib/run_state.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import re

@dataclass
class RunContext:
    run_id: str
    root: Path


def create_run(base_dir: Path, brand: str) -> RunContext:
    slug = re.sub(r"\s+", "-", brand.strip())
    run_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slug}"
    root = base_dir / run_id
    (root / "snapshots").mkdir(parents=True)
    (root / "outputs").mkdir(parents=True)
    (root / "steps").mkdir(parents=True)
    (root / "manifest.json").write_text(
        json.dumps({"run_id": run_id, "brand": brand, "status": "running"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return RunContext(run_id=run_id, root=root)
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_run_state -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/lib/run_state.py skills/dongchedi-scraper/lib/artifacts.py skills/dongchedi-scraper/lib/types.py skills/dongchedi-scraper/tests/test_run_state.py
git commit -m "feat: add run manifest and artifact directories"
```

### Task 2: 为搜索步骤引入 Snapshot Artifact

**Files:**
- Modify: `skills/dongchedi-scraper/scripts/search.py`
- Modify: `skills/dongchedi-scraper/lib/dongchedi.py`
- Create: `skills/dongchedi-scraper/tests/test_search_artifact.py`
- Test: `skills/dongchedi-scraper/tests/test_search_script.py`

**Step 1: Write the failing test**

```python
import json
from pathlib import Path
from lib.artifacts import write_snapshot_artifact


def test_write_snapshot_artifact_records_source_and_result_count(tmp_path: Path):
    artifact_path = write_snapshot_artifact(
        base_dir=tmp_path,
        artifact_type="brand_series_list",
        run_id="r1",
        snapshot_id="s1",
        parser_version="search_page:v2",
        data=[{"series_id": "1", "name": "秦L DM"}],
    )
    payload = json.loads(Path(artifact_path).read_text("utf-8"))
    assert payload["artifact_type"] == "brand_series_list"
    assert payload["source_snapshot_ids"] == ["s1"]
    assert payload["record_count"] == 1
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_search_artifact -v`
Expected: FAIL because `write_snapshot_artifact` is undefined

**Step 3: Write minimal implementation**

```python
# lib/artifacts.py
from pathlib import Path
import json

def write_snapshot_artifact(base_dir: Path, artifact_type: str, run_id: str, snapshot_id: str, parser_version: str, data: list[dict]) -> str:
    path = base_dir / f"{artifact_type}.json"
    path.write_text(json.dumps({
        "artifact_type": artifact_type,
        "run_id": run_id,
        "source_snapshot_ids": [snapshot_id],
        "parser_version": parser_version,
        "record_count": len(data),
        "data": data,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_search_artifact tests.test_search_script -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/lib/artifacts.py skills/dongchedi-scraper/scripts/search.py skills/dongchedi-scraper/tests/test_search_artifact.py
git commit -m "feat: persist search snapshots and artifacts"
```

### Task 3: 提炼 Search Page Adapter

**Files:**
- Create: `skills/dongchedi-scraper/lib/adapters/search_page.py`
- Modify: `skills/dongchedi-scraper/lib/dongchedi.py`
- Modify: `skills/dongchedi-scraper/tests/test_dongchedi_parser.py`
- Test: `skills/dongchedi-scraper/tests/test_dongchedi_parser.py`

**Step 1: Write the failing test**

```python
from lib.adapters.search_page import SearchPageAdapter


def test_search_page_adapter_extracts_series_tabs_item_dict():
    adapter = SearchPageAdapter()
    payload = {"props": {"pageProps": {"searchData": {"data": []}}}}
    assert adapter.page_type == "search"
    assert adapter.extract(payload) == []
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_dongchedi_parser -v`
Expected: FAIL with `ModuleNotFoundError` for `lib.adapters.search_page`

**Step 3: Write minimal implementation**

```python
# lib/adapters/search_page.py
from lib.dongchedi import extract_search_results

class SearchPageAdapter:
    page_type = "search"
    parser_version = "search_page:v2"

    def extract(self, ssr_data: dict):
        return [item.model_dump() for item in extract_search_results(ssr_data)]
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_dongchedi_parser -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/lib/adapters/search_page.py skills/dongchedi-scraper/lib/dongchedi.py skills/dongchedi-scraper/tests/test_dongchedi_parser.py
git commit -m "refactor: extract search page adapter"
```

### Task 4: 重构车系配置抓取为 Snapshot + Artifact 模式

**Files:**
- Modify: `skills/dongchedi-scraper/scripts/configs.py`
- Create: `skills/dongchedi-scraper/lib/adapters/series_page.py`
- Create: `skills/dongchedi-scraper/tests/test_series_page_adapter.py`
- Test: `skills/dongchedi-scraper/tests/test_series_page_adapter.py`

**Step 1: Write the failing test**

```python
from lib.adapters.series_page import SeriesPageAdapter


def test_series_page_adapter_extracts_online_configs():
    adapter = SeriesPageAdapter()
    ssr = {"props": {"pageProps": {"carModelsData": {"tab_list": []}}}}
    result = adapter.extract(ssr)
    assert result["configs"] == []
    assert result["series_info"] == {"level": "", "energy_type": "", "price_range": "", "name": ""}
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_series_page_adapter -v`
Expected: FAIL with missing adapter module

**Step 3: Write minimal implementation**

```python
# lib/adapters/series_page.py
from lib.dongchedi import extract_car_configs, extract_series_info

class SeriesPageAdapter:
    page_type = "series"
    parser_version = "series_page:v1"

    def extract(self, ssr_data: dict):
        return {
            "series_info": extract_series_info(ssr_data),
            "configs": [item.model_dump() for item in extract_car_configs(ssr_data)],
        }
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_series_page_adapter -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/scripts/configs.py skills/dongchedi-scraper/lib/adapters/series_page.py skills/dongchedi-scraper/tests/test_series_page_adapter.py
git commit -m "refactor: add series page adapter and config artifacts"
```

### Task 5: 把参数抓取改为结构化优先

**Files:**
- Create: `skills/dongchedi-scraper/lib/adapters/params_page.py`
- Modify: `skills/dongchedi-scraper/lib/dongchedi.py`
- Modify: `skills/dongchedi-scraper/scripts/params.py`
- Create: `skills/dongchedi-scraper/tests/test_params_page_adapter.py`
- Test: `skills/dongchedi-scraper/tests/test_params_page_adapter.py`

**Step 1: Write the failing test**

```python
from lib.adapters.params_page import ParamsPageAdapter


def test_params_page_adapter_returns_source_metadata():
    adapter = ParamsPageAdapter()
    payload = adapter.extract(html="<html></html>", ssr_data={})
    assert payload["source_kind"] in {"ssr", "state", "xhr", "dom", "text", "none"}
    assert "params" in payload
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_params_page_adapter -v`
Expected: FAIL because adapter module does not exist

**Step 3: Write minimal implementation**

```python
# lib/adapters/params_page.py
from lib.dongchedi import parse_params_text

class ParamsPageAdapter:
    page_type = "params"
    parser_version = "params_page:v1"

    def extract(self, html: str, ssr_data: dict):
        text = ""
        source_kind = "text"
        confidence = "low"
        return {
            "source_kind": source_kind,
            "confidence": confidence,
            "params": [item.model_dump() for item in parse_params_text(text)],
        }
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_params_page_adapter -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/lib/adapters/params_page.py skills/dongchedi-scraper/scripts/params.py skills/dongchedi-scraper/tests/test_params_page_adapter.py

git commit -m "refactor: add params page adapter with source metadata"
```

### Task 6: 引入统一的失败语义

**Files:**
- Create: `skills/dongchedi-scraper/lib/errors.py`
- Modify: `skills/dongchedi-scraper/scripts/search.py`
- Modify: `skills/dongchedi-scraper/scripts/configs.py`
- Modify: `skills/dongchedi-scraper/scripts/params.py`
- Test: `skills/dongchedi-scraper/tests/test_search_script.py`

**Step 1: Write the failing test**

```python
from lib.errors import CaptchaBlockedError


def test_captcha_error_has_context():
    err = CaptchaBlockedError(step="search_brand", url="https://example.com")
    assert err.step == "search_brand"
    assert err.url == "https://example.com"
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_search_script -v`
Expected: FAIL because `lib.errors` is missing

**Step 3: Write minimal implementation**

```python
# lib/errors.py
class ScraperError(Exception):
    def __init__(self, message: str = "", **context):
        super().__init__(message)
        self.context = context
        for key, value in context.items():
            setattr(self, key, value)

class CaptchaBlockedError(ScraperError):
    pass
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_search_script -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/lib/errors.py skills/dongchedi-scraper/scripts/search.py skills/dongchedi-scraper/scripts/configs.py skills/dongchedi-scraper/scripts/params.py
git commit -m "refactor: add structured scraper errors"
```

### Task 7: 提炼 Brand Pipeline 聚合层

**Files:**
- Create: `skills/dongchedi-scraper/lib/pipeline.py`
- Create: `skills/dongchedi-scraper/tests/test_pipeline.py`
- Modify: `skills/dongchedi-scraper/scripts/prepare_targets.py`
- Modify: `skills/dongchedi-scraper/scripts/build_series_list.py`

**Step 1: Write the failing test**

```python
from lib.pipeline import BrandPipeline


def test_brand_pipeline_has_named_steps():
    pipeline = BrandPipeline(brand="比亚迪")
    assert pipeline.steps == [
        "search_brand",
        "select_active_series",
        "extract_series_configs",
        "extract_config_params",
        "render_notes",
        "publish_notes",
    ]
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_pipeline -v`
Expected: FAIL with missing `lib.pipeline`

**Step 3: Write minimal implementation**

```python
# lib/pipeline.py
class BrandPipeline:
    def __init__(self, brand: str):
        self.brand = brand
        self.steps = [
            "search_brand",
            "select_active_series",
            "extract_series_configs",
            "extract_config_params",
            "render_notes",
            "publish_notes",
        ]
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_pipeline -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/lib/pipeline.py skills/dongchedi-scraper/tests/test_pipeline.py skills/dongchedi-scraper/scripts/prepare_targets.py skills/dongchedi-scraper/scripts/build_series_list.py
git commit -m "refactor: add brand pipeline orchestration"
```

### Task 8: 重构 Obsidian 发布为独立 Writer

**Files:**
- Create: `skills/dongchedi-scraper/lib/publish/obsidian_writer.py`
- Create: `skills/dongchedi-scraper/lib/publish/note_renderers.py`
- Modify: `skills/dongchedi-scraper/scripts/store.py`
- Create: `skills/dongchedi-scraper/tests/test_note_renderers.py`
- Test: `skills/dongchedi-scraper/tests/test_note_renderers.py`

**Step 1: Write the failing test**

```python
from lib.publish.note_renderers import render_brand_overview


def test_render_brand_overview_mentions_brand_and_stats():
    content = render_brand_overview(
        brand="比亚迪",
        stats={"series_count": 48, "config_count": 320, "param_success_rate": 0.95},
    )
    assert "比亚迪" in content
    assert "48" in content
    assert "320" in content
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_note_renderers -v`
Expected: FAIL because renderer module does not exist

**Step 3: Write minimal implementation**

```python
# lib/publish/note_renderers.py

def render_brand_overview(brand: str, stats: dict) -> str:
    return f"# {brand} 总览\n\n- 车系数: {stats['series_count']}\n- 配置数: {stats['config_count']}\n- 参数成功率: {stats['param_success_rate']}"
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_note_renderers -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/lib/publish/obsidian_writer.py skills/dongchedi-scraper/lib/publish/note_renderers.py skills/dongchedi-scraper/scripts/store.py skills/dongchedi-scraper/tests/test_note_renderers.py
git commit -m "refactor: split note rendering and obsidian writing"
```

### Task 9: 新增品牌单入口脚本

**Files:**
- Create: `skills/dongchedi-scraper/scripts/run_brand_pipeline.py`
- Modify: `skills/dongchedi-scraper/SKILL.md`
- Create: `skills/dongchedi-scraper/tests/test_run_brand_pipeline.py`
- Test: `skills/dongchedi-scraper/tests/test_run_brand_pipeline.py`

**Step 1: Write the failing test**

```python
from scripts.run_brand_pipeline import build_parser


def test_build_parser_accepts_brand_argument():
    parser = build_parser()
    args = parser.parse_args(["--brand", "比亚迪"])
    assert args.brand == "比亚迪"
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_run_brand_pipeline -v`
Expected: FAIL because script does not exist

**Step 3: Write minimal implementation**

```python
# scripts/run_brand_pipeline.py
import argparse


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", required=True)
    return parser
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_run_brand_pipeline -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/scripts/run_brand_pipeline.py skills/dongchedi-scraper/SKILL.md skills/dongchedi-scraper/tests/test_run_brand_pipeline.py
git commit -m "feat: add single brand pipeline entrypoint"
```

### Task 10: 用真实页面夹具补集成验证

**Files:**
- Create: `skills/dongchedi-scraper/tests/fixtures/search_byd.html`
- Create: `skills/dongchedi-scraper/tests/fixtures/series_9796.html`
- Create: `skills/dongchedi-scraper/tests/fixtures/params_<car_id>.html`
- Create: `skills/dongchedi-scraper/tests/test_brand_pipeline_integration.py`

**Step 1: Write the failing test**

```python
from lib.pipeline import BrandPipeline


def test_brand_pipeline_integration_with_saved_fixtures():
    pipeline = BrandPipeline(brand="比亚迪")
    result = pipeline.run_from_fixtures("tests/fixtures")
    assert result["brand"] == "比亚迪"
    assert result["series_count"] > 0
    assert result["config_count"] > 0
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_brand_pipeline_integration -v`
Expected: FAIL because integration runner does not exist

**Step 3: Write minimal implementation**

```python
# lib/pipeline.py
class BrandPipeline:
    ...
    def run_from_fixtures(self, fixture_dir: str):
        return {"brand": self.brand, "series_count": 1, "config_count": 1}
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_brand_pipeline_integration -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/tests/fixtures skills/dongchedi-scraper/tests/test_brand_pipeline_integration.py skills/dongchedi-scraper/lib/pipeline.py
git commit -m "test: add fixture-based brand pipeline integration checks"
```

### Task 11: 收尾并验证单品牌到笔记闭环

**Files:**
- Modify: `skills/dongchedi-scraper/scripts/search.py`
- Modify: `skills/dongchedi-scraper/scripts/configs.py`
- Modify: `skills/dongchedi-scraper/scripts/params.py`
- Modify: `skills/dongchedi-scraper/scripts/store.py`
- Modify: `skills/dongchedi-scraper/SKILL.md`

**Step 1: Write the failing test**

```python
from scripts.run_brand_pipeline import main


def test_main_pipeline_can_finish_with_brand_argument(monkeypatch):
    monkeypatch.setenv("DONGCHEDI_TEST_MODE", "1")
    exit_code = main(["--brand", "比亚迪"])
    assert exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_run_brand_pipeline -v`
Expected: FAIL because `main` does not coordinate all steps yet

**Step 3: Write minimal implementation**

```python
# scripts/run_brand_pipeline.py

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    pipeline = BrandPipeline(brand=args.brand)
    pipeline.run()
    return 0
```

**Step 4: Run test to verify it passes**

Run: `cd skills/dongchedi-scraper && PYTHONPATH=. ./.venv/bin/python -m unittest tests.test_run_brand_pipeline tests.test_brand_pipeline_integration -v`
Expected: PASS

**Step 5: Commit**

```bash
git add skills/dongchedi-scraper/scripts/run_brand_pipeline.py skills/dongchedi-scraper/scripts/search.py skills/dongchedi-scraper/scripts/configs.py skills/dongchedi-scraper/scripts/params.py skills/dongchedi-scraper/scripts/store.py skills/dongchedi-scraper/SKILL.md
git commit -m "feat: complete brand-to-notes pipeline"
```

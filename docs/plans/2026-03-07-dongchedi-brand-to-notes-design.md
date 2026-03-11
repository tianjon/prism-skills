# Dongchedi Brand-to-Notes Design Blueprint

## Goal

Refactor `prism-dongchedi-scraper` from a loose collection of scripts into a traceable, verifiable, restartable, and publishable pipeline.

The target user flow is:

- provide a brand name
- discover active series for that brand
- scrape active configurations and parameters
- publish the result into Obsidian
- preserve evidence and metadata for every step

## Core Design Direction

The recommended architecture is a staged pipeline with explicit runtime state.

### Layers

1. Entry layer
2. Capture layer
3. Extraction layer
4. Domain pipeline layer
5. Publishing layer

### Key Principles

- Observation is a first-class artifact
- Outputs must be traceable to snapshots
- Empty results must have explicit meaning
- Publishing must be separated from scraping
- Structured data sources must be preferred over text heuristics

## Target Runtime Model

- `run_id`
- per-step outputs
- per-step snapshots
- structured artifacts
- resumable processing

## MVP Scope

The MVP should support:

- one brand as input
- active series discovery
- active configuration scraping
- parameter extraction
- Obsidian publishing
- evidence preservation
- phase-level failure visibility

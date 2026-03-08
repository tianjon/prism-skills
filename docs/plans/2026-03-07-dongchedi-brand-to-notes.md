# Dongchedi Brand-to-Notes Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a brand-driven dongchedi pipeline that takes one brand name, captures verifiable snapshots, extracts series, configuration, and parameter data, and publishes structured notes into Obsidian.

**Architecture:** Keep the existing skill entrypoints, but refactor the internals into a staged pipeline with explicit run state, snapshot artifacts, page adapters, and a decoupled publishing layer.

**Tech Stack:** Python 3.11+, `browser-use`, `pydantic`, local JSON artifacts, `Obsidian-cli`, `unittest`.

---

## High-Level Tasks

1. Add runtime state and manifest handling
2. Persist search snapshots and search artifacts
3. Extract page adapters for search, series, and params pages
4. Refactor config and parameter extraction into stable pipeline stages
5. Split publishing from scraping logic
6. Add one canonical brand entrypoint
7. Add fixture-driven integration checks
8. Verify deterministic output structure

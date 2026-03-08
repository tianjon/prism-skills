"""Data models for dongchedi scraper."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CarModel(BaseModel):
    """A car model (series) from dongchedi."""

    name: str
    series_id: str
    price_range: str = ""
    level: str = ""  # 中型SUV, 中大型SUV, 中大型车, etc.
    energy_type: str = ""  # 纯电动, 增程式, 插电式混合动力, etc.


class CarConfig(BaseModel):
    """A specific configuration (trim) of a car model."""

    car_id: str
    car_name: str
    price: str = ""
    year: str = ""
    series_name: str = ""
    series_id: str = ""
    brand_name: str = ""
    brand: str = ""
    level: str = ""
    energy_type: str = ""
    is_target: bool = False  # Whether this is the target brand (not competitor)


class ParamItem(BaseModel):
    """A single parameter entry."""

    category: str
    name: str
    value: str


class ConfigWithParams(BaseModel):
    """A car config with its extracted parameters."""

    config: CarConfig
    params: list[ParamItem] = Field(default_factory=list)
    error: str | None = None


class CompetitorEntry(BaseModel):
    """A competitor model with tier classification."""

    model: CarModel
    tier: str  # A, B, C


class CompetitorMapping(BaseModel):
    """Competitor mapping for a target model."""

    target: CarModel
    competitors: dict[str, list[CarModel]] = Field(
        default_factory=lambda: {"A": [], "B": [], "C": []}
    )


class ChangeRecord(BaseModel):
    """Record of a change detected during update."""

    note_path: str
    change_type: str  # price_change, param_added, param_removed, param_changed, new_config, discontinued
    field: str = ""
    old_value: str = ""
    new_value: str = ""
    description: str = ""


class ScrapeResult(BaseModel):
    """Overall result of a scrape session."""

    total_configs: int = 0
    success_count: int = 0
    error_count: int = 0
    new_count: int = 0
    updated_count: int = 0
    unchanged_count: int = 0
    discontinued_count: int = 0
    changes: list[ChangeRecord] = Field(default_factory=list)

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import argparse

import yaml


VALID_AD_TYPES = {"image", "video"}
COMMON_AD_FIELDS = ("name", "type", "file", "headline", "body", "call_to_action", "link")


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ads: list[dict[str, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _require_fields(section: dict[str, Any], fields: tuple[str, ...], prefix: str, result: ValidationResult) -> None:
    for field_name in fields:
        if _is_blank(section.get(field_name)):
            result.errors.append(f"{prefix}.{field_name} is required")


def load_campaign(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Campaign file must contain a top-level mapping.")
    return data


def validate_campaign_data(data: dict[str, Any], campaign_path: Path) -> ValidationResult:
    result = ValidationResult()

    campaign = data.get("campaign")
    ad_set = data.get("ad_set")
    ads = data.get("ads")

    if not isinstance(campaign, dict):
        result.errors.append("campaign section is required")
    if not isinstance(ad_set, dict):
        result.errors.append("ad_set section is required")
    if not isinstance(ads, list) or not ads:
        result.errors.append("ads section must be a non-empty list")

    if result.errors:
        return result

    _require_fields(campaign, ("name", "objective"), "campaign", result)
    if campaign.get("daily_budget") is None and campaign.get("lifetime_budget") is None:
        result.errors.append("campaign.daily_budget or campaign.lifetime_budget is required")

    _require_fields(ad_set, ("name",), "ad_set", result)
    if not isinstance(ad_set.get("targeting"), dict):
        result.errors.append("ad_set.targeting must be a mapping")

    base_dir = campaign_path.parent

    for index, ad in enumerate(ads, start=1):
        if not isinstance(ad, dict):
            result.errors.append(f"ads[{index}] must be a mapping")
            continue

        _require_fields(ad, COMMON_AD_FIELDS, f"ads[{index}]", result)
        ad_type = ad.get("type")
        if ad_type not in VALID_AD_TYPES:
            result.errors.append(f"ads[{index}].type must be one of: image, video")

        asset_path = ad.get("file")
        if isinstance(asset_path, str) and asset_path.strip():
            resolved_asset = base_dir / asset_path
            if not resolved_asset.exists():
                result.errors.append(f"ads[{index}].file does not exist: {asset_path}")

        if ad_type == "video":
            if _is_blank(ad.get("thumbnail")):
                result.errors.append(f"ads[{index}].thumbnail is required for video ads")
            else:
                thumbnail_path = base_dir / str(ad["thumbnail"])
                if not thumbnail_path.exists():
                    result.errors.append(f"ads[{index}].thumbnail does not exist: {ad['thumbnail']}")

        if isinstance(ad.get("headline"), str) and len(ad["headline"]) > 40:
            result.warnings.append(f"ads[{index}].headline exceeds 40 characters")
        if isinstance(ad.get("body"), str) and len(ad["body"]) > 4096:
            result.warnings.append(f"ads[{index}].body exceeds 4096 characters")

        result.ads.append(
            {
                "index": str(index),
                "name": str(ad.get("name", "")),
                "type": str(ad.get("type", "")),
                "file": str(ad.get("file", "")),
            }
        )

    return result


def validate_campaign_file(path: Path) -> ValidationResult:
    return validate_campaign_data(load_campaign(path), path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Meta Ads campaign YAML file.")
    parser.add_argument("campaign_file", type=Path, help="Path to the campaign YAML file")
    args = parser.parse_args(argv)

    result = validate_campaign_file(args.campaign_file)

    print(f"Campaign file: {args.campaign_file}")
    for ad in result.ads:
        print(f"[{ad['index']}] {ad['type']}: {ad['name']} -> {ad['file']}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"- {warning}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"- {error}")
        return 1

    print("\nValidation passed.")
    return 0

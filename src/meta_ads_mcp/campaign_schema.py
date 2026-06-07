from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import argparse

import yaml


VALID_AD_TYPES = {"image", "video"}
VALID_DESTINATIONS = {"website", "whatsapp"}
WHATSAPP_AD_SET_DESTINATION_TYPES = {"WHATSAPP"}
COMMON_AD_FIELDS = ("name", "type", "file")


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
    has_whatsapp_ads = False

    for index, ad in enumerate(ads, start=1):
        if not isinstance(ad, dict):
            result.errors.append(f"ads[{index}] must be a mapping")
            continue

        _require_fields(ad, COMMON_AD_FIELDS, f"ads[{index}]", result)
        ad_type = ad.get("type")
        if ad_type not in VALID_AD_TYPES:
            result.errors.append(f"ads[{index}].type must be one of: image, video")

        destination = str(ad.get("destination", "website")).strip().lower()
        if destination not in VALID_DESTINATIONS:
            result.errors.append(f"ads[{index}].destination must be one of: website, whatsapp")
        if destination == "website":
            _require_fields(ad, ("call_to_action", "link"), f"ads[{index}]", result)
        if destination == "whatsapp":
            has_whatsapp_ads = True
            if _is_blank(ad.get("call_to_action")):
                result.warnings.append(f"ads[{index}].call_to_action is empty; SHOP_NOW will be used")
            elif ad.get("call_to_action") == "WHATSAPP_MESSAGE":
                result.warnings.append(f"ads[{index}].call_to_action should usually be SHOP_NOW for click-to-message ads")

        asset_path = ad.get("file")
        if isinstance(asset_path, str) and asset_path.strip():
            resolved_asset = base_dir / asset_path
            if not resolved_asset.exists():
                result.errors.append(f"ads[{index}].file does not exist: {asset_path}")

        if ad_type == "video" and not _is_blank(ad.get("thumbnail")):
            thumbnail_path = base_dir / str(ad["thumbnail"])
            if not thumbnail_path.exists():
                result.errors.append(f"ads[{index}].thumbnail does not exist: {ad['thumbnail']}")

        # Validate headline(s): accept single string or list
        headlines = ad.get("headlines") or ([ad["headline"]] if ad.get("headline") else [])
        if not headlines:
            result.errors.append(f"ads[{index}].headlines (or headline) is required")
        for h in headlines if isinstance(headlines, list) else [headlines]:
            if isinstance(h, str) and len(h) > 40:
                result.warnings.append(f"ads[{index}] headline exceeds 40 characters: '{h[:40]}…'")

        # Validate body/bodies
        bodies = ad.get("bodies") or ([ad["body"]] if ad.get("body") else [])
        if not bodies:
            result.errors.append(f"ads[{index}].bodies (or body) is required")
        for b in bodies if isinstance(bodies, list) else [bodies]:
            if isinstance(b, str) and len(b) > 4096:
                result.warnings.append(f"ads[{index}] body exceeds 4096 characters")

        result.ads.append(
            {
                "index": str(index),
                "name": str(ad.get("name", "")),
                "type": str(ad.get("type", "")),
                "file": str(ad.get("file", "")),
                "destination": destination,
            }
        )

    if has_whatsapp_ads:
        if ad_set.get("destination_type") not in WHATSAPP_AD_SET_DESTINATION_TYPES:
            result.errors.append(
                "ad_set.destination_type must be WHATSAPP when any ad uses destination: whatsapp"
            )
        promoted_object = ad_set.get("promoted_object")
        if not isinstance(promoted_object, dict) or _is_blank(promoted_object.get("page_id")):
            result.errors.append("ad_set.promoted_object.page_id is required for WhatsApp click-to-message ads")
        if not isinstance(promoted_object, dict) or _is_blank(promoted_object.get("whatsapp_phone_number")):
            result.errors.append(
                "ad_set.promoted_object.whatsapp_phone_number is required for WhatsApp click-to-message ads"
            )
        if campaign.get("objective") not in {"OUTCOME_SALES", "OUTCOME_ENGAGEMENT", "MESSAGES"}:
            result.warnings.append("campaign.objective is usually OUTCOME_SALES for the observed WhatsApp campaign")
        if ad_set.get("optimization_goal") != "CONVERSATIONS":
            result.warnings.append("ad_set.optimization_goal is usually CONVERSATIONS for WhatsApp ads")

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

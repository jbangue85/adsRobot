from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adset import AdSet
from meta_ads_mcp.client import get_ad_account


def list_ads(ad_set_id: str, limit: int = 50) -> list[dict]:
    """Lista los anuncios de un ad set."""
    get_ad_account()  # ensure API is initialized
    fields = [
        Ad.Field.id,
        Ad.Field.name,
        Ad.Field.status,
        Ad.Field.adset_id,
        Ad.Field.campaign_id,
        Ad.Field.creative,
        Ad.Field.created_time,
    ]
    ad_set = AdSet(ad_set_id)
    ads = ad_set.get_ads(fields=fields, params={"limit": limit})
    result = []
    for a in ads:
        ad_dict = dict(a)
        if "creative" in ad_dict:
            creative = ad_dict["creative"]
            ad_dict["creative_id"] = creative.get("id") if isinstance(creative, dict) else getattr(creative, "_data", {}).get("id")
            del ad_dict["creative"]
        result.append(ad_dict)
    return result


def update_ad_status(ad_id: str, status: str) -> dict:
    """
    Pausa o activa un anuncio.

    Args:
        ad_id: ID del anuncio.
        status: ACTIVE o PAUSED.
    """
    ad = Ad(ad_id)
    ad.update({Ad.Field.status: status})
    ad.remote_update()
    return {"id": ad_id, "status": status, "updated": True}

from facebook_business.adobjects.ad import Ad
from meta_ads_mcp.client import get_ad_account


def list_ads(ad_set_id: str, limit: int = 50) -> list[dict]:
    """Lista los anuncios de un ad set."""
    account = get_ad_account()
    fields = [
        Ad.Field.id,
        Ad.Field.name,
        Ad.Field.status,
        Ad.Field.adset_id,
        Ad.Field.campaign_id,
        Ad.Field.creative,
        Ad.Field.created_time,
    ]
    ads = account.get_ads(
        fields=fields,
        params={"adset_id": ad_set_id, "limit": limit},
    )
    return [dict(a) for a in ads]


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

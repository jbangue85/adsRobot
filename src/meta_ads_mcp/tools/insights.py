from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from meta_ads_mcp.client import get_ad_account, get_account_currency

_DEFAULT_FIELDS = [
    AdsInsights.Field.campaign_id,
    AdsInsights.Field.campaign_name,
    AdsInsights.Field.adset_id,
    AdsInsights.Field.adset_name,
    AdsInsights.Field.impressions,
    AdsInsights.Field.reach,
    AdsInsights.Field.clicks,
    AdsInsights.Field.spend,
    AdsInsights.Field.cpc,
    AdsInsights.Field.cpm,
    AdsInsights.Field.ctr,
    AdsInsights.Field.actions,
    AdsInsights.Field.action_values,
    AdsInsights.Field.date_start,
    AdsInsights.Field.date_stop,
]


def get_account_insights(
    date_preset: str = "last_30d",
    time_increment: int | None = None,
) -> list[dict]:
    """
    Obtiene métricas globales de la cuenta publicitaria.

    Args:
        date_preset: Rango de fechas predefinido: today, yesterday, last_7d,
                     last_14d, last_30d, last_month, last_quarter, last_year.
        time_increment: Si se especifica, devuelve datos por día (1) o por semana (7).
    """
    account = get_ad_account()
    params: dict = {"date_preset": date_preset, "level": "account"}
    if time_increment is not None:
        params["time_increment"] = time_increment

    currency = get_account_currency()
    insights = account.get_insights(fields=_DEFAULT_FIELDS, params=params)
    return [{**dict(i), "currency": currency} for i in insights]


def get_campaign_insights(
    campaign_id: str,
    date_preset: str = "last_30d",
    time_increment: int | None = None,
) -> list[dict]:
    """
    Obtiene métricas de una campaña específica.

    Args:
        campaign_id: ID de la campaña.
        date_preset: Rango de fechas: today, yesterday, last_7d, last_14d,
                     last_30d, last_month, last_quarter, last_year.
        time_increment: Desglose por día (1) o semana (7).
    """
    campaign = Campaign(campaign_id)
    params: dict = {"date_preset": date_preset, "level": "campaign"}
    if time_increment is not None:
        params["time_increment"] = time_increment

    currency = get_account_currency()
    insights = campaign.get_insights(fields=_DEFAULT_FIELDS, params=params)
    return [{**dict(i), "currency": currency} for i in insights]


def get_campaign_metrics(
    campaign_id: str,
    date_preset: str = "last_7d",
) -> dict:
    """
    Retorna métricas clave de una campaña: impresiones, clics, gasto, CTR y CPC.

    Args:
        campaign_id: ID de la campaña.
        date_preset: Rango de fechas: today, yesterday, last_7d, last_30d, etc.
    """
    campaign = Campaign(campaign_id)
    fields = [
        AdsInsights.Field.impressions,
        AdsInsights.Field.clicks,
        AdsInsights.Field.spend,
        AdsInsights.Field.ctr,
        AdsInsights.Field.cpc,
        AdsInsights.Field.reach,
        AdsInsights.Field.actions,
        AdsInsights.Field.date_start,
        AdsInsights.Field.date_stop,
    ]
    currency = get_account_currency()
    insights = campaign.get_insights(fields=fields, params={"date_preset": date_preset})
    return {**dict(insights[0]), "currency": currency} if insights else {}


def get_daily_spend(date_preset: str = "last_7d") -> list[dict]:
    """
    Retorna el gasto diario de la cuenta publicitaria.

    Args:
        date_preset: Rango de fechas: today, yesterday, last_7d, last_30d, etc.
    """
    account = get_ad_account()
    fields = [
        AdsInsights.Field.spend,
        AdsInsights.Field.date_start,
        AdsInsights.Field.date_stop,
    ]
    params = {"date_preset": date_preset, "time_increment": 1, "level": "account"}
    currency = get_account_currency()
    insights = account.get_insights(fields=fields, params=params)
    return [{**dict(i), "currency": currency} for i in insights]


def get_ad_set_insights(
    ad_set_id: str,
    date_preset: str = "last_30d",
    time_increment: int | None = None,
) -> list[dict]:
    """
    Obtiene métricas de un ad set específico.

    Args:
        ad_set_id: ID del ad set.
        date_preset: Rango de fechas: today, yesterday, last_7d, last_14d,
                     last_30d, last_month, last_quarter, last_year.
        time_increment: Desglose por día (1) o semana (7).
    """
    ad_set = AdSet(ad_set_id)
    params: dict = {"date_preset": date_preset, "level": "adset"}
    if time_increment is not None:
        params["time_increment"] = time_increment

    currency = get_account_currency()
    insights = ad_set.get_insights(fields=_DEFAULT_FIELDS, params=params)
    return [{**dict(i), "currency": currency} for i in insights]

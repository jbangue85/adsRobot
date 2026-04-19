from facebook_business.adobjects.adset import AdSet
from meta_ads_mcp.client import get_ad_account


def list_ad_sets(campaign_id: str, limit: int = 50) -> list[dict]:
    """Lista los ad sets de una campaña."""
    account = get_ad_account()
    fields = [
        AdSet.Field.id,
        AdSet.Field.name,
        AdSet.Field.status,
        AdSet.Field.daily_budget,
        AdSet.Field.lifetime_budget,
        AdSet.Field.budget_remaining,
        AdSet.Field.billing_event,
        AdSet.Field.optimization_goal,
        AdSet.Field.start_time,
        AdSet.Field.end_time,
    ]
    ad_sets = account.get_ad_sets(
        fields=fields,
        params={"campaign_id": campaign_id, "limit": limit},
    )
    return [dict(a) for a in ad_sets]


def create_ad_set(
    campaign_id: str,
    name: str,
    daily_budget: int | None = None,
    lifetime_budget: int | None = None,
    billing_event: str = "IMPRESSIONS",
    optimization_goal: str = "REACH",
    bid_strategy: str | None = None,
    bid_amount: int | None = None,
    promoted_object: dict | None = None,
    targeting: dict | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    status: str = "PAUSED",
) -> dict:
    """
    Crea un ad set dentro de una campaña.

    Args:
        campaign_id: ID de la campaña padre.
        name: Nombre del ad set.
        daily_budget: Presupuesto diario en centavos.
        lifetime_budget: Presupuesto total en centavos.
        billing_event: Evento de facturación (IMPRESSIONS, LINK_CLICKS, etc.).
        optimization_goal: Objetivo de optimización (REACH, LINK_CLICKS, CONVERSIONS, etc.).
        bid_strategy: Estrategia de puja (LOWEST_COST_WITHOUT_CAP, LOWEST_COST_WITH_BID_CAP, etc.).
        bid_amount: Monto de puja en centavos (opcional).
        targeting: Dict de targeting de Meta (geo_locations, age_min, age_max, etc.).
        start_time: Fecha de inicio en formato ISO 8601 (ej. "2024-01-01T00:00:00-0500").
        end_time: Fecha de fin en formato ISO 8601.
        status: ACTIVE o PAUSED (default: PAUSED).
    """
    account = get_ad_account()
    params = {
        AdSet.Field.name: name,
        AdSet.Field.campaign_id: campaign_id,
        AdSet.Field.billing_event: billing_event,
        AdSet.Field.optimization_goal: optimization_goal,
        AdSet.Field.status: status,
        AdSet.Field.targeting: targeting or {"geo_locations": {"countries": ["US"]}},
    }
    if daily_budget is not None:
        params[AdSet.Field.daily_budget] = daily_budget
    if lifetime_budget is not None:
        params[AdSet.Field.lifetime_budget] = lifetime_budget
    if bid_strategy is not None:
        params["bid_strategy"] = bid_strategy
    if bid_amount is not None:
        params[AdSet.Field.bid_amount] = bid_amount
    if promoted_object is not None:
        params["promoted_object"] = promoted_object
    if start_time is not None:
        params[AdSet.Field.start_time] = start_time
    if end_time is not None:
        params[AdSet.Field.end_time] = end_time

    ad_set = account.create_ad_set(fields=[AdSet.Field.id, AdSet.Field.name], params=params)
    return dict(ad_set)


def update_ad_set_status(ad_set_id: str, status: str) -> dict:
    """
    Pausa o activa un ad set.

    Args:
        ad_set_id: ID del ad set.
        status: ACTIVE o PAUSED.
    """
    ad_set = AdSet(ad_set_id)
    ad_set.update({AdSet.Field.status: status})
    ad_set.remote_update()
    return {"id": ad_set_id, "status": status, "updated": True}


def update_ad_set_budget(
    ad_set_id: str,
    daily_budget: int | None = None,
    lifetime_budget: int | None = None,
) -> dict:
    """
    Modifica el presupuesto de un ad set.

    Args:
        ad_set_id: ID del ad set.
        daily_budget: Nuevo presupuesto diario en centavos.
        lifetime_budget: Nuevo presupuesto total en centavos.
    """
    if daily_budget is None and lifetime_budget is None:
        raise ValueError("Se debe especificar daily_budget o lifetime_budget.")

    ad_set = AdSet(ad_set_id)
    updates: dict = {}
    if daily_budget is not None:
        updates[AdSet.Field.daily_budget] = daily_budget
    if lifetime_budget is not None:
        updates[AdSet.Field.lifetime_budget] = lifetime_budget

    ad_set.update(updates)
    ad_set.remote_update()
    return {"id": ad_set_id, **updates, "updated": True}

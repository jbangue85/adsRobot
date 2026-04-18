from facebook_business.adobjects.campaign import Campaign
from meta_ads_mcp.client import get_ad_account, get_account_currency


def list_campaigns(limit: int = 50) -> list[dict]:
    """Lista todas las campañas de la cuenta con estado, objetivo y presupuesto."""
    account = get_ad_account()
    currency = get_account_currency()
    fields = [
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.status,
        Campaign.Field.objective,
        Campaign.Field.daily_budget,
        Campaign.Field.lifetime_budget,
        Campaign.Field.budget_remaining,
        Campaign.Field.start_time,
        Campaign.Field.stop_time,
    ]
    campaigns = account.get_campaigns(fields=fields, params={"limit": limit})
    return [{**dict(c), "currency": currency} for c in campaigns]


def get_campaign(campaign_id: str) -> dict:
    """Obtiene el detalle completo de una campaña por ID."""
    fields = [
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.status,
        Campaign.Field.objective,
        Campaign.Field.daily_budget,
        Campaign.Field.lifetime_budget,
        Campaign.Field.budget_remaining,
        Campaign.Field.start_time,
        Campaign.Field.stop_time,
        Campaign.Field.bid_strategy,
    ]
    campaign = Campaign(campaign_id)
    campaign.remote_read(fields=fields)
    return {**dict(campaign), "currency": get_account_currency()}


def create_campaign(
    name: str,
    objective: str,
    status: str = "PAUSED",
    daily_budget: int | None = None,
    lifetime_budget: int | None = None,
    special_ad_categories: list[str] | None = None,
) -> dict:
    """
    Crea una nueva campaña.

    Args:
        name: Nombre de la campaña.
        objective: Objetivo (OUTCOME_TRAFFIC, OUTCOME_AWARENESS, OUTCOME_LEADS,
                   OUTCOME_SALES, OUTCOME_ENGAGEMENT, OUTCOME_APP_PROMOTION).
        status: Estado inicial — ACTIVE o PAUSED (default: PAUSED).
        daily_budget: Presupuesto diario en centavos (ej. 1000 = $10.00).
        lifetime_budget: Presupuesto total en centavos.
        special_ad_categories: Lista de categorías especiales (ej. ["CREDIT", "EMPLOYMENT"]).
                               Usar [] si no aplica.
    """
    account = get_ad_account()
    params = {
        Campaign.Field.name: name,
        Campaign.Field.objective: objective,
        Campaign.Field.status: status,
        Campaign.Field.special_ad_categories: special_ad_categories or [],
    }
    if daily_budget is not None:
        params[Campaign.Field.daily_budget] = daily_budget
    if lifetime_budget is not None:
        params[Campaign.Field.lifetime_budget] = lifetime_budget

    campaign = account.create_campaign(fields=[Campaign.Field.id, Campaign.Field.name], params=params)
    return dict(campaign)


def update_campaign_status(campaign_id: str, status: str) -> dict:
    """
    Pausa o activa una campaña.

    Args:
        campaign_id: ID de la campaña.
        status: ACTIVE o PAUSED.
    """
    campaign = Campaign(campaign_id)
    campaign.update({Campaign.Field.status: status})
    campaign.remote_update()
    return {"id": campaign_id, "status": status, "updated": True}


def get_active_campaigns() -> list[dict]:
    """Retorna todas las campañas con estado ACTIVE."""
    account = get_ad_account()
    fields = [
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.status,
        Campaign.Field.objective,
        Campaign.Field.daily_budget,
        Campaign.Field.lifetime_budget,
        Campaign.Field.budget_remaining,
        Campaign.Field.start_time,
        Campaign.Field.stop_time,
    ]
    params = {
        "filtering": [{"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}],
    }
    currency = get_account_currency()
    campaigns = account.get_campaigns(fields=fields, params=params)
    return [{**dict(c), "currency": currency} for c in campaigns]


def update_campaign_budget(
    campaign_id: str,
    daily_budget: int | None = None,
    lifetime_budget: int | None = None,
) -> dict:
    """
    Modifica el presupuesto de una campaña.

    Args:
        campaign_id: ID de la campaña.
        daily_budget: Nuevo presupuesto diario en centavos.
        lifetime_budget: Nuevo presupuesto total en centavos.
    """
    if daily_budget is None and lifetime_budget is None:
        raise ValueError("Se debe especificar daily_budget o lifetime_budget.")

    campaign = Campaign(campaign_id)
    updates: dict = {}
    if daily_budget is not None:
        updates[Campaign.Field.daily_budget] = daily_budget
    if lifetime_budget is not None:
        updates[Campaign.Field.lifetime_budget] = lifetime_budget

    campaign.update(updates)
    campaign.remote_update()
    return {"id": campaign_id, **updates, "updated": True}

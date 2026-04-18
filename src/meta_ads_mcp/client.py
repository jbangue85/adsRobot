import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

load_dotenv()

_api_initialized = False
_ad_account: AdAccount | None = None
_account_currency: str | None = None


def get_ad_account() -> AdAccount:
    global _api_initialized, _ad_account

    if not _api_initialized:
        app_id = os.environ["META_APP_ID"]
        app_secret = os.environ["META_APP_SECRET"]
        access_token = os.environ["META_ACCESS_TOKEN"]
        FacebookAdsApi.init(app_id, app_secret, access_token, api_version="v25.0")
        _api_initialized = True

    if _ad_account is None:
        account_id = os.environ["META_AD_ACCOUNT_ID"]
        _ad_account = AdAccount(account_id)

    return _ad_account


def get_account_currency() -> str:
    global _account_currency
    if _account_currency is None:
        account = get_ad_account()
        account.remote_read(fields=[AdAccount.Field.currency])
        _account_currency = account[AdAccount.Field.currency]
    return _account_currency

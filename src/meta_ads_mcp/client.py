import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

load_dotenv()

_api_initialized = False
_ad_account: AdAccount | None = None


def get_ad_account() -> AdAccount:
    global _api_initialized, _ad_account

    if not _api_initialized:
        app_id = os.environ["META_APP_ID"]
        app_secret = os.environ["META_APP_SECRET"]
        access_token = os.environ["META_ACCESS_TOKEN"]
        FacebookAdsApi.init(app_id, app_secret, access_token)
        _api_initialized = True

    if _ad_account is None:
        account_id = os.environ["META_AD_ACCOUNT_ID"]
        _ad_account = AdAccount(account_id)

    return _ad_account

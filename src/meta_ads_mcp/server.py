from mcp.server.fastmcp import FastMCP

from meta_ads_mcp.tools.campaigns import (
    list_campaigns,
    get_campaign,
    create_campaign,
    update_campaign_status,
    update_campaign_budget,
)
from meta_ads_mcp.tools.ad_sets import (
    list_ad_sets,
    create_ad_set,
    update_ad_set_status,
    update_ad_set_budget,
)
from meta_ads_mcp.tools.ads import list_ads, update_ad_status
from meta_ads_mcp.tools.creatives import (
    upload_image,
    upload_video,
    create_ad_creative_image,
    create_ad_creative_video,
    create_ad,
)
from meta_ads_mcp.tools.insights import (
    get_account_insights,
    get_campaign_insights,
    get_ad_set_insights,
)

mcp = FastMCP("meta-ads")

# Campaigns
mcp.tool()(list_campaigns)
mcp.tool()(get_campaign)
mcp.tool()(create_campaign)
mcp.tool()(update_campaign_status)
mcp.tool()(update_campaign_budget)

# Ad Sets
mcp.tool()(list_ad_sets)
mcp.tool()(create_ad_set)
mcp.tool()(update_ad_set_status)
mcp.tool()(update_ad_set_budget)

# Ads
mcp.tool()(list_ads)
mcp.tool()(update_ad_status)

# Creatives & assets
mcp.tool()(upload_image)
mcp.tool()(upload_video)
mcp.tool()(create_ad_creative_image)
mcp.tool()(create_ad_creative_video)
mcp.tool()(create_ad)

# Insights
mcp.tool()(get_account_insights)
mcp.tool()(get_campaign_insights)
mcp.tool()(get_ad_set_insights)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

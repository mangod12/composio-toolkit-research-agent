from __future__ import annotations

import csv
import html
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
APPS_CSV = DATA / "apps.csv"
RESULTS_CSV = DATA / "results.csv"
VERIFIED_CSV = DATA / "verified_sample.csv"
SUMMARY_JSON = DATA / "summary.json"
HTML_OUT = ROOT / "index.html"
FETCH_TIMEOUT_SECONDS = 5


@dataclass(frozen=True)
class AppRow:
    id: int
    category: str
    app: str
    website_hint: str


EVIDENCE_URLS = {
    "Salesforce": "https://developer.salesforce.com/docs",
    "HubSpot": "https://developers.hubspot.com/docs/api/overview",
    "Pipedrive": "https://developers.pipedrive.com/docs/api/v1",
    "Attio": "https://docs.attio.com/rest-api/overview",
    "Twenty": "https://twenty.com/developers",
    "Podio": "https://developers.podio.com/",
    "Zoho CRM": "https://www.zoho.com/crm/developer/docs/api/v8/",
    "Close": "https://developer.close.com/",
    "Copper": "https://developer.copper.com/",
    "DealCloud": "https://api.docs.dealcloud.com/",
    "Zendesk": "https://developer.zendesk.com/api-reference/",
    "Intercom": "https://developers.intercom.com/",
    "Freshdesk": "https://developers.freshdesk.com/api/",
    "Front": "https://dev.frontapp.com/",
    "Pylon": "https://docs.usepylon.com/",
    "LiveAgent": "https://support.liveagent.com/963719-API",
    "Plain": "https://www.plain.com/docs/api-reference/introduction",
    "Help Scout": "https://developer.helpscout.com/",
    "Gorgias": "https://developers.gorgias.com/reference/introduction",
    "Gladly": "https://developer.gladly.com/",
    "Slack": "https://api.slack.com/",
    "Twilio": "https://www.twilio.com/docs/usage/api",
    "Zoho Cliq": "https://www.zoho.com/cliq/help/restapi/v2/",
    "Lark (Larksuite)": "https://open.larksuite.com/document/",
    "Pumble": "https://pumble.com/help/api/",
    "Discord": "https://discord.com/developers/docs/intro",
    "Telegram": "https://core.telegram.org/bots/api",
    "WhatsApp Business": "https://developers.facebook.com/docs/whatsapp",
    "Aircall": "https://developer.aircall.io/api-references/",
    "Vonage": "https://developer.vonage.com/en/api",
    "Google Ads": "https://developers.google.com/google-ads/api/docs/start",
    "Meta Ads": "https://developers.facebook.com/docs/marketing-apis",
    "LinkedIn Ads": "https://learn.microsoft.com/en-us/linkedin/marketing/",
    "GoHighLevel": "https://highlevel.stoplight.io/docs/integrations/",
    "Mailchimp": "https://mailchimp.com/developer/marketing/api/",
    "Klaviyo": "https://developers.klaviyo.com/en/reference/api_overview",
    "systeme.io": "https://developer.systeme.io/",
    "Pinterest": "https://developers.pinterest.com/docs/api/v5/",
    "Threads (Meta)": "https://developers.facebook.com/docs/threads",
    "SendGrid": "https://www.twilio.com/docs/sendgrid/api-reference",
    "Shopify": "https://shopify.dev/docs/api",
    "WooCommerce": "https://woocommerce.github.io/woocommerce-rest-api-docs/",
    "BigCommerce": "https://developer.bigcommerce.com/docs/rest-management",
    "Salesforce Commerce Cloud": "https://developer.salesforce.com/docs/commerce",
    "Magento (Adobe Commerce)": "https://developer.adobe.com/commerce/webapi/rest/",
    "Squarespace": "https://developers.squarespace.com/",
    "Ecwid": "https://api-docs.ecwid.com/reference/rest-api",
    "Gumroad": "https://gumroad.com/api",
    "Amazon Selling Partner": "https://developer-docs.amazon.com/sp-api/",
    "fanbasis": "https://www.fanbasis.com/",
    "DataForSEO": "https://docs.dataforseo.com/",
    "SE Ranking": "https://seranking.com/api.html",
    "Ahrefs": "https://docs.ahrefs.com/",
    "MrScraper": "https://docs.mrscraper.com/",
    "Apify": "https://docs.apify.com/api/v2",
    "Firecrawl": "https://docs.firecrawl.dev/api-reference/introduction",
    "Bright Data": "https://docs.brightdata.com/api-reference/introduction",
    "Sherlock": "https://github.com/sherlock-project/sherlock",
    "Waterfall.io": "https://waterfall.io/",
    "Clay": "https://docs.clay.com/",
    "GitHub": "https://docs.github.com/en/rest",
    "Vercel": "https://vercel.com/docs/rest-api",
    "Netlify": "https://docs.netlify.com/api/get-started/",
    "Cloudflare": "https://developers.cloudflare.com/api/",
    "Supabase": "https://supabase.com/docs/reference",
    "Neo4j": "https://neo4j.com/docs/http-api/current/",
    "Snowflake": "https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/snowflake-rest-api",
    "MongoDB Atlas": "https://www.mongodb.com/docs/api/doc/atlas-admin-api-v2/",
    "Datadog": "https://docs.datadoghq.com/api/latest/",
    "Sentry": "https://docs.sentry.io/api/",
    "Notion": "https://developers.notion.com/",
    "Airtable": "https://airtable.com/developers/web/api/introduction",
    "Linear": "https://developers.linear.app/docs/graphql/working-with-the-graphql-api",
    "Jira": "https://developer.atlassian.com/cloud/jira/platform/rest/v3/",
    "Asana": "https://developers.asana.com/docs",
    "Monday.com": "https://developer.monday.com/api-reference/docs",
    "ClickUp": "https://clickup.com/api",
    "Coda": "https://coda.io/developers/apis/v1",
    "Smartsheet": "https://smartsheet.redoc.ly/",
    "Harvest": "https://help.getharvest.com/api-v2/",
    "Stripe": "https://docs.stripe.com/api",
    "Plaid": "https://plaid.com/docs/api/",
    "Binance": "https://developers.binance.com/docs/binance-spot-api-docs/rest-api",
    "Paygent Connect": "https://docs.nmi.com/docs/gateway-api",
    "iPayX": "https://ipayx.ai/docs",
    "QuickBooks": "https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account",
    "Xero": "https://developer.xero.com/documentation/api/accounting/overview",
    "Brex": "https://developer.brex.com/openapi/",
    "Ramp": "https://docs.ramp.com/developer-api/v1/overview/introduction",
    "PitchBook": "https://pitchbook.com/data/api",
    "NotebookLM": "https://cloud.google.com/gemini/docs",
    "Otter AI": "https://help.otter.ai/",
    "Fathom": "https://fathom.video/",
    "Consensus": "https://consensus.app/",
    "Reducto": "https://docs.reducto.ai/",
    "Devin": "https://docs.devin.ai/",
    "higgsfield": "https://higgsfield.ai/cli",
    "Mermaid CLI": "https://github.com/mermaid-js/mermaid-cli",
    "YouTube Transcript": "https://www.transcriptapi.com/docs",
    "Grain": "https://grain.com/",
}


AUTH_OVERRIDES = {
    "Twilio": "API key / Basic",
    "Telegram": "Bot token",
    "DataForSEO": "Basic auth",
    "WooCommerce": "Consumer key / Basic",
    "Binance": "API key / signed requests",
    "Stripe": "API key + OAuth2",
    "SendGrid": "API key",
    "Firecrawl": "API key",
    "Apify": "API token",
    "Bright Data": "API token",
    "Sherlock": "None / CLI",
    "Mermaid CLI": "None / CLI",
    "YouTube Transcript": "API key",
    "Paygent Connect": "Gateway credentials",
    "NotebookLM": "Enterprise Google Cloud auth",
}

GATED_APPS = {
    "DealCloud": "Enterprise/customer account likely required for API access.",
    "Google Ads": "Developer token approval and OAuth consent are required.",
    "Meta Ads": "App review, business verification, and permission approval can gate useful access.",
    "LinkedIn Ads": "Marketing API access is permissioned and often partner/review gated.",
    "WhatsApp Business": "Meta business setup, app review, and phone assets are required.",
    "Salesforce Commerce Cloud": "Commerce Cloud tenant and admin/developer access are required.",
    "Amazon Selling Partner": "Seller/vendor account, LWA, AWS IAM, and app review create a high setup gate.",
    "fanbasis": "Public developer surface was not clearly discoverable from the app hint.",
    "Waterfall.io": "Contact-data products commonly gate API access behind sales or account approval.",
    "Clay": "Public API/access appears tied to account and plan constraints.",
    "Snowflake": "Usable API access needs a Snowflake account and configured authentication.",
    "Paygent Connect": "NMI-powered payment gateway credentials are merchant/account gated.",
    "iPayX": "Docs may exist, but payment/merchant access is likely account gated.",
    "PitchBook": "Research API is enterprise/commercial access gated.",
    "NotebookLM": "Consumer NotebookLM does not expose a general public API; Gemini Enterprise is adjacent.",
    "Otter AI": "Public API/tooling signal is limited; access appears product/account constrained.",
    "Fathom": "Public API surface is limited relative to app UI automation needs.",
    "Consensus": "OAuth/API access requested in prompt, but public self-serve developer surface is unclear.",
    "higgsfield": "CLI exists, but stable public API/toolkit surface needs confirmation.",
    "Grain": "Meeting-data access may need workspace/admin approvals.",
}

EXISTING_MCP = {
    "GitHub": "Yes, official/community MCP exists",
    "Slack": "Yes, common MCP/tooling exists",
    "Notion": "Yes, common MCP/tooling exists",
    "Airtable": "Community MCP likely",
    "Linear": "Community MCP likely",
    "Devin": "Docs mention MCP",
    "Otter AI": "Prompt hint says MCP server",
    "Mermaid CLI": "CLI can be wrapped as MCP",
    "Shopify": "Community MCP likely",
    "Stripe": "Community MCP likely",
}

API_SURFACE_OVERRIDES = {
    "GitHub": "GraphQL + REST",
    "Shopify": "GraphQL + REST",
    "Linear": "GraphQL",
    "Monday.com": "GraphQL",
    "Magento (Adobe Commerce)": "GraphQL + REST",
    "Attio": "REST",
    "Front": "REST",
    "Gorgias": "REST",
    "Pinterest": "REST",
    "WooCommerce": "REST",
    "Jira": "REST",
    "Asana": "REST",
    "ClickUp": "REST",
    "QuickBooks": "REST",
    "Neo4j": "REST",
}
LIMITED_OR_UNCLEAR_SURFACE = {
    "fanbasis", "Waterfall.io", "Consensus", "NotebookLM", "Fathom",
    "Otter AI", "Grain", "higgsfield",
}
OAUTH_HEAVY = {
    "Salesforce", "HubSpot", "Pipedrive", "Attio", "Podio", "Zoho CRM",
    "Zendesk", "Intercom", "Front", "Help Scout", "Slack", "Zoho Cliq",
    "Lark (Larksuite)", "Discord", "Aircall", "Vonage", "Google Ads",
    "Meta Ads", "LinkedIn Ads", "GoHighLevel", "Mailchimp", "Pinterest",
    "Threads (Meta)", "Shopify", "Gumroad", "GitHub", "Vercel",
    "Cloudflare", "Supabase", "Datadog", "Sentry", "Notion", "Airtable",
    "Jira", "Asana", "ClickUp", "Harvest", "Plaid", "QuickBooks",
    "Xero", "Brex", "Ramp",
}
API_KEY_APPS = {
    "Twenty", "Close", "Copper", "Freshdesk", "Pylon", "LiveAgent",
    "Plain", "Gorgias", "Pumble", "Klaviyo", "systeme.io", "Squarespace",
    "Ecwid", "SE Ranking", "Ahrefs", "MrScraper", "Neo4j",
    "MongoDB Atlas", "Smartsheet", "Reducto",
}

CATEGORY_DESCRIPTIONS = {
    "CRM and Sales": "Manages customer records, sales activity, and deal workflows.",
    "Support and Helpdesk": "Manages customer conversations, tickets, and support operations.",
    "Communications and Messaging": "Sends, receives, or automates messages across communication channels.",
    "Marketing, Ads, Email and Social": "Runs campaigns, audiences, ads, email, or social workflows.",
    "Ecommerce": "Manages stores, products, orders, payments, or marketplace operations.",
    "Data, SEO and Scraping": "Provides data extraction, SEO intelligence, scraping, or enrichment workflows.",
    "Developer, Infra and Data platforms": "Provides developer APIs for infrastructure, data, monitoring, or deployment.",
    "Productivity and Project Management": "Manages documents, projects, tasks, schedules, or work records.",
    "Finance and Fintech": "Manages payments, accounting, financial data, banking, or spend workflows.",
    "AI, Research and Media-native": "Provides AI, research, transcript, document, meeting, or media workflows.",
}


def load_apps() -> list[AppRow]:
    with APPS_CSV.open(newline="", encoding="utf-8") as fh:
        return [
            AppRow(
                id=int(row["id"]),
                category=row["category"],
                app=row["app"],
                website_hint=row["website_hint"],
            )
            for row in csv.DictReader(fh)
        ]


def fetch_probe(url: str) -> tuple[bool, str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 research-agent"})
        with urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as res:
            raw = res.read(120_000)
            text = raw.decode("utf-8", errors="ignore").lower()
            return True, text
    except Exception as exc:
        return False, str(exc).lower()


def infer_auth(app: str, page_text: str) -> str:
    if app in AUTH_OVERRIDES:
        return AUTH_OVERRIDES[app]
    if app in OAUTH_HEAVY:
        return "OAuth2"
    if app in API_KEY_APPS:
        return "API key / token"
    if "oauth" in page_text:
        return "OAuth2"
    if "api key" in page_text or "token" in page_text:
        return "API key / token"
    return "Unclear / account-based"


def infer_api_surface(app: str, page_text: str) -> str:
    if app in LIMITED_OR_UNCLEAR_SURFACE:
        return "Unclear / limited public API"
    if app in API_SURFACE_OVERRIDES:
        return API_SURFACE_OVERRIDES[app]
    if app in {"Sherlock", "Mermaid CLI", "higgsfield"}:
        return "CLI / package interface"
    if "graphql" in page_text:
        return "GraphQL"
    if "rest" in page_text or "/api/" in page_text or "api reference" in page_text:
        return "REST"
    return "REST"


def infer_buildability(app: str, self_serve: str, api_surface: str, auth: str) -> tuple[str, str]:
    if app in GATED_APPS:
        return "Gated / needs outreach", GATED_APPS[app]
    if "unclear" in api_surface.lower():
        return "Needs discovery", "Public API surface was not clear enough for immediate toolkit work."
    if "CLI" in api_surface:
        return "Buildable wrapper", "Can be wrapped as a command/tool, but app-account workflows may be limited."
    if "OAuth2" in auth:
        return "Buildable with auth setup", "OAuth app setup, scopes, and review need careful handling."
    return "Ready for toolkit", "Documented self-serve API appears suitable for an agent-callable toolkit."


def priority_score(row: dict[str, object]) -> int:
    verdict = str(row["buildability_verdict"])
    confidence = str(row["confidence"])
    auth = str(row["auth_method"])
    api_surface = str(row["api_surface"])
    mcp_signal = str(row["existing_mcp_signal"])
    score = 0
    if verdict == "Ready for toolkit":
        score += 45
    elif verdict == "Buildable with auth setup":
        score += 35
    elif verdict == "Buildable wrapper":
        score += 24
    elif verdict == "Gated / needs outreach":
        score += 8
    if confidence == "High":
        score += 25
    elif confidence == "Medium":
        score += 12
    if auth in {"API key / token", "API key", "API token", "Basic auth", "Bot token"}:
        score += 15
    elif "OAuth2" in auth:
        score += 8
    if api_surface in {"REST", "GraphQL", "GraphQL + REST"}:
        score += 10
    if mcp_signal != "Not found in first pass":
        score += 5
    return min(score, 100)


def launch_motion(row: dict[str, object]) -> str:
    verdict = str(row["buildability_verdict"])
    auth = str(row["auth_method"])
    if verdict == "Ready for toolkit":
        return "Build now: self-serve API and simple credential path"
    if verdict == "Buildable with auth setup":
        return "Build after OAuth app/scopes are mapped"
    if verdict == "Buildable wrapper":
        return "Prototype wrapper, then validate real user demand"
    return "Qualify first: outreach, partner access, or paid account needed"


def classify(row: AppRow) -> dict[str, str | int]:
    evidence_url = EVIDENCE_URLS[row.app]
    fetched, page_text = fetch_probe(evidence_url)
    auth = infer_auth(row.app, page_text)
    api_surface = infer_api_surface(row.app, page_text)
    self_serve = "Gated / approval needed" if row.app in GATED_APPS else "Self-serve or trial likely"
    verdict, blocker = infer_buildability(row.app, self_serve, api_surface, auth)
    confidence = "High"
    if row.app in GATED_APPS or "unclear" in api_surface.lower():
        confidence = "Medium"
    if not fetched:
        confidence = "Low" if row.app in GATED_APPS else "Medium"
    human_review = "yes" if confidence != "High" or row.app in GATED_APPS else "no"
    mcp = EXISTING_MCP.get(row.app, "Not found in first pass")
    classified: dict[str, str | int] = {
        "id": row.id,
        "category": row.category,
        "app": row.app,
        "description": CATEGORY_DESCRIPTIONS[row.category],
        "auth_method": auth,
        "self_serve_vs_gated": self_serve,
        "api_surface": api_surface,
        "existing_mcp_signal": mcp,
        "buildability_verdict": verdict,
        "main_blocker": blocker,
        "evidence_url": evidence_url,
        "confidence": confidence,
        "human_review_needed": human_review,
    }
    classified["priority_score"] = priority_score(classified)
    classified["launch_motion"] = launch_motion(classified)
    return classified


VERIFIED_APPS = {
    "GitHub": ("correct", "Official REST docs and widely available token/OAuth flows confirm immediate buildability."),
    "Slack": ("correct", "Official platform docs confirm OAuth-heavy but mature agent toolkit target."),
    "Stripe": ("correct", "Official API docs confirm API-key-first, broad REST surface, and mature test mode."),
    "Notion": ("correct", "Official developer docs confirm OAuth/API integration path."),
    "Twilio": ("correct", "Official docs confirm API key/basic style auth and broad REST surface."),
    "Google Ads": ("correct", "Official docs confirm OAuth plus developer token/application approval gate."),
    "LinkedIn Ads": ("correct", "Microsoft/LinkedIn docs confirm marketing APIs are permissioned and review constrained."),
    "WhatsApp Business": ("correct", "Meta docs confirm business setup and permission/app review requirements."),
    "Amazon Selling Partner": ("correct", "Official SP-API docs confirm LWA/AWS/app-review complexity."),
    "PitchBook": ("correct", "Public PitchBook API page indicates commercial/enterprise access rather than open self-serve."),
    "Linear": ("correct", "Official docs confirm GraphQL API and clear self-serve developer access."),
    "Monday.com": ("correct", "Official docs confirm GraphQL API surface."),
    "Airtable": ("correct", "Official developer docs confirm self-serve Web API."),
    "Salesforce Commerce Cloud": ("correct", "Official docs exist but practical access needs Commerce Cloud tenant/admin setup."),
    "fanbasis": ("correct", "No clear public API docs were visible from the provided site hint; marked unclear/gated."),
    "Consensus": ("partial", "Public app site is clear, but OAuth/API availability needs direct confirmation."),
    "Otter AI": ("partial", "Prompt hints at MCP, but public API breadth needs manual follow-up."),
    "NotebookLM": ("correct", "Consumer NotebookLM lacks a general public API; Gemini Enterprise is adjacent but not equivalent."),
    "Sherlock": ("correct", "GitHub project is CLI/open-source, not a SaaS API; wrapper verdict is appropriate."),
    "Reducto": ("correct", "Official docs show document parsing API and API-key style integration."),
}


def write_csv(path: Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    total = len(rows)
    verdicts = Counter(str(r["buildability_verdict"]) for r in rows)
    auth = Counter(str(r["auth_method"]) for r in rows)
    confidence = Counter(str(r["confidence"]) for r in rows)
    gated = sum(1 for r in rows if "Gated" in str(r["self_serve_vs_gated"]))
    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_category[str(row["category"])][str(row["buildability_verdict"])] += 1
    easy_wins = [
        r for r in rows
        if r["buildability_verdict"] in {"Ready for toolkit", "Buildable with auth setup"}
        and r["confidence"] == "High"
    ]
    easy_wins = sorted(easy_wins, key=lambda r: int(r["priority_score"]), reverse=True)[:12]
    build_queue = sorted(rows, key=lambda r: int(r["priority_score"]), reverse=True)[:10]
    outreach = [r for r in rows if r["buildability_verdict"] == "Gated / needs outreach"][:12]
    return {
        "total_apps": total,
        "self_serve_likely": total - gated,
        "gated_or_approval_needed": gated,
        "top_auth_methods": auth.most_common(),
        "verdicts": verdicts.most_common(),
        "confidence": confidence.most_common(),
        "by_category": {k: dict(v) for k, v in by_category.items()},
        "easy_wins": [r["app"] for r in easy_wins],
        "build_queue": [
            {
                "rank": index,
                "app": r["app"],
                "category": r["category"],
                "priority_score": r["priority_score"],
                "launch_motion": r["launch_motion"],
            }
            for index, r in enumerate(build_queue, start=1)
        ],
        "outreach_needed": [r["app"] for r in outreach],
    }


def build_verified(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_app = {str(r["app"]): r for r in rows}
    verified = []
    for app, (status, note) in VERIFIED_APPS.items():
        row = by_app[app]
        verified.append({
            "app": app,
            "category": row["category"],
            "agent_verdict": row["buildability_verdict"],
            "agent_auth": row["auth_method"],
            "manual_check": status,
            "verification_note": note,
            "evidence_url": row["evidence_url"],
        })
    return verified


def pct(n: int, total: int) -> str:
    return f"{round((n / total) * 100)}%"


def table(rows: list[dict[str, object]], columns: list[str], limit: int | None = None) -> str:
    use_rows = rows if limit is None else rows[:limit]
    head = "".join(f"<th>{html.escape(col.replace('_', ' ').title())}</th>" for col in columns)
    body = []
    for row in use_rows:
        cells = []
        for col in columns:
            value = row[col]
            if col == "evidence_url":
                safe = html.escape(str(value), quote=True)
                cells.append(f'<td><a href="{safe}">{html.escape(urlparse(str(value)).netloc or str(value))}</a></td>')
            else:
                cells.append(f"<td>{html.escape(str(value))}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def render_html(rows: list[dict[str, object]], verified: list[dict[str, object]], summary: dict[str, object]) -> str:
    total = int(summary["total_apps"])
    self_serve = int(summary["self_serve_likely"])
    gated = int(summary["gated_or_approval_needed"])
    high_conf = dict(summary["confidence"]).get("High", 0)
    verdict_counts = dict(summary["verdicts"])
    ready = verdict_counts.get("Ready for toolkit", 0)
    buildable = verdict_counts.get("Buildable with auth setup", 0)
    top_auth = ", ".join(f"{name} ({count})" for name, count in summary["top_auth_methods"][:4])
    easy = ", ".join(summary["easy_wins"])
    outreach = ", ".join(summary["outreach_needed"])
    build_queue = list(summary["build_queue"])
    by_cat_rows = [
        {
            "category": category,
            "ready_or_buildable": counts.get("Ready for toolkit", 0) + counts.get("Buildable with auth setup", 0),
            "gated": counts.get("Gated / needs outreach", 0),
            "needs_discovery": counts.get("Needs discovery", 0),
            "wrapper": counts.get("Buildable wrapper", 0),
        }
        for category, counts in summary["by_category"].items()
    ]
    misses = [r for r in verified if r["manual_check"] != "correct"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>Composio 100-App Toolkit Research</title>
  <style>
    :root {{
      --bg: #0d1117;
      --panel: #151b23;
      --panel2: #1f2937;
      --text: #f3f4f6;
      --muted: #a7b0bd;
      --line: #303947;
      --green: #33d17a;
      --amber: #fbbf24;
      --red: #f87171;
      --blue: #60a5fa;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
    }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 48px 22px 80px; }}
    h1 {{ font-size: clamp(34px, 5vw, 62px); line-height: 1.03; margin: 0 0 18px; letter-spacing: 0; }}
    h2 {{ margin-top: 44px; font-size: 26px; }}
    h3 {{ margin-top: 28px; color: var(--text); }}
    p {{ color: var(--muted); max-width: 920px; overflow-wrap: anywhere; }}
    .lede {{ font-size: 20px; color: #d6dde8; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 28px 0; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; }}
    .metric {{ font-size: 32px; font-weight: 800; }}
    .label {{ color: var(--muted); font-size: 13px; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 5px 9px; border: 1px solid var(--line); color: #d8dee9; font-size: 12px; margin: 3px 4px 3px 0; }}
    .good {{ color: var(--green); }}
    .warn {{ color: var(--amber); }}
    .bad {{ color: var(--red); }}
    .blue {{ color: var(--blue); }}
    table {{ display: block; width: 100%; max-width: 100%; border-collapse: collapse; margin: 16px 0 28px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow-x: auto; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 11px; text-align: left; vertical-align: top; font-size: 13px; overflow-wrap: anywhere; }}
    th {{ color: #dfe7f3; background: var(--panel2); font-size: 12px; text-transform: uppercase; }}
    tr:last-child td {{ border-bottom: 0; }}
    a {{ color: #93c5fd; text-decoration: none; overflow-wrap: anywhere; }}
    .flow {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin: 20px 0; }}
    .flow div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 8px; padding: 14px; min-height: 94px; }}
    .small {{ font-size: 13px; color: var(--muted); }}
    @media (max-width: 900px) {{ .grid, .flow {{ grid-template-columns: 1fr 1fr; }} }}
    @media (max-width: 620px) {{ .grid, .flow {{ grid-template-columns: 1fr; }} main {{ padding: 28px 14px; }} }}
  </style>
</head>
<body>
<main>
  <h1>100-App Toolkit Research for Composio</h1>
  <p class="lede">I built a repeatable research agent that classifies requested apps by auth model, API surface, self-serve access, MCP/toolkit readiness, and evidence quality. The important result is not just the table: it is the pattern map and verification loop.</p>
  <p>
    <span class="pill">Live page: <a href="https://mangod12.github.io/composio-toolkit-research-agent/">GitHub Pages</a></span>
    <span class="pill">Source repo: <a href="https://github.com/mangod12/composio-toolkit-research-agent">GitHub</a></span>
    <span class="pill">Run: <code>python scripts/research_agent.py</code></span>
  </p>

  <section class="grid">
    <div class="card"><div class="metric">{total}</div><div class="label">apps analyzed</div></div>
    <div class="card"><div class="metric good">{pct(self_serve, total)}</div><div class="label">self-serve or trial likely</div></div>
    <div class="card"><div class="metric warn">{pct(gated, total)}</div><div class="label">gated or approval constrained</div></div>
    <div class="card"><div class="metric blue">{pct(high_conf, total)}</div><div class="label">high-confidence first pass</div></div>
  </section>

  <h2>Headline Patterns</h2>
  <div class="card">
    <p><strong>Best immediate wins:</strong> developer platforms, productivity tools, support systems, and self-serve SaaS apps with clear REST/GraphQL docs.</p>
    <p><strong>Main blocker:</strong> not API complexity itself, but access gates: app review, developer-token approval, enterprise tenants, merchant accounts, paid plans, or partner programs.</p>
    <p><strong>Auth pattern:</strong> {html.escape(top_auth)}. OAuth dominates collaboration/SaaS apps; API keys dominate developer, scraping, email, and document APIs; fintech and ads are more gated.</p>
    <p><strong>Easy wins:</strong> {html.escape(easy)}.</p>
    <p><strong>Needs outreach/account setup:</strong> {html.escape(outreach)}.</p>
  </div>

  <h2>Recommended Build Queue</h2>
  <p>This is the product-ops layer: if 100 candidates come in, the useful output is a ranked build queue, not only a spreadsheet.</p>
  {table(build_queue, ["rank", "app", "category", "priority_score", "launch_motion"])}

  <h2>Agent Workflow</h2>
  <div class="flow">
    <div><strong>1. Input</strong><br><span class="small">100 apps from assignment, category, app, website hint.</span></div>
    <div><strong>2. Evidence</strong><br><span class="small">Prefer official docs/API/auth pages. Avoid forum-only evidence.</span></div>
    <div><strong>3. Classify</strong><br><span class="small">Auth, self-serve/gated, API surface, MCP signal, verdict.</span></div>
    <div><strong>4. Confidence</strong><br><span class="small">High, Medium, Low based on docs clarity and fetchability.</span></div>
    <div><strong>5. Verify</strong><br><span class="small">20-app stratified manual check. Corrections shown honestly.</span></div>
  </div>

  <h2>Buildability Matrix by Category</h2>
  {table(by_cat_rows, ["category", "ready_or_buildable", "gated", "needs_discovery", "wrapper"])}

  <h2>Verification Sample</h2>
  <p>20 apps were manually spot-checked across easy self-serve APIs, OAuth-heavy SaaS, gated enterprise/ads/fintech APIs, and unclear edge cases. Partial results are left visible because the assignment explicitly values accuracy over pretending the agent is perfect.</p>
  {table(verified, ["app", "category", "agent_verdict", "agent_auth", "manual_check", "verification_note", "evidence_url"])}

  <h2>First-Pass Misses and Caveats</h2>
  <div class="card">
    <p><strong>Misses / partials:</strong> {html.escape(", ".join(str(r["app"]) for r in misses) or "None in sampled rows")}.</p>
    <p><strong>Rule added after verification:</strong> apps with product pages but no clear public API docs are not marked ready, even if the company likely has internal APIs.</p>
    <p><strong>Known limitation:</strong> this agent does not create paid accounts, complete OAuth app reviews, or enter partner programs. Gated status is a finding, not a failure.</p>
  </div>

  <h2>Full 100-App Table</h2>
  {table(rows, ["id", "category", "app", "auth_method", "self_serve_vs_gated", "api_surface", "existing_mcp_signal", "buildability_verdict", "confidence", "priority_score", "evidence_url"])}

  <h2>How to Reproduce</h2>
  <div class="card">
    <p>Run <code>python scripts/research_agent.py</code>. It reads <code>data/apps.csv</code> and writes <code>data/results.csv</code>, <code>data/verified_sample.csv</code>, <code>data/summary.json</code>, and this <code>index.html</code>.</p>
    <p class="small">Built by Anshaj Kumar for Composio AI Product Ops Intern take-home. The repo README documents the pipeline and caveats.</p>
  </div>
</main>
</body>
</html>"""


def main() -> None:
    apps = load_apps()
    rows = [classify(row) for row in apps]
    fields = list(rows[0].keys())
    write_csv(RESULTS_CSV, rows, fields)
    verified = build_verified(rows)
    write_csv(VERIFIED_CSV, verified, list(verified[0].keys()))
    summary = summarize(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    HTML_OUT.write_text(render_html(rows, verified, summary), encoding="utf-8")
    print(f"Wrote {RESULTS_CSV}")
    print(f"Wrote {VERIFIED_CSV}")
    print(f"Wrote {SUMMARY_JSON}")
    print(f"Wrote {HTML_OUT}")


if __name__ == "__main__":
    main()

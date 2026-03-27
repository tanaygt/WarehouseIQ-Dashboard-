"""
╔══════════════════════════════════════════════════════════════╗
║        Warehouse Intelligence Dashboard  v1.0               ║
║        Built by Tanay Shrivastava                           ║
║        AI • Data • Supply Chain                             ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
import time

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG  ── must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WarehouseIQ | Intelligence Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
_defaults = {
    "dark_mode": True,
    "chat_history": [],
    "show_insights": False,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────
# THEME PALETTES
# ─────────────────────────────────────────────────────────────────
DARK = {
    "bg":           "#0D0B09",
    "sidebar":      "#110E0A",
    "card":         "#1A1510",
    "card_border":  "#2C2118",
    "hover":        "#221A10",
    "text":         "#F0E8DC",
    "text2":        "#A8967C",
    "text3":        "#6B5540",
    "accent":       "#C9A84C",
    "accent2":      "#8B6520",
    "accent_light": "#E8CA7A",
    "accent_glow":  "rgba(201,168,76,0.15)",
    "success":      "#5A8C48",
    "danger":       "#A84848",
    "grid":         "#2C2118",
    "mode":         "dark",
}

LIGHT = {
    "bg":           "#F8F4EE",
    "sidebar":      "#EDE5D8",
    "card":         "#FFFFFF",
    "card_border":  "#DDD0BE",
    "hover":        "#F5EDE0",
    "text":         "#1A1008",
    "text2":        "#5A3E28",
    "text3":        "#8B6540",
    "accent":       "#7A5410",
    "accent2":      "#B8860B",
    "accent_light": "#C8980C",
    "accent_glow":  "rgba(122,84,16,0.12)",
    "success":      "#2E6B1A",
    "danger":       "#8B2020",
    "grid":         "#DDD0BE",
    "mode":         "light",
}


def T():
    return DARK if st.session_state.dark_mode else LIGHT


# ─────────────────────────────────────────────────────────────────
# DATA GENERATION
# ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Generate 3 years of realistic warehouse data with seasonality & growth."""
    np.random.seed(42)
    now = datetime.now()
    rows = []

    for yr in [2024, 2025, 2026]:
        for mo in range(1, 13):
            # Skip months in the future
            if yr > now.year:
                continue
            if yr == now.year and mo > now.month:
                continue

            # Seasonal curve: peak Nov–Dec, dip Jan–Feb
            s = 1.0 + 0.35 * np.sin((mo - 2) * np.pi / 6)
            # Year-over-year growth
            g = 1.0 + (yr - 2024) * 0.18

            orders  = max(500, int(np.random.normal(1100, 130) * s * g))
            revenue = round(orders * np.random.uniform(48, 72), 2)
            # Delays improve over years (efficiency gains)
            delay   = max(0.5, round(np.random.normal(4.5, 1.2) / (1 + (yr - 2024) * 0.08), 2))
            returns = max(0, int(np.random.normal(orders * 0.05, orders * 0.012)))

            rows.append({
                "Year":            yr,
                "Month":           mo,
                "Month_Name":      datetime(yr, mo, 1).strftime("%b"),
                "Month_Year":      datetime(yr, mo, 1).strftime("%b %Y"),
                "Orders":          orders,
                "Revenue":         revenue,
                "Avg_Delay_Hours": delay,
                "Returns":         returns,
                "Return_Rate":     round(returns / orders * 100, 2),
            })

    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df[["Year", "Month"]].assign(Day=1))
    df["Rev_Per_Order"] = (df["Revenue"] / df["Orders"]).round(2)
    return df


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
def fmt_money(n: float) -> str:
    if n >= 1_000_000:
        return f"${n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"${n / 1_000:.1f}K"
    return f"${n:.0f}"


def hex_to_rgba(hex_color: str, alpha: float = 0.18) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def base_layout(t: dict, title: str = "", height: int = 340) -> dict:
    """Shared Plotly layout for all charts."""
    return dict(
        title=dict(
            text=title,
            font=dict(family="DM Sans", size=13, color=t["text2"]),
            x=0, pad=dict(l=2, t=4),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=t["text2"], size=11),
        height=height,
        margin=dict(l=8, r=8, t=44, b=8),
        xaxis=dict(
            gridcolor=t["grid"], gridwidth=0.5,
            linecolor=t["grid"],
            tickfont=dict(color=t["text3"], size=10),
            showgrid=True, zeroline=False,
        ),
        yaxis=dict(
            gridcolor=t["grid"], gridwidth=0.5,
            linecolor="rgba(0,0,0,0)",
            tickfont=dict(color=t["text3"], size=10),
            showgrid=True, zeroline=False,
        ),
        legend=dict(
            font=dict(color=t["text2"], size=11),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="right",  x=1,
        ),
        hoverlabel=dict(
            bgcolor=t["card"],
            font_color=t["text"],
            bordercolor=t["accent"],
            font_size=12,
        ),
    )


# ─────────────────────────────────────────────────────────────────
# RULE-BASED AI CHATBOT
# ─────────────────────────────────────────────────────────────────
def ai_respond(user_msg: str, df: pd.DataFrame) -> str:
    msg = user_msg.lower().strip()

    # Aggregate stats
    total_orders  = int(df["Orders"].sum())
    total_rev     = df["Revenue"].sum()
    avg_delay     = df["Avg_Delay_Hours"].mean()
    total_returns = int(df["Returns"].sum())
    ret_rate      = df["Return_Rate"].mean()

    yr_stats = df.groupby("Year").agg(
        Orders=("Orders", "sum"),
        Revenue=("Revenue", "sum"),
        Delay=("Avg_Delay_Hours", "mean"),
        Returns=("Returns", "sum"),
        RetRate=("Return_Rate", "mean"),
    ).reset_index()

    best_mo    = df.loc[df["Orders"].idxmax()]
    worst_del  = df.loc[df["Avg_Delay_Hours"].idxmax()]
    best_rev   = df.loc[df["Revenue"].idxmax()]

    # ── Greetings ────────────────────────────────────────────────
    if any(w in msg for w in ["hi", "hello", "hey", "good morning", "good evening", "greet"]):
        return (
            "👋 Hello! I'm **WarehouseIQ Assistant** — your supply chain intelligence engine.\n\n"
            "I can answer questions about **orders, revenue, delays, returns, and trends**.\n"
            "Type `help` to see everything I can do."
        )

    # ── Help ─────────────────────────────────────────────────────
    if any(w in msg for w in ["help", "what can you", "commands", "menu", "options"]):
        return (
            "Here's what you can ask me:\n\n"
            "📦 **Orders** — *total orders / orders in 2025 / best month*\n"
            "💰 **Revenue** — *total revenue / revenue 2024 / average revenue*\n"
            "⏱ **Delays** — *average delay / worst delay / delay trend*\n"
            "↩️ **Returns** — *total returns / return rate / highest returns*\n"
            "📈 **Trends** — *year over year / growth / performance summary*\n"
            "📊 **Summary** — *overview / full report / all metrics*"
        )

    # ── Orders ───────────────────────────────────────────────────
    if "order" in msg:
        for yr in [2024, 2025, 2026]:
            if str(yr) in msg:
                row = yr_stats[yr_stats.Year == yr]
                if row.empty:
                    return f"⚠️ No data available for {yr} in your current filter."
                v = int(row["Orders"].values[0])
                return f"📦 **{yr} Order Volume**: **{v:,} orders**\nMonthly avg: {v//12:,} orders/month."
        if any(w in msg for w in ["best", "peak", "highest", "max", "top"]):
            return (
                f"🏆 **Peak Month**: **{best_mo['Month_Name']} {best_mo['Year']}**\n"
                f"Orders: **{int(best_mo['Orders']):,}** — the highest single month on record."
            )
        if any(w in msg for w in ["avg", "average", "mean", "monthly"]):
            avg = df["Orders"].mean()
            return f"📦 **Average Monthly Orders**: **{avg:,.0f}**\nBest: {int(best_mo['Orders']):,} | Worst: {int(df['Orders'].min()):,}"
        return (
            f"📦 **Total Orders**: **{total_orders:,}**\n"
            f"Monthly avg: {total_orders // len(df):,} | "
            f"Best month: {best_mo['Month_Name']} {best_mo['Year']} ({int(best_mo['Orders']):,} orders)\n\n"
            "💡 Ask about a specific year: *orders in 2025*"
        )

    # ── Revenue ──────────────────────────────────────────────────
    if any(w in msg for w in ["revenue", "sales", "income", "money", "earning", "profit"]):
        for yr in [2024, 2025, 2026]:
            if str(yr) in msg:
                row = yr_stats[yr_stats.Year == yr]
                if row.empty:
                    return f"⚠️ No data for {yr}."
                v = row["Revenue"].values[0]
                return f"💰 **{yr} Revenue**: **{fmt_money(v)}**\nMonthly avg: {fmt_money(v/12)}"
        if any(w in msg for w in ["avg", "average", "mean", "monthly"]):
            return f"💰 **Average Monthly Revenue**: **{fmt_money(df['Revenue'].mean())}**"
        if any(w in msg for w in ["best", "peak", "highest", "max"]):
            return (
                f"💰 **Best Revenue Month**: **{best_rev['Month_Name']} {best_rev['Year']}**\n"
                f"Revenue: **{fmt_money(best_rev['Revenue'])}** | "
                f"Rev/Order: ${best_rev['Rev_Per_Order']:.0f}"
            )
        return (
            f"💰 **Total Revenue**: **{fmt_money(total_rev)}**\n"
            f"Monthly avg: {fmt_money(df['Revenue'].mean())} | "
            f"Rev/Order avg: ${df['Rev_Per_Order'].mean():.0f}\n\n"
            "💡 Ask: *revenue in 2025* or *best revenue month*"
        )

    # ── Delays ───────────────────────────────────────────────────
    if any(w in msg for w in ["delay", "late", "slow", "fulfil", "shipping time", "lead time"]):
        if any(w in msg for w in ["worst", "highest", "max", "bad"]):
            return (
                f"⚠️ **Worst Delay**: **{worst_del['Avg_Delay_Hours']:.1f} hrs**\n"
                f"Recorded in {worst_del['Month_Name']} {worst_del['Year']} — "
                f"{worst_del['Avg_Delay_Hours'] - 3:.1f} hrs above the 3-hr target."
            )
        if any(w in msg for w in ["trend", "improving", "better", "worse", "change"]):
            years_avail = sorted(yr_stats["Year"].unique())
            if len(years_avail) >= 2:
                d1 = yr_stats[yr_stats.Year == years_avail[-2]]["Delay"].values[0]
                d2 = yr_stats[yr_stats.Year == years_avail[-1]]["Delay"].values[0]
                chg = d2 - d1
                emoji = "📉 Improving" if chg < 0 else "📈 Worsening"
                return (
                    f"⏱ **Delay Trend**: {emoji}\n"
                    f"{years_avail[-2]}: {d1:.1f} hrs → {years_avail[-1]}: {d2:.1f} hrs "
                    f"({'−' if chg < 0 else '+'}{abs(chg):.1f} hrs)"
                )
        for yr in [2024, 2025, 2026]:
            if str(yr) in msg:
                row = yr_stats[yr_stats.Year == yr]
                if row.empty:
                    return f"⚠️ No data for {yr}."
                d = row["Delay"].values[0]
                status = "✅ On target" if d <= 3.0 else "⚠️ Above target"
                return f"⏱ **{yr} Avg Delay**: **{d:.1f} hrs** — {status} (target: < 3.0 hrs)"
        status = "✅ On target" if avg_delay <= 3.0 else "⚠️ Above target"
        return (
            f"⏱ **Average Delay**: **{avg_delay:.1f} hrs** — {status}\n"
            f"Target: < 3.0 hrs | Worst: {worst_del['Avg_Delay_Hours']:.1f} hrs\n\n"
            "💡 Ask: *delay trend* or *worst delay*"
        )

    # ── Returns ──────────────────────────────────────────────────
    if any(w in msg for w in ["return", "refund", "reject", "sent back"]):
        if "rate" in msg:
            benchmark = "✅ Below benchmark" if ret_rate < 5.0 else "⚠️ Above benchmark"
            return (
                f"↩️ **Avg Return Rate**: **{ret_rate:.1f}%** — {benchmark}\n"
                f"Industry benchmark: 5–8% for e-commerce fulfilment."
            )
        if any(w in msg for w in ["worst", "highest", "max"]):
            worst_ret = df.loc[df["Returns"].idxmax()]
            return (
                f"↩️ **Peak Returns**: **{int(worst_ret['Returns']):,} units**\n"
                f"Month: {worst_ret['Month_Name']} {worst_ret['Year']} "
                f"({worst_ret['Return_Rate']:.1f}% return rate)"
            )
        for yr in [2024, 2025, 2026]:
            if str(yr) in msg:
                row = yr_stats[yr_stats.Year == yr]
                if row.empty:
                    return f"⚠️ No data for {yr}."
                v = int(row["Returns"].values[0])
                r = row["RetRate"].values[0]
                return f"↩️ **{yr} Returns**: **{v:,} units** ({r:.1f}% return rate)"
        return (
            f"↩️ **Total Returns**: **{total_returns:,} units**\n"
            f"Avg return rate: {ret_rate:.1f}% of total orders.\n\n"
            "💡 Ask: *return rate* or *highest returns*"
        )

    # ── Trends / YoY ─────────────────────────────────────────────
    if any(w in msg for w in ["trend", "growth", "yoy", "year over year", "compare", "change", "improve"]):
        yrs = sorted(yr_stats["Year"].unique())
        if len(yrs) < 2:
            return "📊 Need at least 2 years of data for trend comparison."
        y1, y2 = yr_stats[yr_stats.Year == yrs[-2]].iloc[0], yr_stats[yr_stats.Year == yrs[-1]].iloc[0]
        o_chg  = (y2.Orders  - y1.Orders)  / y1.Orders  * 100
        r_chg  = (y2.Revenue - y1.Revenue) / y1.Revenue * 100
        d_chg  = y2.Delay   - y1.Delay
        rt_chg = y2.RetRate - y1.RetRate
        return (
            f"📈 **Year-over-Year: {int(yrs[-2])} → {int(yrs[-1])}**\n\n"
            f"• Orders:   {'+' if o_chg > 0 else ''}{o_chg:.1f}% "
            f"({'Growth ✅' if o_chg > 0 else 'Decline ⚠️'})\n"
            f"• Revenue:  {'+' if r_chg > 0 else ''}{r_chg:.1f}% "
            f"({'Growth ✅' if r_chg > 0 else 'Decline ⚠️'})\n"
            f"• Delays:   {'+' if d_chg > 0 else ''}{d_chg:.1f} hrs "
            f"({'Worsening ⚠️' if d_chg > 0 else 'Improving ✅'})\n"
            f"• Returns:  {'+' if rt_chg > 0 else ''}{rt_chg:.1f}% "
            f"({'Rising ⚠️' if rt_chg > 0 else 'Falling ✅'})"
        )

    # ── Full Summary ─────────────────────────────────────────────
    if any(w in msg for w in ["summary", "overview", "all", "everything", "report", "full"]):
        return (
            "📊 **Warehouse Intelligence Summary**\n\n"
            f"• **Total Orders**:   {total_orders:,}\n"
            f"• **Total Revenue**:  {fmt_money(total_rev)}\n"
            f"• **Avg Delay**:      {avg_delay:.1f} hrs\n"
            f"• **Total Returns**:  {total_returns:,} ({ret_rate:.1f}% return rate)\n"
            f"• **Best Month**:     {best_mo['Month_Name']} {best_mo['Year']} "
            f"({int(best_mo['Orders']):,} orders)\n"
            f"• **Best Revenue**:   {best_rev['Month_Name']} {best_rev['Year']} "
            f"({fmt_money(best_rev['Revenue'])})\n"
            f"• **Data Range**:     2024 – 2026"
        )

    # ── Default ──────────────────────────────────────────────────
    return (
        "🤔 I'm not sure about that. Try asking about:\n"
        "**orders**, **revenue**, **delays**, **returns**, **trends**, or **summary**\n\n"
        "Type `help` to see all options."
    )


# ─────────────────────────────────────────────────────────────────
# SMART INSIGHTS ENGINE
# ─────────────────────────────────────────────────────────────────
def generate_insights(df: pd.DataFrame) -> list[dict]:
    insights = []
    yr_stats = df.groupby("Year").agg(
        Orders=("Orders", "sum"),
        Revenue=("Revenue", "sum"),
        Delay=("Avg_Delay_Hours", "mean"),
        Returns=("Returns", "sum"),
        RetRate=("Return_Rate", "mean"),
    ).reset_index()

    yrs = sorted(yr_stats["Year"].unique())

    if len(yrs) >= 2:
        prev, curr = yr_stats[yr_stats.Year == yrs[-2]].iloc[0], yr_stats[yr_stats.Year == yrs[-1]].iloc[0]
        o_g  = (curr.Orders  - prev.Orders)  / prev.Orders  * 100
        r_g  = (curr.Revenue - prev.Revenue) / prev.Revenue * 100
        d_g  = curr.Delay    - prev.Delay
        rt_g = curr.RetRate  - prev.RetRate

        # 1 — Orders
        insights.append({
            "icon":  "📈" if o_g > 0 else "📉",
            "title": f"Order Volume {'Up' if o_g > 0 else 'Down'} {abs(o_g):.1f}%",
            "body":  (
                f"Orders moved from {int(prev.Orders):,} to {int(curr.Orders):,} units "
                f"({int(yrs[-2])} → {int(yrs[-1])}).\n"
                + ("Momentum is strong — consider expanding storage capacity and labour headcount."
                   if o_g > 0 else
                   "Investigate demand drivers: check marketing ROI, product assortment, and pricing.")
            ),
        })
        # 2 — Revenue
        insights.append({
            "icon":  "💰" if r_g > 0 else "⚠️",
            "title": f"Revenue {'Grew' if r_g > 0 else 'Declined'} {abs(r_g):.1f}%",
            "body":  (
                f"Revenue shifted from {fmt_money(prev.Revenue)} to {fmt_money(curr.Revenue)}. "
                + ("Revenue grew faster than orders — rev/order improved. Expand premium lines."
                   if r_g > o_g else
                   "Revenue growth lagged order growth. Review pricing strategy and product mix.")
            ),
        })
        # 3 — Delay
        if d_g < 0:
            insights.append({
                "icon":  "✅",
                "title": f"Fulfilment Speed Improved by {abs(d_g):.1f} hrs",
                "body":  (
                    f"Avg delay dropped from {prev.Delay:.1f} hrs to {curr.Delay:.1f} hrs — "
                    f"{'below target ✅' if curr.Delay < 3.0 else 'still above 3-hr target ⚠️'}. "
                    "Keep investing in automation and route optimisation."
                ),
            })
        else:
            insights.append({
                "icon":  "⚠️",
                "title": f"Fulfillment Delays Rose by {d_g:.1f} hrs",
                "body":  (
                    f"Delays increased from {prev.Delay:.1f} to {curr.Delay:.1f} hrs. "
                    "Recommended actions: automate pick-pack for top SKUs, add flex staff "
                    "during peak months, and audit bottleneck zones in the warehouse."
                ),
            })
        # 4 — Returns
        if rt_g > 0:
            insights.append({
                "icon":  "⚠️",
                "title": f"Return Rate Rising (+{rt_g:.1f} pp)",
                "body":  (
                    f"Return rate went from {prev.RetRate:.1f}% to {curr.RetRate:.1f}%. "
                    "Audit top return reasons (packaging damage, sizing, product description mismatch). "
                    "Goal: bring below 4% through quality checks."
                ),
            })
        else:
            insights.append({
                "icon":  "✅",
                "title": f"Return Rate Improving ({rt_g:.1f} pp)",
                "body":  (
                    f"Return rate fell from {prev.RetRate:.1f}% to {curr.RetRate:.1f}%. "
                    "Continue investing in accurate product descriptions, better packaging, "
                    "and post-purchase QC audits."
                ),
            })

    # 5 — Peak season
    peak = df.loc[df["Orders"].idxmax()]
    trough = df.loc[df["Orders"].idxmin()]
    insights.append({
        "icon":  "🏔️",
        "title": f"Peak Demand: {peak['Month_Name']} {peak['Year']}",
        "body":  (
            f"Highest volume: {int(peak['Orders']):,} orders in {peak['Month_Name']} {peak['Year']}. "
            f"Lowest: {int(trough['Orders']):,} orders in {trough['Month_Name']} {trough['Year']}. "
            "Pre-stock 6–8 weeks before peak. Use the trough period for warehouse reorganisation."
        ),
    })
    # 6 — Rev/Order optimisation
    df2 = df.copy()
    best_rpo = df2.loc[df2["Rev_Per_Order"].idxmax()]
    insights.append({
        "icon":  "💡",
        "title": "Revenue per Order Optimisation",
        "body":  (
            f"Best rev/order was ${best_rpo['Rev_Per_Order']:.0f} "
            f"({best_rpo['Month_Name']} {best_rpo['Year']}). "
            "Introduce bundle offers, upsell at checkout, and personalise "
            "recommendations to lift this metric across all months."
        ),
    })

    return insights


# ─────────────────────────────────────────────────────────────────
# CSS INJECTION
# ─────────────────────────────────────────────────────────────────
def inject_css():
    t = T()
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

/* ── Base ─────────────────────────────────────────────────── */
html, body, .stApp {{
    background-color: {t['bg']} !important;
    font-family: 'DM Sans', sans-serif;
    color: {t['text']};
}}
* {{ box-sizing: border-box; }}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background-color: {t['sidebar']} !important;
    border-right: 1px solid {t['card_border']} !important;
}}
[data-testid="stSidebar"] * {{ color: {t['text']} !important; }}
[data-testid="stSidebar"] label {{
    font-size: 10px !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {t['text3']} !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] .stMarkdown p {{
    font-size: 12px;
    color: {t['text2']} !important;
}}

/* ── Typography ───────────────────────────────────────────── */
h1, h2, h3 {{
    font-family: 'Playfair Display', serif !important;
    color: {t['text']} !important;
    letter-spacing: -0.01em;
}}
p, li, span {{ color: {t['text']}; }}

/* ── KPI Cards ────────────────────────────────────────────── */
.kpi-card {{
    background: {t['card']};
    border: 1px solid {t['card_border']};
    border-radius: 14px;
    padding: 22px 22px 18px;
    position: relative;
    overflow: hidden;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    cursor: default;
    min-height: 138px;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {t['accent']}, {t['accent_light']}, transparent);
    opacity: 0.9;
}}
.kpi-card:hover {{
    border-color: {t['accent']};
    box-shadow: 0 6px 30px {t['accent_glow']};
    transform: translateY(-3px);
}}
.kpi-icon {{
    position: absolute;
    top: 20px; right: 20px;
    font-size: 24px;
    opacity: 0.25;
    transition: opacity 0.2s;
}}
.kpi-card:hover .kpi-icon {{ opacity: 0.5; }}
.kpi-label {{
    font-size: 10px;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: {t['text3']};
    font-weight: 600;
    margin-bottom: 10px;
}}
.kpi-value {{
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    font-weight: 700;
    color: {t['text']};
    line-height: 1.1;
    letter-spacing: -0.02em;
}}
.kpi-sub {{
    font-size: 11px;
    color: {t['text3']};
    margin-top: 8px;
}}
.kpi-trend-up   {{ color: {t['success']}; font-size: 11px; font-weight: 600; }}
.kpi-trend-down {{ color: {t['danger']};  font-size: 11px; font-weight: 600; }}
.kpi-trend-neutral {{ color: {t['text3']};font-size: 11px; }}

/* ── Chart wrapper ────────────────────────────────────────── */
.chart-card {{
    background: {t['card']};
    border: 1px solid {t['card_border']};
    border-radius: 14px;
    padding: 18px 18px 8px;
    margin-bottom: 18px;
    transition: box-shadow 0.2s;
}}
.chart-card:hover {{
    box-shadow: 0 4px 20px {t['accent_glow']};
}}

/* ── Section labels ───────────────────────────────────────── */
.section-label {{
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {t['text3']};
    font-weight: 600;
    margin-bottom: 2px;
}}
.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 600;
    color: {t['text']};
    margin-bottom: 18px;
}}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {{
    background-color: {t['accent']} !important;
    color: #0D0B09 !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.03em !important;
    padding: 10px 22px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    box-shadow: 0 2px 8px {t['accent_glow']} !important;
}}
.stButton > button:hover {{
    background-color: {t['accent2']} !important;
    box-shadow: 0 4px 18px {t['accent_glow']} !important;
    transform: translateY(-2px) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
}}

/* ── Download button ──────────────────────────────────────── */
.stDownloadButton > button {{
    background: transparent !important;
    border: 1px solid {t['accent']} !important;
    color: {t['accent']} !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 10px 22px !important;
    transition: all 0.2s ease !important;
    width: 100%;
}}
.stDownloadButton > button:hover {{
    background-color: {t['accent_glow']} !important;
    box-shadow: 0 2px 12px {t['accent_glow']} !important;
}}

/* ── Tabs ─────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background-color: {t['card']} !important;
    border-radius: 11px !important;
    border: 1px solid {t['card_border']} !important;
    padding: 5px !important;
    gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {t['text2']} !important;
    background: transparent !important;
    border: none !important;
    padding: 9px 20px !important;
    transition: all 0.18s ease !important;
}}
.stTabs [aria-selected="true"] {{
    background-color: {t['accent']} !important;
    color: #0D0B09 !important;
    font-weight: 600 !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background-color: {t['hover']} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 22px !important; }}

/* ── Selects ──────────────────────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {{
    background-color: {t['card']} !important;
    border-color: {t['card_border']} !important;
    border-radius: 9px !important;
    color: {t['text']} !important;
}}
.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {{
    border-color: {t['accent']} !important;
}}

/* ── Text input ───────────────────────────────────────────── */
.stTextInput > div > div > input {{
    background: {t['card']} !important;
    border-color: {t['card_border']} !important;
    color: {t['text']} !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}}
.stTextInput > div > div > input::placeholder {{ color: {t['text3']} !important; }}
.stTextInput > div > div > input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
}}

/* ── Dataframe ────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid {t['card_border']} !important;
}}

/* ── Chat bubbles ─────────────────────────────────────────── */
.chat-user {{
    background: {t['accent_glow']};
    border: 1px solid {t['card_border']};
    border-radius: 14px 14px 2px 14px;
    padding: 12px 16px;
    margin: 8px 0;
    margin-left: 18%;
    color: {t['text']};
    font-size: 13px;
    line-height: 1.55;
}}
.chat-bot {{
    background: {t['card']};
    border: 1px solid {t['card_border']};
    border-radius: 2px 14px 14px 14px;
    padding: 12px 16px;
    margin: 8px 0;
    margin-right: 18%;
    color: {t['text']};
    font-size: 13px;
    line-height: 1.55;
}}
.chat-label {{
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {t['accent']};
    font-weight: 700;
    margin-bottom: 5px;
}}
.quick-prompt-btn {{
    display: inline-block;
    background: {t['card']};
    border: 1px solid {t['card_border']};
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 12px;
    color: {t['text2']};
    cursor: pointer;
    margin: 3px;
    transition: all 0.15s;
}}
.quick-prompt-btn:hover {{
    border-color: {t['accent']};
    color: {t['accent']};
}}

/* ── Insight cards ────────────────────────────────────────── */
.insight-block {{
    background: {t['card']};
    border: 1px solid {t['card_border']};
    border-left: 3px solid {t['accent']};
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin: 10px 0;
    transition: box-shadow 0.2s;
}}
.insight-block:hover {{
    box-shadow: 0 4px 20px {t['accent_glow']};
}}
.insight-block-title {{
    font-weight: 600;
    font-size: 14px;
    color: {t['text']};
    margin-bottom: 6px;
}}
.insight-block-body {{
    font-size: 13px;
    color: {t['text2']};
    line-height: 1.6;
}}

/* ── Pill badges ──────────────────────────────────────────── */
.pill {{
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    border-radius: 20px;
    padding: 3px 10px;
}}
.pill-green {{
    background: rgba(90,140,72,0.15);
    color: {t['success']};
    border: 1px solid rgba(90,140,72,0.35);
}}
.pill-amber {{
    background: {t['accent_glow']};
    color: {t['accent']};
    border: 1px solid rgba(201,168,76,0.35);
}}

/* ── Brand in sidebar ─────────────────────────────────────── */
.brand-wrap {{
    padding: 6px 0 22px;
}}
.brand-sub {{
    font-size: 9px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {t['accent']};
    font-weight: 700;
}}
.brand-title {{
    font-family: 'Playfair Display', serif;
    font-size: 21px;
    font-weight: 700;
    color: {t['text']};
    line-height: 1.15;
    margin-top: 2px;
}}

/* ── Last updated ─────────────────────────────────────────── */
.last-updated {{
    font-size: 10px;
    color: {t['text3']};
    background: {t['card']};
    border: 1px solid {t['card_border']};
    border-radius: 20px;
    padding: 4px 12px;
    letter-spacing: 0.04em;
    display: inline-block;
}}

/* ── Separator ────────────────────────────────────────────── */
.sep {{
    border: none;
    border-top: 1px solid {t['card_border']};
    margin: 0;
}}

/* ── Footer ───────────────────────────────────────────────── */
.footer {{
    text-align: center;
    padding: 28px 0 10px;
    color: {t['text3']};
    font-size: 12px;
    border-top: 1px solid {t['card_border']};
    margin-top: 48px;
    letter-spacing: 0.04em;
}}
.footer .accent {{ color: {t['accent']}; font-weight: 600; }}
.footer .dim {{ font-size: 10px; opacity: 0.45; margin-top: 4px; }}

/* ── Scrollbar ────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {t['text3']}; border-radius: 3px; }}

/* ── Spinner ──────────────────────────────────────────────── */
.stSpinner > div {{ border-top-color: {t['accent']} !important; }}

/* ── Recommendation card ──────────────────────────────────── */
.rec-card {{
    background: {t['card']};
    border: 1px solid {t['card_border']};
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}}
.rec-title {{
    font-size: 13px;
    font-weight: 600;
    color: {t['accent']};
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.rec-body {{
    font-size: 12px;
    color: {t['text2']};
    line-height: 1.6;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────
def main():
    inject_css()
    t = T()
    df_all = load_data()
    available_years = sorted(df_all["Year"].unique().tolist())

    # ── SIDEBAR ──────────────────────────────────────────────────
    with st.sidebar:
        # Brand
        st.markdown("""
        <div class="brand-wrap">
            <div class="brand-sub">Warehouse Intelligence</div>
            <div class="brand-title">WarehouseIQ</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<hr class="sep">', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Theme toggle
        toggle_label = "☀️  Switch to Light Mode" if st.session_state.dark_mode else "🌙  Switch to Dark Mode"
        if st.button(toggle_label, key="theme_toggle", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Filters</div>', unsafe_allow_html=True)

        selected_years = st.multiselect(
            "Year",
            options=available_years,
            default=available_years,
            key="year_sel",
        )
        month_map = {i: datetime(2000, i, 1).strftime("%B") for i in range(1, 13)}
        selected_months = st.multiselect(
            "Month (optional)",
            options=list(month_map.keys()),
            format_func=lambda x: month_map[x],
            default=[],
            key="month_sel",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)

        # Build filtered df for export
        exp_yrs = selected_years if selected_years else available_years
        df_exp = df_all[df_all["Year"].isin(exp_yrs)].copy()
        if selected_months:
            df_exp = df_exp[df_exp["Month"].isin(selected_months)].copy()

        buf = io.StringIO()
        df_exp.to_csv(buf, index=False)
        st.download_button(
            "📥  Download Filtered CSV",
            data=buf.getvalue(),
            file_name=f"warehouse_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="last-updated">🕐 {datetime.now().strftime("%d %b %Y, %H:%M")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # Sidebar mini-stats
        st.markdown('<div class="section-label">Quick Stats</div>', unsafe_allow_html=True)
        qs_df = df_all[df_all["Year"].isin(exp_yrs)]
        st.markdown(f"""
        <div style="font-size:12px;color:{t['text2']};line-height:2">
        📅 &nbsp;Months of data: <strong>{len(qs_df)}</strong><br>
        📦 &nbsp;Total orders: <strong>{qs_df['Orders'].sum():,}</strong><br>
        💰 &nbsp;Total revenue: <strong>{fmt_money(qs_df['Revenue'].sum())}</strong>
        </div>
        """, unsafe_allow_html=True)

    # ── APPLY FILTERS ────────────────────────────────────────────
    years = selected_years if selected_years else available_years
    df = df_all[df_all["Year"].isin(years)].copy()
    if selected_months:
        df = df[df["Month"].isin(selected_months)].copy()

    if df.empty:
        st.warning("⚠️ No data for the selected filters. Please adjust your selections.")
        return

    # ── PAGE HEADER ──────────────────────────────────────────────
    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_l:
        yr_label = (
            " & ".join(map(str, sorted(years)))
            if len(years) <= 3
            else f"{min(years)}–{max(years)}"
        )
        st.markdown(f"""
        <div style="padding:8px 0 2px">
            <div class="section-label">Supply Chain · Operations Centre</div>
            <h1 style="font-size:32px;margin:4px 0 0;line-height:1.1">
                Warehouse Intelligence Dashboard
            </h1>
        </div>
        """, unsafe_allow_html=True)
    with hdr_r:
        st.markdown(f"""
        <div style="text-align:right;padding:20px 0 0">
            <span class="pill pill-green">● Live</span>
            &nbsp;
            <span class="pill pill-amber">{yr_label}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<hr class="sep" style="margin:14px 0 26px">', unsafe_allow_html=True)

    # ── KPI METRICS ──────────────────────────────────────────────
    total_orders  = int(df["Orders"].sum())
    total_rev     = df["Revenue"].sum()
    avg_delay     = df["Avg_Delay_Hours"].mean()
    total_returns = int(df["Returns"].sum())
    avg_ret_rate  = df["Return_Rate"].mean()
    months_count  = len(df)

    # Trend vs previous period
    def yoy_trend(col_name, agg="sum", good="up"):
        if len(years) == 1 and years[0] in available_years:
            idx = available_years.index(years[0])
            if idx > 0:
                prev_yr = available_years[idx - 1]
                df_prev = df_all[df_all["Year"] == prev_yr]
                if selected_months:
                    df_prev = df_prev[df_prev["Month"].isin(selected_months)]
                if not df_prev.empty:
                    prev_v = df_prev[col_name].sum() if agg == "sum" else df_prev[col_name].mean()
                    curr_v = df[col_name].sum()      if agg == "sum" else df[col_name].mean()
                    if prev_v > 0:
                        pct = (curr_v - prev_v) / prev_v * 100
                        up  = pct > 0
                        is_good = (up and good == "up") or (not up and good == "down")
                        arrow = "▲" if up else "▼"
                        cls   = "kpi-trend-up" if is_good else "kpi-trend-down"
                        return f'<span class="{cls}">{arrow} {abs(pct):.1f}% vs {prev_yr}</span>'
        return ""

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        {
            "col": k1,
            "icon": "📦",
            "label": "Total Orders",
            "value": f"{total_orders:,}",
            "sub": f"{total_orders // months_count:,} avg / month",
            "trend": yoy_trend("Orders", "sum", "up"),
        },
        {
            "col": k2,
            "icon": "💰",
            "label": "Total Revenue",
            "value": fmt_money(total_rev),
            "sub": f"{fmt_money(total_rev / months_count)} avg / month",
            "trend": yoy_trend("Revenue", "sum", "up"),
        },
        {
            "col": k3,
            "icon": "⏱",
            "label": "Avg Delay",
            "value": f"{avg_delay:.1f} hrs",
            "sub": "Target < 3.0 hrs",
            "trend": yoy_trend("Avg_Delay_Hours", "mean", "down"),
        },
        {
            "col": k4,
            "icon": "↩️",
            "label": "Total Returns",
            "value": f"{total_returns:,}",
            "sub": f"{avg_ret_rate:.1f}% return rate",
            "trend": yoy_trend("Returns", "sum", "down"),
        },
    ]
    for kpi in kpis:
        with kpi["col"]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{kpi['icon']}</div>
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-value">{kpi['value']}</div>
                <div class="kpi-sub">{kpi['sub']}</div>
                <div style="margin-top:7px">{kpi['trend']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS ─────────────────────────────────────────────────────
    tab_ana, tab_ins, tab_ai, tab_raw = st.tabs(
        ["📊  Analytics", "🧠  Smart Insights", "🤖  AI Assistant", "📋  Raw Data"]
    )

    # ────────────────────────────────────────────────────────────
    # TAB 1 — ANALYTICS
    # ────────────────────────────────────────────────────────────
    with tab_ana:
        YEAR_COLORS = [t["accent"], t["accent2"], t["accent_light"]]

        # Row 1 ─ Orders+Revenue trend · Returns scatter
        r1c1, r1c2 = st.columns([3, 2])

        with r1c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(
                    x=df["Month_Year"], y=df["Orders"],
                    name="Orders",
                    marker_color=t["accent"],
                    marker_opacity=0.82,
                    hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
                ),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=df["Month_Year"], y=df["Revenue"],
                    name="Revenue",
                    mode="lines+markers",
                    line=dict(color=t["text2"], width=2),
                    marker=dict(size=5, color=t["text2"],
                                line=dict(color=t["card"], width=1.5)),
                    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
                ),
                secondary_y=True,
            )
            lo = base_layout(t, "Monthly Orders & Revenue Trend", 335)
            fig.update_layout(**lo)
            fig.update_yaxes(
                secondary_y=False,
                gridcolor=t["grid"], tickfont=dict(color=t["text3"]),
                title_text="", showgrid=True,
            )
            fig.update_yaxes(
                secondary_y=True,
                gridcolor="rgba(0,0,0,0)", tickfont=dict(color=t["text3"]),
                title_text="", showgrid=False,
                tickprefix="$",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with r1c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df["Orders"], y=df["Returns"],
                mode="markers",
                text=df["Month_Year"],
                marker=dict(
                    size=11,
                    color=df["Return_Rate"],
                    colorscale=[[0, t["card"]], [0.4, t["accent2"]], [1, t["accent_light"]]],
                    showscale=True,
                    colorbar=dict(
                        title="Return %",
                        tickfont=dict(color=t["text3"], size=9),
                        len=0.75, thickness=10,
                        outlinewidth=0,
                    ),
                    line=dict(width=1, color=t["card_border"]),
                    opacity=0.88,
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>Orders: %{x:,}"
                    "<br>Returns: %{y:,}<extra></extra>"
                ),
            ))
            lo2 = base_layout(t, "Returns vs Orders · Coloured by Return Rate %", 335)
            lo2["xaxis"]["title"] = dict(text="Orders", font=dict(color=t["text3"], size=10))
            lo2["yaxis"]["title"] = dict(text="Returns", font=dict(color=t["text3"], size=10))
            fig2.update_layout(**lo2)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Row 2 ─ Delay bar · Area demand
        r2c1, r2c2 = st.columns(2)

        with r2c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            bar_colors = [
                t["danger"]  if v > 5.0 else
                t["accent"]  if v > 3.0 else
                t["success"]
                for v in df["Avg_Delay_Hours"]
            ]
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=df["Month_Year"],
                y=df["Avg_Delay_Hours"],
                marker_color=bar_colors,
                marker_opacity=0.85,
                hovertemplate="<b>%{x}</b><br>Delay: %{y:.1f} hrs<extra></extra>",
                showlegend=False,
            ))
            fig3.add_hline(
                y=3.0,
                line_dash="dot",
                line_color=t["text3"],
                line_width=1.2,
                annotation_text="Target 3 hrs",
                annotation_font_color=t["text3"],
                annotation_font_size=9,
                annotation_position="top right",
            )
            lo3 = base_layout(t, "Avg Fulfillment Delay by Month  ·  🟢 <3h  🟡 3-5h  🔴 >5h", 315)
            fig3.update_layout(**lo3)
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with r2c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig4 = go.Figure()
            for i, yr in enumerate(sorted(df["Year"].unique())):
                df_yr = df[df["Year"] == yr].sort_values("Month")
                clr   = YEAR_COLORS[i % len(YEAR_COLORS)]
                fig4.add_trace(go.Scatter(
                    x=df_yr["Month_Name"],
                    y=df_yr["Orders"],
                    name=str(yr),
                    mode="lines",
                    fill="tozeroy",
                    line=dict(width=2.5, color=clr),
                    fillcolor=hex_to_rgba(clr, 0.12),
                    hovertemplate=f"<b>{yr} %{{x}}</b><br>Orders: %{{y:,}}<extra></extra>",
                ))
            lo4 = base_layout(t, "Demand Area — Year-on-Year Overlay", 315)
            lo4["showlegend"] = True
            fig4.update_layout(**lo4)
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Row 3 ─ YoY grouped bar comparison
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        yr_agg = df.groupby("Year").agg(
            Orders=("Orders",          "sum"),
            Revenue=("Revenue",        "sum"),
            Delay=("Avg_Delay_Hours",  "mean"),
            Returns=("Returns",        "sum"),
        ).reset_index()

        metrics_cmp = [
            ("Orders",  "Total Orders",       t["accent"],  1),
            ("Revenue", "Total Revenue ($)",  t["accent2"], 2),
            ("Delay",   "Avg Delay (hrs)",    t["danger"],  3),
            ("Returns", "Total Returns",       t["text2"],  4),
        ]
        fig5 = make_subplots(
            rows=1, cols=4,
            subplot_titles=[m[1] for m in metrics_cmp],
            horizontal_spacing=0.055,
        )
        for (col_key, _, color, col_idx) in metrics_cmp:
            fig5.add_trace(
                go.Bar(
                    x=yr_agg["Year"].astype(str),
                    y=yr_agg[col_key],
                    marker_color=color,
                    marker_opacity=0.82,
                    showlegend=False,
                    hovertemplate=f"<b>%{{x}}</b><br>{col_key}: %{{y:,.1f}}<extra></extra>",
                ),
                row=1, col=col_idx,
            )
        lo5 = base_layout(t, "Year-over-Year Comparison", 285)
        lo5["showlegend"] = False
        lo5.pop("xaxis", None)
        lo5.pop("yaxis", None)
        fig5.update_layout(**lo5)
        for ci in range(1, 5):
            fig5.update_xaxes(
                gridcolor=t["grid"], tickfont=dict(color=t["text3"], size=10),
                row=1, col=ci,
            )
            fig5.update_yaxes(
                gridcolor=t["grid"], tickfont=dict(color=t["text3"], size=10),
                row=1, col=ci,
            )
        for ann in fig5.layout.annotations:
            ann.font.color  = t["text2"]
            ann.font.size   = 11
            ann.font.family = "DM Sans"
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        # Row 4 ─ Revenue per order · Return rate trend
        r4c1, r4c2 = st.columns(2)

        with r4c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig6 = go.Figure()
            fig6.add_trace(go.Scatter(
                x=df["Month_Year"],
                y=df["Rev_Per_Order"],
                mode="lines+markers",
                line=dict(color=t["accent"], width=2.5),
                marker=dict(size=6, color=t["accent"],
                            line=dict(color=t["card"], width=1.5)),
                fill="tozeroy",
                fillcolor=hex_to_rgba(t["accent"], 0.10),
                hovertemplate="<b>%{x}</b><br>Rev/Order: $%{y:.0f}<extra></extra>",
                name="Rev / Order",
            ))
            lo6 = base_layout(t, "Revenue per Order — Monthly", 310)
            fig6.update_layout(**lo6)
            fig6.update_yaxes(tickprefix="$")
            st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with r4c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig7 = go.Figure()
            fig7.add_trace(go.Scatter(
                x=df["Month_Year"],
                y=df["Return_Rate"],
                mode="lines+markers",
                line=dict(color=t["danger"], width=2.5),
                marker=dict(size=6, color=t["danger"],
                            line=dict(color=t["card"], width=1.5)),
                fill="tozeroy",
                fillcolor=hex_to_rgba(t["danger"], 0.10),
                hovertemplate="<b>%{x}</b><br>Return Rate: %{y:.1f}%<extra></extra>",
                name="Return Rate",
            ))
            fig7.add_hline(
                y=5.0,
                line_dash="dot",
                line_color=t["text3"],
                line_width=1.2,
                annotation_text="Benchmark 5%",
                annotation_font_color=t["text3"],
                annotation_font_size=9,
                annotation_position="top right",
            )
            lo7 = base_layout(t, "Return Rate % — Monthly Trend", 310)
            fig7.update_layout(**lo7)
            fig7.update_yaxes(ticksuffix="%")
            st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────
    # TAB 2 — SMART INSIGHTS
    # ────────────────────────────────────────────────────────────
    with tab_ins:
        ins_l, ins_r = st.columns([1, 3])
        with ins_l:
            gen_btn = st.button("🧠  Generate Insights", use_container_width=True)
            if gen_btn:
                st.session_state.show_insights = True

            if st.session_state.show_insights:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("↺  Reset", use_container_width=True, key="reset_ins"):
                    st.session_state.show_insights = False
                    st.rerun()

        if st.session_state.show_insights:
            with st.spinner("🔍  Analysing warehouse data…"):
                time.sleep(0.7)

            st.markdown(f"""
            <div style="margin-bottom:20px">
                <div class="section-label">AI Analysis · {datetime.now().strftime('%d %b %Y')}</div>
                <div class="section-title">Smart Insights Report</div>
            </div>
            """, unsafe_allow_html=True)

            insights = generate_insights(df)
            for ins in insights:
                st.markdown(f"""
                <div class="insight-block">
                    <div class="insight-block-title">{ins['icon']}  {ins['title']}</div>
                    <div class="insight-block-body">{ins['body']}</div>
                </div>
                """, unsafe_allow_html=True)

            # Summary table
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="section-label">Summary by Year</div>', unsafe_allow_html=True)

            smry = df.groupby("Year").agg(
                Total_Orders=("Orders",          "sum"),
                Total_Revenue=("Revenue",        "sum"),
                Avg_Delay=("Avg_Delay_Hours",    "mean"),
                Total_Returns=("Returns",        "sum"),
                Return_Rate=("Return_Rate",      "mean"),
            ).reset_index()
            smry["Total_Revenue"]  = smry["Total_Revenue"].apply(fmt_money)
            smry["Avg_Delay"]      = smry["Avg_Delay"].apply(lambda x: f"{x:.2f} hrs")
            smry["Return_Rate"]    = smry["Return_Rate"].apply(lambda x: f"{x:.1f}%")
            smry["Total_Orders"]   = smry["Total_Orders"].apply(lambda x: f"{x:,}")
            smry["Total_Returns"]  = smry["Total_Returns"].apply(lambda x: f"{x:,}")
            smry.columns = ["Year", "Total Orders", "Revenue", "Avg Delay", "Returns", "Return Rate"]
            st.dataframe(smry, use_container_width=True, hide_index=True)

            # Strategic recommendations
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="section-label">Strategic Recommendations</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:600;
                 color:{t['text']};margin-bottom:16px">Action Plan</div>
            """, unsafe_allow_html=True)

            recs = [
                ("🗓", "Demand Forecasting",
                 "Pre-stock peak-season SKUs 6–8 weeks in advance. Use seasonal indices to plan "
                 "labour rosters and carrier capacity. Maintain safety stock at 15% above rolling average."),
                ("⚡", "Delay Reduction",
                 "Implement automated pick-and-pack for top-selling SKUs. Set SLA alerts at 2.5 hrs "
                 "to catch issues before breaching the 3-hr target. Audit warehouse layout for bottlenecks."),
                ("↩️", "Return Rate Management",
                 "Conduct post-purchase surveys to capture return reasons. Invest in improved product "
                 "photography and accurate sizing guides. Target sub-4% return rate within 12 months."),
                ("💰", "Revenue Optimisation",
                 "Introduce bundle pricing and cross-sell at order confirmation. "
                 "Target a 5–8% uplift in average order value through personalisation "
                 "and loyalty programme incentives."),
                ("👥", "Workforce Planning",
                 "Align headcount with monthly order curves. Add flex workers for Nov–Jan surge. "
                 "Cross-train staff on multiple warehouse zones to reduce single-point-of-failure risk."),
            ]
            for icon, title, body in recs:
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-title">{icon} {title}</div>
                    <div class="rec-body">{body}</div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div style="text-align:center;padding:70px 0;color:{t['text3']}">
                <div style="font-size:52px;margin-bottom:18px;opacity:0.5">🧠</div>
                <div style="font-family:'Playfair Display',serif;font-size:22px;
                     color:{t['text2']};margin-bottom:10px">Smart Insights Engine</div>
                <div style="font-size:13px;max-width:420px;margin:auto;line-height:1.7">
                    Click <strong>Generate Insights</strong> to analyse your filtered data
                    and receive AI-powered business recommendations and strategic actions.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────
    # TAB 3 — AI ASSISTANT
    # ────────────────────────────────────────────────────────────
    with tab_ai:
        st.markdown(f"""
        <div style="margin-bottom:20px">
            <div class="section-label">Rule-Based Intelligence Engine</div>
            <div style="font-family:'Playfair Display',serif;font-size:22px;
                 font-weight:600;color:{t['text']}">WarehouseIQ Assistant</div>
            <div style="font-size:12px;color:{t['text3']};margin-top:3px">
                Ask about orders · revenue · delays · returns · trends
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Chat history display
        if not st.session_state.chat_history:
            st.markdown(f"""
            <div class="chat-bot">
                <div class="chat-label">WarehouseIQ</div>
                👋 Hello! I'm your Warehouse Intelligence Assistant.<br>
                I can analyse <strong>orders, revenue, delays, returns, and trends</strong>
                across your filtered dataset.<br><br>
                Type <code>help</code> to see everything I can do, or try one of the quick buttons below.
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="chat-user">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    body = msg["content"].replace("\n", "<br>")
                    st.markdown(
                        f'<div class="chat-bot"><div class="chat-label">WarehouseIQ</div>{body}</div>',
                        unsafe_allow_html=True,
                    )

        # Quick prompts
        st.markdown("<br>", unsafe_allow_html=True)
        quick_cols = st.columns(4)
        quick_prompts = [
            "📊  Full summary",
            "📦  Best month",
            "⏱  Delay trend",
            "📈  Year over year",
        ]
        for i, (col, prompt) in enumerate(zip(quick_cols, quick_prompts)):
            with col:
                if st.button(prompt, key=f"qp_{i}", use_container_width=True):
                    clean = prompt.split("  ", 1)[-1]
                    st.session_state.chat_history.append({"role": "user",      "content": clean})
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_respond(clean, df)})
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Input row
        inp_col, btn_col = st.columns([5, 1])
        with inp_col:
            user_input = st.text_input(
                "_",
                placeholder="Ask anything: 'revenue in 2025', 'average delay', 'return rate'…",
                label_visibility="collapsed",
                key="chat_input",
            )
        with btn_col:
            send = st.button("Send →", use_container_width=True, key="send_btn")

        if send and user_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
            with st.spinner(""):
                resp = ai_respond(user_input.strip(), df)
            st.session_state.chat_history.append({"role": "assistant", "content": resp})
            st.rerun()

        # Clear
        if st.session_state.chat_history:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑  Clear Chat History", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

    # ────────────────────────────────────────────────────────────
    # TAB 4 — RAW DATA
    # ────────────────────────────────────────────────────────────
    with tab_raw:
        st.markdown(f"""
        <div style="margin-bottom:20px">
            <div class="section-label">Filtered Dataset View</div>
            <div class="section-title">Raw Data Explorer</div>
        </div>
        """, unsafe_allow_html=True)

        display_df = df[[
            "Year", "Month_Name", "Orders", "Revenue",
            "Avg_Delay_Hours", "Returns", "Return_Rate", "Rev_Per_Order"
        ]].copy()
        display_df.columns = [
            "Year", "Month", "Orders", "Revenue ($)",
            "Avg Delay (hrs)", "Returns", "Return Rate (%)", "Rev / Order ($)"
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)

        # Descriptive stats
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Descriptive Statistics</div>', unsafe_allow_html=True)
        stats = df[["Orders", "Revenue", "Avg_Delay_Hours", "Returns", "Return_Rate"]].describe().round(2)
        stats.columns = ["Orders", "Revenue ($)", "Avg Delay (hrs)", "Returns", "Return Rate (%)"]
        st.dataframe(stats, use_container_width=True)

        # Month heatmap — orders
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Heatmap — Orders by Month & Year</div>', unsafe_allow_html=True)
        pivot = df.pivot_table(index="Month_Name", columns="Year", values="Orders", aggfunc="sum")
        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        pivot = pivot.reindex([m for m in month_order if m in pivot.index])

        fig_hm = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.astype(str).tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, t["card"]], [0.5, t["accent2"]], [1, t["accent_light"]]],
            hovertemplate="<b>%{y} %{x}</b><br>Orders: %{z:,}<extra></extra>",
            showscale=True,
            colorbar=dict(
                tickfont=dict(color=t["text3"]),
                outlinewidth=0, thickness=12,
            ),
        ))
        lo_hm = base_layout(t, "", 340)
        lo_hm["margin"] = dict(l=50, r=12, t=18, b=12)
        fig_hm.update_layout(**lo_hm)
        fig_hm.update_xaxes(side="top")
        st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})

    # ── FOOTER ───────────────────────────────────────────────────
    st.markdown("""
    <div class="footer">
        Built by <span class="accent">Tanay Shrivastava</span>
        &nbsp;·&nbsp; AI &nbsp;•&nbsp; Data &nbsp;•&nbsp; Supply Chain
        <div class="dim">WarehouseIQ Dashboard  v1.0  ·  Powered by Streamlit & Plotly</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

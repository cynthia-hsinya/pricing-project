import sys
import os
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from pricing_model import evaluate_price, find_optimal_price
from visualize import plot_price_vs_metric, plot_price_trend, plot_strategy_comparison
from competitor_analysis import (
    load_competitor_data,
    get_current_prices,
    build_comparison_table,
    detect_price_alerts,
)
from strategy_simulator import compare_strategies

st.set_page_config(page_title="Pricing Simulator", layout="wide")

st.title("Competitive Pricing Intelligence & Simulator")
st.caption("PowerUp 行動電源 — 定價策略模擬工具（Portfolio Project，非真實市場數據）")

# ---------- Input Panel (shared across tabs) ----------
with st.sidebar:
    st.header("Input Parameters")

    base_price = st.number_input("Base Price (目前售價)", min_value=1, value=690, step=10)
    base_demand = st.number_input("Base Demand (月銷量, 假設值)", min_value=1, value=1000, step=50)
    unit_cost = st.number_input("Unit Cost (單位成本)", min_value=1, value=400, step=10)
    elasticity = st.slider("Price Elasticity (需求價格彈性)", min_value=-4.0, max_value=-0.1,
                            value=-1.8, step=0.1,
                            help="數值越負，代表消費者對價格越敏感（商品越同質、替代品越多）")

    st.subheader("Price Range for Analysis")
    price_min = st.number_input("最低測試價格", min_value=1, value=400, step=10)
    price_max = st.number_input("最高測試價格", min_value=1, value=1500, step=10)

    st.divider()
    st.caption("⚠️ Demand 與 Elasticity 為假設值，用於展示分析方法，非真實預測。")

# ---------- Shared Calculations ----------
best, all_results = find_optimal_price(base_price, base_demand, elasticity, unit_cost,
                                        price_min, price_max, step=5)
current = evaluate_price(base_price, base_price, base_demand, elasticity, unit_cost)
results_df = pd.DataFrame(all_results)

competitor_csv_path = os.path.join(os.path.dirname(__file__), "data", "competitor_prices.csv")
competitor_data_available = os.path.exists(competitor_csv_path)
if competitor_data_available:
    competitor_df = load_competitor_data(competitor_csv_path)
    current_prices = get_current_prices(competitor_df)

# ---------- Tabs ----------
tab_pricing, tab_monitoring, tab_strategy = st.tabs([
    "📊 Pricing Model", "🔍 Competitor Monitoring", "⚔️ Strategy Simulator"
])

# ============================================================
# TAB 1 — Pricing Model
# ============================================================
with tab_pricing:
    st.subheader("Current Price vs Recommended Price")
    st.caption(
        "「Current」是你在左側設定的 Base Price 本身的表現；「Recommended」是模型在你設定的 "
        "Price Range 內，找到的利潤最大化價格。兩者用同一組 demand/elasticity/cost 假設計算，"
        "差異只來自「選哪個價格」。此頁的 demand model 僅反映我們自身的 own-price elasticity，"
        "未納入競品價格（見「Strategy Simulator」分頁）。"
    )

    col_current, col_recommended = st.columns(2)

    with col_current:
        st.markdown("##### 📍 Current Price（你目前的設定）")
        st.metric("Price", f"${current['price']:.0f}")
        st.metric("Demand", f"{current['demand']:.0f} units")
        st.metric("Revenue", f"${current['revenue']:,.0f}")
        st.metric("Profit", f"${current['profit']:,.0f}")
        st.metric("Margin", f"{current['margin']:.1%}")

    with col_recommended:
        st.markdown("##### ⭐ Recommended Price（模型建議）")
        profit_delta = best['profit'] - current['profit']
        st.metric("Price", f"${best['price']:.0f}")
        st.metric("Demand", f"{best['demand']:.0f} units")
        st.metric("Revenue", f"${best['revenue']:,.0f}")
        st.metric("Profit", f"${best['profit']:,.0f}", delta=f"{profit_delta:,.0f} vs current")
        st.metric("Margin", f"{best['margin']:.1%}")

    st.info(
        f"若採用模型建議價格（${best['price']:.0f}）而非目前設定的 Base Price（${base_price:.0f}），"
        f"在目前假設下，估計利潤變化為 {'+' if profit_delta >= 0 else ''}{profit_delta:,.0f} 元。"
        f"此為 model-based estimate，非保證結果。"
    )

    st.divider()
    st.subheader("Price Sensitivity Analysis")

    tab_profit, tab_demand, tab_revenue = st.tabs(["📈 Profit", "📊 Demand", "💰 Revenue"])

    with tab_profit:
        fig_profit = plot_price_vs_metric(results_df, "profit", best["price"], "")
        st.plotly_chart(fig_profit, width='stretch')
        st.caption("紅色虛線標示 Recommended Price。曲線高峰即為利潤最大化的價格點。")

    with tab_demand:
        fig_demand = plot_price_vs_metric(results_df, "demand", best["price"], "")
        st.plotly_chart(fig_demand, width='stretch')
        st.caption("需求隨價格上升而下降，下降速度由 Elasticity 決定。")

    with tab_revenue:
        fig_revenue = plot_price_vs_metric(results_df, "revenue", best["price"], "")
        st.plotly_chart(fig_revenue, width='stretch')
        st.caption(
            "當 |Elasticity| > 1（elastic demand）時，Revenue 會隨價格上升單調遞減——"
            "這也是為什麼 Recommended Price 不等於 Revenue-maximizing Price。"
        )

# ============================================================
# TAB 2 — Competitor Monitoring
# ============================================================
with tab_monitoring:
    st.subheader("Competitor Price Monitoring")

    if competitor_data_available:
        comparison_table = build_comparison_table(current_prices, base_price)

        st.markdown("##### Current Market Price")
        st.dataframe(
            comparison_table.style.format({
                "Our Price": "${:.0f}",
                "Competitor Price": "${:.0f}",
                "Price Diff": "{:+.0f}",
                "Price Diff %": "{:+.1f}%",
            }),
            width='stretch',
            hide_index=True,
        )
        st.caption("Price Diff % 為正代表我們比該競品貴，負代表我們比較便宜。")

        st.markdown("##### ⚠️ Price Alerts（過去 7 天變動 ≥ 5%）")
        alerts = detect_price_alerts(competitor_df, lookback_days=7, threshold=0.05)

        if alerts.empty:
            st.success("目前沒有競品出現顯著價格變動。")
        else:
            for _, row in alerts.iterrows():
                direction = "⬇️ 降價" if row["Change %"] < 0 else "⬆️ 漲價"
                st.warning(
                    f"**{row['Competitor']}** {direction} {abs(row['Change %']):.1f}%"
                    f"（從 ${row['Price (7 days ago)']:.0f} 變為 ${row['Latest Price']:.0f}）"
                )

        st.markdown("##### Historical Price Trend")
        fig_trend = plot_price_trend(competitor_df, base_price, "")
        st.plotly_chart(fig_trend, width='stretch')
        st.caption(
            "觀察各競品的價格波動模式——例如是否有規律性的促銷檔期，"
            "有助於提前預判競品行為，而不只是被動應對已發生的變化。"
        )
    else:
        st.info("尚未找到競品價格資料檔案（data/competitor_prices.csv）。")

# ============================================================
# TAB 3 — Strategy Simulator
# ============================================================
with tab_strategy:
    st.subheader("Pricing Strategy Simulator")
    st.caption(
        "假設某個競品突然大幅降價，我們應該如何反應？比較「維持價格」「跟進降價」"
        "「部分降價」三種策略。這一頁的 demand model 額外加入了 cross-price elasticity，"
        "讓競品的價格變化真的會影響我們的需求估計（不同於 Pricing Model 分頁的 own-price only 模型）。"
    )

    if competitor_data_available:
        competitor_names = current_prices["Competitor"].tolist()
        selected_competitor = st.selectbox("假設哪個競品突然降價？", competitor_names)
        competitor_current = current_prices.loc[
            current_prices["Competitor"] == selected_competitor, "Price"
        ].values[0]

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(f"{selected_competitor} 目前價格", f"${competitor_current:.0f}")
        with col_b:
            competitor_new_price = st.number_input(
                f"{selected_competitor} 突然降到多少？", min_value=1,
                value=int(competitor_current * 0.85), step=10,
            )

        partial_cut_price = st.slider(
            "部分降價（Partial Cut）要降到多少？",
            min_value=int(competitor_new_price), max_value=int(base_price),
            value=int((competitor_new_price + base_price) / 2),
        )

        cross_elasticity = st.slider(
            "Cross-Price Elasticity（我們與競品的替代敏感度）",
            min_value=0.1, max_value=3.0, value=1.0, step=0.1,
            help="數值越大，代表競品降價時，我們流失的顧客越多（替代性越高）。"
                 "行動電源規格接近同質，設定中等偏高（約 1.0）是合理假設；"
                 "數值需為正——正值代表『競品降價 → 我們的需求被搶走』這個方向。"
        )

        strategies = {
            "Maintain Price": base_price,
            f"Match {selected_competitor} ({competitor_new_price})": competitor_new_price,
            f"Partial Cut ({partial_cut_price})": partial_cut_price,
        }

        strategy_df = compare_strategies(
            strategies=strategies,
            competitor_price=competitor_new_price,
            base_price=base_price,
            base_demand=base_demand,
            elasticity=elasticity,
            competitor_base_price=competitor_current,
            cross_elasticity=cross_elasticity,
            unit_cost=unit_cost,
        )

        st.markdown("##### Strategy Comparison")
        st.dataframe(
            strategy_df.style.format({
                "price": "${:.0f}", "demand": "{:.0f}", "revenue": "${:,.0f}",
                "total_cost": "${:,.0f}", "profit": "${:,.0f}", "margin": "{:.1%}",
            }),
            width='stretch', hide_index=True,
        )

        fig_strategy = plot_strategy_comparison(strategy_df, "")
        st.plotly_chart(fig_strategy, width='stretch')

        recommended = strategy_df.loc[strategy_df["is_recommended"], "strategy"].values[0]
        st.success(
            f"**Recommended Strategy: {recommended}**　"
            f"此建議根據目前設定的 demand model、own-price/cross-price elasticity、"
            f"cost assumptions 計算而來，是 model-based recommendation，非保證結果。"
        )
    else:
        st.info("尚未找到競品價格資料檔案（data/competitor_prices.csv）。")

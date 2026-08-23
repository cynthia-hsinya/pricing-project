import pandas as pd
import plotly.express as px
from pricing_model import find_optimal_price


def build_results_df(base_price, base_demand, elasticity, unit_cost,
                      price_min, price_max, step=5):
    """把 grid search 的結果整理成 DataFrame，方便畫圖跟之後接 Streamlit。"""
    best, all_results = find_optimal_price(base_price, base_demand, elasticity,
                                            unit_cost, price_min, price_max, step)
    df = pd.DataFrame(all_results)
    return df, best


def plot_price_vs_metric(df: pd.DataFrame, metric: str, best_price: float, title: str):
    """
    畫出 Price vs 某個財務指標的折線圖，並在最佳價格處標一條垂直線。
    metric 可以是 'demand' / 'revenue' / 'profit'
    """
    fig = px.line(df, x="price", y=metric, title=title)
    fig.add_vline(x=best_price, line_dash="dash", line_color="red",
                   annotation_text=f"Optimal Price = {best_price}")
    return fig


def plot_price_trend(competitor_df: pd.DataFrame, our_price: float, title: str = ""):
    """
    畫出各競品價格隨時間變化的趨勢圖，並用水平虛線標示我們自己的價格作為對照。
    competitor_df 需包含 Date / Competitor / Price 欄位（長格式，一列一筆觀察值）。
    """
    fig = px.line(competitor_df, x="Date", y="Price", color="Competitor", title=title)
    fig.add_hline(y=our_price, line_dash="dash", line_color="black",
                   annotation_text=f"Our Price = {our_price}")
    return fig


def plot_strategy_comparison(strategy_df: pd.DataFrame, title: str = ""):
    """
    畫出各定價策略的利潤比較長條圖，用顏色標示出 Recommended Strategy。
    strategy_df 需包含 strategy / profit / is_recommended 欄位。
    """
    colors = strategy_df["is_recommended"].map({True: "#2ecc71", False: "#95a5a6"})
    fig = px.bar(strategy_df, x="strategy", y="profit", title=title,
                 text=strategy_df["profit"].apply(lambda p: f"${p:,.0f}"))
    fig.update_traces(marker_color=colors, textposition="outside")
    fig.update_layout(xaxis_title="", yaxis_title="Profit")
    return fig


if __name__ == "__main__":
    P0, Q0, elasticity, unit_cost = 690, 1000, -1.8, 400

    df, best = build_results_df(P0, Q0, elasticity, unit_cost,
                                 price_min=400, price_max=1500, step=5)

    fig_demand = plot_price_vs_metric(df, "demand", best["price"], "Price vs Demand")
    fig_revenue = plot_price_vs_metric(df, "revenue", best["price"], "Price vs Revenue")
    fig_profit = plot_price_vs_metric(df, "profit", best["price"], "Price vs Profit")

    print(f"最佳價格：{best['price']}（利潤 = {best['profit']:.0f}）")
    # 在 Jupyter Notebook 裡執行時，取消下面註解就能直接互動顯示：
    # fig_demand.show()
    # fig_revenue.show()
    # fig_profit.show()

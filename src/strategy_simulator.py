import pandas as pd
from demand_model import estimate_demand_competitive


def evaluate_price_competitive(price: float, competitor_price: float, base_price: float,
                                base_demand: float, elasticity: float,
                                competitor_base_price: float, cross_elasticity: float,
                                unit_cost: float) -> dict:
    """跟 evaluate_price() 邏輯一樣，但需求估計改用會反映競品價格的線性模型。"""
    demand = estimate_demand_competitive(price, competitor_price, base_price, base_demand,
                                          elasticity, competitor_base_price, cross_elasticity)
    revenue = price * demand
    total_cost = unit_cost * demand
    profit = revenue - total_cost
    margin = profit / revenue if revenue > 0 else 0
    return {
        "price": price, "demand": demand, "revenue": revenue,
        "total_cost": total_cost, "profit": profit, "margin": margin,
    }


def compare_strategies(strategies: dict, competitor_price: float, base_price: float,
                        base_demand: float, elasticity: float, competitor_base_price: float,
                        cross_elasticity: float, unit_cost: float) -> pd.DataFrame:
    """
    比較多種定價策略的財務結果，同一情境下所有策略共用同一個「競品新價格」。

    strategies: dict，例如 {"Maintain": 690, "Match Competitor": 400, "Partial Cut": 550}
    competitor_price: 競品「突然變動後」的新價格（情境輸入，所有策略共用）
    competitor_base_price: 競品原本（變動前）的價格，作為需求模型的校準錨點
    """
    rows = []
    for strategy_name, price in strategies.items():
        result = evaluate_price_competitive(price, competitor_price, base_price, base_demand,
                                             elasticity, competitor_base_price,
                                             cross_elasticity, unit_cost)
        result["strategy"] = strategy_name
        rows.append(result)

    df = pd.DataFrame(rows)
    df = df[["strategy", "price", "demand", "revenue", "total_cost", "profit", "margin"]]

    best_idx = df["profit"].idxmax()
    df["is_recommended"] = False
    df.loc[best_idx, "is_recommended"] = True

    return df


if __name__ == "__main__":
    # 沿用我們專案的 base assumptions
    P0, Q0, elasticity, unit_cost = 690, 1000, -1.8, 400
    cross_elasticity = 1.0  # 假設：行動電源接近完全替代品，交叉彈性設中等偏高

    competitor_base_price = 802  # Anker 原本的價格

    print("=== 情境比較：Anker 從 802 降到不同程度，看策略排名怎麼變 ===\n")
    for competitor_new_price in [600, 500, 400, 300]:
        strategies = {
            "Maintain (690)": 690,
            "Match (%d)" % competitor_new_price: competitor_new_price,
            "Partial Cut (600)": 600,
        }
        result_df = compare_strategies(strategies, competitor_new_price, P0, Q0, elasticity,
                                        competitor_base_price, cross_elasticity, unit_cost)
        recommended = result_df.loc[result_df["is_recommended"], "strategy"].values[0]
        print(f"Anker 降到 {competitor_new_price}: Recommended = {recommended}")
        print(result_df[["strategy", "price", "demand", "profit"]].round(1).to_string(index=False))
        print()

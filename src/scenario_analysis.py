import pandas as pd
from pricing_model import find_optimal_price
from strategy_simulator import compare_strategies


def run_cost_elasticity_scenarios(base_price: float, base_demand: float,
                                   elasticity: float, unit_cost: float,
                                   price_min: float, price_max: float) -> pd.DataFrame:
    """
    比較「基準情境」與「成本上升 10%」「彈性更敏感」情境下，
    Optimal Price / Profit 的變化。

    這裡回答的問題是：市場條件變化時，我們自己的最佳定價會怎麼調整？
    """
    scenarios = {
        "Baseline": {"elasticity": elasticity, "unit_cost": unit_cost},
        "Unit Cost +10%": {"elasticity": elasticity, "unit_cost": unit_cost * 1.10},
        "Elasticity More Sensitive (x1.3)": {"elasticity": elasticity * 1.3, "unit_cost": unit_cost},
    }

    rows = []
    for name, params in scenarios.items():
        best, _ = find_optimal_price(base_price, base_demand, params["elasticity"],
                                      params["unit_cost"], price_min, price_max, step=5)
        rows.append({
            "scenario": name,
            "elasticity": params["elasticity"],
            "unit_cost": params["unit_cost"],
            "optimal_price": best["price"],
            "expected_profit": best["profit"],
            "profit_margin": best["margin"],
        })

    df = pd.DataFrame(rows)
    baseline_price = df.loc[df["scenario"] == "Baseline", "optimal_price"].values[0]
    df["price_change_vs_baseline"] = df["optimal_price"] - baseline_price
    return df


def run_competitor_price_scenarios(competitor_base_price: float, our_price: float,
                                    base_demand: float, elasticity: float, unit_cost: float,
                                    cross_elasticity: float) -> pd.DataFrame:
    """
    情境 1、2：競品價格分別下降 5% / 10%，看「Maintain / Match / Partial Cut」
    三種策略中，哪一個是 model-recommended，以及利潤差距有多大。

    這裡改用 Strategy Simulator 的競爭型需求模型（會反映競品價格），
    而不是 Phase 1 的 optimizer——因為只有競爭型模型才能表現出策略排名
    會隨競品降價幅度改變的動態。
    """
    rows = []
    for pct in [0.05, 0.10]:
        competitor_new_price = competitor_base_price * (1 - pct)
        partial_cut_price = (our_price + competitor_new_price) / 2

        strategies = {
            "Maintain": our_price,
            "Match": competitor_new_price,
            "Partial Cut": partial_cut_price,
        }

        result_df = compare_strategies(
            strategies=strategies,
            competitor_price=competitor_new_price,
            base_price=our_price,
            base_demand=base_demand,
            elasticity=elasticity,
            competitor_base_price=competitor_base_price,
            cross_elasticity=cross_elasticity,
            unit_cost=unit_cost,
        )

        recommended = result_df.loc[result_df["is_recommended"], "strategy"].values[0]
        recommended_profit = result_df.loc[result_df["is_recommended"], "profit"].values[0]
        maintain_profit = result_df.loc[result_df["strategy"] == "Maintain", "profit"].values[0]

        rows.append({
            "scenario": f"Competitor Price -{int(pct*100)}%",
            "competitor_new_price": round(competitor_new_price, 1),
            "recommended_strategy": recommended,
            "recommended_profit": recommended_profit,
            "maintain_profit": maintain_profit,
            "profit_gain_vs_maintain": recommended_profit - maintain_profit,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    P0, Q0, elasticity, unit_cost = 690, 1000, -1.8, 400

    print("=== Scenario 3, 4: Cost / Elasticity Sensitivity ===")
    df1 = run_cost_elasticity_scenarios(P0, Q0, elasticity, unit_cost,
                                         price_min=400, price_max=1500)
    print(df1.round(2).to_string(index=False))

    print("\n=== Scenario 1, 2: Competitor Price Decrease (Anker as example) ===")
    competitor_base_price = 802  # Anker 目前價格
    cross_elasticity = 1.0
    df2 = run_competitor_price_scenarios(competitor_base_price, P0, Q0, elasticity,
                                          unit_cost, cross_elasticity)
    print(df2.round(1).to_string(index=False))

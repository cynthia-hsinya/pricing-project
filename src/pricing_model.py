from demand_model import estimate_demand


def evaluate_price(price: float, base_price: float, base_demand: float,
                    elasticity: float, unit_cost: float) -> dict:
    """
    給定一個價格，計算對應的 demand / revenue / cost / profit / margin。
    回傳 dict，方便之後接 DataFrame 或畫圖。
    """
    demand = estimate_demand(price, base_price, base_demand, elasticity)
    revenue = price * demand
    total_cost = unit_cost * demand
    profit = revenue - total_cost
    margin = profit / revenue if revenue > 0 else 0

    return {
        "price": price,
        "demand": demand,
        "revenue": revenue,
        "total_cost": total_cost,
        "profit": profit,
        "margin": margin,
    }


if __name__ == "__main__":
    P0 = 690
    Q0 = 1000
    elasticity = -1.8
    unit_cost = 400

    test_prices = [500, 600, 690, 750, 850]

    print(f"{'Price':>6} | {'Demand':>8} | {'Revenue':>10} | {'Cost':>10} | {'Profit':>10} | {'Margin':>7}")
    print("-" * 65)
    for p in test_prices:
        r = evaluate_price(p, P0, Q0, elasticity, unit_cost)
        print(f"{r['price']:>6} | {r['demand']:>8.1f} | {r['revenue']:>10.0f} | "
              f"{r['total_cost']:>10.0f} | {r['profit']:>10.0f} | {r['margin']:>6.1%}")


def find_optimal_price(base_price: float, base_demand: float, elasticity: float,
                        unit_cost: float, price_min: float, price_max: float,
                        step: float = 5) -> dict:
    """
    在 [price_min, price_max] 區間內，以 step 為間隔，找出利潤最高的價格。
    """
    results = []
    price = price_min
    while price <= price_max:
        results.append(evaluate_price(price, base_price, base_demand, elasticity, unit_cost))
        price += step

    best = max(results, key=lambda r: r["profit"])
    return best, results


if __name__ == "__main__":
    P0 = 690
    Q0 = 1000
    elasticity = -1.8
    unit_cost = 400

    # 理論公式解（Lerner markup rule），拿來驗證
    theoretical_price = unit_cost * (elasticity / (elasticity + 1))
    print(f"理論最佳價格（公式解）：{theoretical_price:.1f}")

    # Grid search
    best, all_results = find_optimal_price(P0, Q0, elasticity, unit_cost,
                                            price_min=400, price_max=1500, step=5)
    print(f"Grid Search 找到的最佳價格：{best['price']}")
    print(f"  → 需求 = {best['demand']:.1f}, 營收 = {best['revenue']:.0f}, "
          f"利潤 = {best['profit']:.0f}, 利潤率 = {best['margin']:.1%}")

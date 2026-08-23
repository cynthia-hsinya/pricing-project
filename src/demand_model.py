def estimate_demand(price: float, base_price: float, base_demand: float, elasticity: float) -> float:
    """
    Constant elasticity demand model.

    Q(P) = Q0 * (P / P0) ^ elasticity

    price        : 我們想測試的新價格 (P)
    base_price   : 目前的基準價格 (P0)
    base_demand  : 基準價格下的需求量 (Q0)
    elasticity   : 需求價格彈性 (通常是負數，商品越同質、替代品越多，數值越負)
    """
    return base_demand * (price / base_price) ** elasticity


def estimate_demand_competitive(own_price: float, competitor_price: float, base_price: float,
                                 base_demand: float, elasticity: float,
                                 competitor_base_price: float, cross_elasticity: float) -> float:
    """
    線性（Bertrand-style）需求模型，同時反映「我們自己的價格」與「競品價格」對需求的影響：

    Q = Q0 + slope_own * (P_own - P0) + slope_cross * (P_comp - P_comp0)

    slope_own（由 elasticity 換算，會是負值）：我們自己漲價，需求怎麼掉。
    slope_cross（由 cross_elasticity 換算，會是正值）：競品漲價，我們的需求怎麼漲
                （反過來，競品降價，我們的需求會被搶走）。

    這裡改用「線性可加」而不是原本的「乘法可分離」結構，是有數學原因的：
    純乘法模型（Q = Q0 * (P/P0)^e * (Pcomp/Pcomp0)^e_cross）不管 e_cross 怎麼設，
    競品價格項對所有候選價格來說都是同一個常數倍率，不會改變「哪個價格利潤最高」的排名。
    只有線性可加的結構，才能讓「最佳價格」真正隨競品價格移動——這正是我們需要的效果。

    own_price               : 我們想測試的價格
    competitor_price        : 情境中競品的新價格
    base_price / base_demand: 我們自己的需求曲線錨點（沿用 Phase 1 的假設）
    competitor_base_price   : 競品原本（變動前）的價格，作為基準參考點
    cross_elasticity        : 正數，競品降價 1%，我們需求大約減少 cross_elasticity%
    """
    slope_own = elasticity * base_demand / base_price
    slope_cross = cross_elasticity * base_demand / competitor_base_price

    q = (base_demand
         + slope_own * (own_price - base_price)
         + slope_cross * (competitor_price - competitor_base_price))

    return max(q, 0)  # 需求不能是負數


if __name__ == "__main__":
    P0 = 690
    Q0 = 1000
    elasticity = -1.8

    test_prices = [500, 600, 690, 750, 850]
    print(f"{'Price':>8} | {'Estimated Demand':>18}")
    print("-" * 30)
    for p in test_prices:
        q = estimate_demand(p, P0, Q0, elasticity)
        print(f"{p:>8} | {q:>18.1f}")

import pandas as pd


def load_competitor_data(csv_path: str) -> pd.DataFrame:
    """讀取競品價格歷史資料，並確保 Date 欄位是日期型別（方便之後排序、篩選）。"""
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def get_current_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    針對每個競品，取出「最新一筆」價格資料。
    做法：先依 Date 排序，再用 groupby + tail(1) 取每個競品的最後一筆。
    """
    df_sorted = df.sort_values("Date")
    latest = df_sorted.groupby("Competitor").tail(1).reset_index(drop=True)
    return latest[["Competitor", "Price", "Date", "URL"]]


def build_comparison_table(current_prices: pd.DataFrame, our_price: float) -> pd.DataFrame:
    """
    把「我們的價格」跟每個競品的最新價格做比較，計算價差與價差百分比。
    價差 = 我們的價格 - 競品價格（正數代表我們比較貴）
    """
    table = current_prices.copy()
    table["Our Price"] = our_price
    table["Price Diff"] = table["Our Price"] - table["Price"]
    table["Price Diff %"] = (table["Price Diff"] / table["Price"]) * 100
    table = table.rename(columns={"Price": "Competitor Price"})
    return table[["Competitor", "Our Price", "Competitor Price", "Price Diff", "Price Diff %"]]


def detect_price_alerts(df: pd.DataFrame, lookback_days: int = 7, threshold: float = 0.05) -> pd.DataFrame:
    """
    偵測每個競品「最近一筆價格」相較於「lookback_days 天前價格」的變動幅度，
    若絕對變動幅度超過 threshold（預設 5%），視為需要警示的事件。

    這是 Phase 4 規格要求的「簡單 threshold」版本，不做複雜的 anomaly detection。
    """
    alerts = []
    for competitor, group in df.groupby("Competitor"):
        group = group.sort_values("Date")
        if len(group) <= lookback_days:
            continue  # 資料不夠長，跳過

        latest_price = group.iloc[-1]["Price"]
        latest_date = group.iloc[-1]["Date"]
        past_price = group.iloc[-1 - lookback_days]["Price"]

        pct_change = (latest_price - past_price) / past_price

        if abs(pct_change) >= threshold:
            alerts.append({
                "Competitor": competitor,
                "Latest Price": latest_price,
                "Price (%d days ago)" % lookback_days: past_price,
                "Change %": pct_change * 100,
                "Date": latest_date,
            })

    return pd.DataFrame(alerts)


if __name__ == "__main__":
    df = load_competitor_data("../data/competitor_prices.csv")
    current = get_current_prices(df)
    print("=== 各競品最新價格 ===")
    print(current.to_string(index=False))

    our_price = 690
    comparison = build_comparison_table(current, our_price)
    print(f"\n=== 比價表（我們的價格 = {our_price}） ===")
    print(comparison.round(1).to_string(index=False))

    print("\n=== Price Alerts（過去 7 天變動 > 5%） ===")
    alerts = detect_price_alerts(df, lookback_days=7, threshold=0.05)
    if alerts.empty:
        print("目前沒有觸發警示的競品。")
    else:
        print(alerts.round(1).to_string(index=False))

import pandas as pd
import numpy as np

np.random.seed(42)  # 固定亂數種子，確保每次產生的資料一致，方便你之後重現/除錯

PRODUCT = "10000mAh USB-C Fast Charging Power Bank"

# 每個競品的基準價格與網址（模擬用）
competitors = {
    "Anker":    {"base_price": 790, "url": "https://example-store.com/anker-10000mah"},
    "Xiaomi":   {"base_price": 490, "url": "https://example-store.com/xiaomi-10000mah"},
    "ROMOSS":   {"base_price": 450, "url": "https://example-store.com/romoss-10000mah"},
    "PhoneMax": {"base_price": 590, "url": "https://example-store.com/phonemax-10000mah"},
}

# 觀察區間：過去 60 天，每天一筆
dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=60, freq="D")

# 設定幾次「促銷檔期」：某競品在某幾天大幅降價後回升，模擬真實促銷行為
# 格式：(競品, 開始天數 index, 持續天數, 降價幅度)
promotions = [
    ("Anker", 15, 4, 0.12),      # Anker 在第 15~18 天降價 12%
    ("Xiaomi", 30, 3, 0.08),     # Xiaomi 在第 30~32 天降價 8%
    ("ROMOSS", 45, 5, 0.15),     # ROMOSS 在第 45~49 天降價 15%（力度較大，符合低價品牌打法）
]

rows = []
for comp, info in competitors.items():
    price = info["base_price"]
    for i, date in enumerate(dates):
        # 平常小幅隨機波動（模擬正常市場雜訊，+-1.5%）
        noise = np.random.normal(0, 0.015)
        daily_price = price * (1 + noise)

        # 檢查是否在促銷區間內
        for promo_comp, start, duration, discount in promotions:
            if comp == promo_comp and start <= i < start + duration:
                daily_price = price * (1 - discount)

        rows.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Product": PRODUCT,
            "Competitor": comp,
            "Price": round(daily_price),
            "URL": info["url"],
        })

df = pd.DataFrame(rows)
df.to_csv("data/competitor_prices.csv", index=False)

print(f"共產生 {len(df)} 筆資料")
print(df.head(10))
print("...")
print(df[df["Competitor"] == "ROMOSS"].iloc[43:50])  # 檢查促銷區間有沒有正確反映降價

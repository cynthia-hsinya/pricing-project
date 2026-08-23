# Competitive Pricing Intelligence & Simulator（競品價格情報與定價策略模擬工具）

一個把競品價格變動轉化為定價建議的決策支援工具。

**[English](./README.md) | [中文](./README.zh-TW.md)**

> **作品集聲明**
> 本專案為求職作品集，非真實商業定價系統。所有需求資料、彈性假設、競品價格均為模擬或假設值，用於展示分析方法論，並非真實市場預測。

---

## 1. 商業問題

假設我是一家電商公司的 Business Analyst，公司的行動電源產品面對多個競爭對手。公司真正想知道的不是「競爭對手現在賣多少錢」，而是「競爭對手改變價格之後，我們應該怎麼定價，才能讓利潤最大化？」

**核心敘事**

```
Competitor Monitoring   → 告訴我們市場發生什麼事
Demand / Elasticity     → 告訴我們價格改變可能造成什麼影響
Pricing Simulator       → 告訴我們不同策略的可能結果
Recommendation          → 幫助決策者做決策
```

---

## 2. 專案目標

建立一個 Collect → Monitor → Analyze → Simulate → Recommend 的完整流程，用經濟學的需求彈性理論，把「競品價格情報」轉化為「可執行的定價決策建議」。

---

## 3. 資料

| 項目 | 說明 |
|---|---|
| 產品 | 10000mAh USB-C 快充行動電源（規格標準化、易比價的品類）|
| 我們的公司 | PowerUp（虛構電商賣家）|
| 競品 | Anker（高價品牌）、Xiaomi、ROMOSS、PhoneMax（中低價品牌）|
| 競品價格資料 | `data/competitor_prices.csv`，60 天模擬歷史資料，內建 3 次模擬促銷事件，用於驗證 Price Alert 機制 |

競品資料為程式模擬產生（見 `scripts/generate_competitor_data.py`），非真實爬蟲結果。專案刻意採用「先驗證方法論、資料源可替換」的設計，著重於「由價格情報到商業決策」的分析框架，而非爬蟲能力。

---

## 4. 方法論

專案採用**兩階段需求模型**，這是整個專案最重要的方法論演進。

### 第一階段 — Constant Elasticity Model（Notebook 1）

```
Q(P) = Q0 × (P / P0)^elasticity
```

用於「我們自己」的最適定價分析，不考慮競爭。這是一個乘法可分離（multiplicatively separable）的模型。

### 第二階段 — 線性（Bertrand-style）競爭模型（Notebook 2）

在開發 Strategy Simulator 時，我們發現第一階段模型有一個**結構性限制**：不論怎麼加入競品價格的乘法項，最佳自身價格數學上都會獨立於競品價格——也就是說，這種模型**天生無法表現「價格戰」**。

解法是改用線性可加模型：

```
Q(P, P_comp) = Q0 + slope_own × (P - P0) + slope_cross × (P_comp - P_comp0)
```

這讓「最佳定價策略」能真正隨競品價格移動，完整推導過程記錄在 `notebooks/02_competitive_strategy_analysis.ipynb`。

---

## 5. 定價模型

| 參數 | 數值 | 說明 |
|---|---|---|
| Base Price | 690 | 假設售價 |
| Base Demand | 1000 units/月 | 假設值 |
| Unit Cost | 400 | 依 10000mAh 行動電源代工出廠價（US$5.44–9.00）加計關稅/認證/物流估算，屬合理範圍 |
| Elasticity | -1.8 | 依產業文獻，標準化程度高、替代品多的消費性電子產品彈性常見 >1.3~2.0，此假設落在合理範圍 |
| Cross-Price Elasticity | 依競品調整，預設 1.0 | 不同品牌與我們的替代性不同（品牌忠誠度、定位重疊度），需依個案判斷 |

利潤最大化價格透過 Grid Search 與 Lerner Markup Rule（`P* = Unit Cost × elasticity/(elasticity+1)`）雙重驗證。

---

## 6. 競品監測

- **Current Market Price**：即時比價表，含 Price Diff / Price Diff %
- **Price Alert**：簡單 threshold 機制（預設過去 7 天變動 ≥ 5% 觸發警示），非複雜異常偵測
- **Historical Price Trend**：多競品價格走勢圖，用於觀察促銷模式

---

## 7. 互動儀表板

Streamlit App（`app.py`）分為三個分頁：

| Tab | 內容 |
|---|---|
| 📊 Pricing Model | Input Panel、Current vs Recommended Price 對照、Demand/Revenue/Profit 敏感度圖表 |
| 🔍 Competitor Monitoring | 比價表、Price Alert、Historical Trend |
| ⚔️ Strategy Simulator | 競品降價情境模擬、Maintain/Match/Partial Cut 三種策略比較（含 Cross-Price Elasticity 調整）|

### 如何執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 8. 商業洞察

1. **利潤最大化 ≠ 營收最大化**：在 elastic demand（|elasticity|>1）情境下，Revenue 隨價格單調遞減，但 Profit 有明確高峰，兩者不是同一個價格點。
2. **別人賣得動的價格，我們不一定賺得到錢**：競品可能有不同的成本結構（規模、供應鏈整合），直接「跟進降價到競品價格」可能讓我們的利潤趨近於零，甚至虧損。
3. **面對競品降價，是否反應取決於降價幅度是否逼近我們的成本線**：溫和降價時「維持原價」通常是最佳解；只有當競品價格大幅逼近我們的成本結構時，跟進或部分降價才會變得划算。
4. **成本上升 vs 市場競爭加劇，因應方式不同**：成本上升可透過調高價格轉嫁、維持利潤率不變；但市場競爭加劇（彈性變敏感）會直接壓縮可能的最大利潤率，無法單純轉嫁。

---

## 9. 限制

- Demand、elasticity、cross-price elasticity 均為假設值，非真實銷售或市場調查資料估計而來。
- 競品價格資料為模擬產生，非真實爬蟲結果。
- Cross-price elasticity 目前需依競品品牌手動調整，未做到系統化、可儲存的品牌別校準。
- Price Alert 採用單點比較（最新 vs N 天前），對事件邊界的偵測時機敏感，非嚴謹的異常偵測方法。
- 模型未納入季節性、庫存、平台演算法排序、廣告等其他影響銷量的因素。
- 所有 Recommended Price / Strategy 皆為 model-based estimate，非保證結果。

---

## 10. 未來優化方向

- 若能取得真實銷售與競品價格歷史資料，改用迴歸方法估計真實彈性，取代假設值。
- 將 cross-price elasticity 依品牌分別設定並持久化儲存。
- 接入真實爬蟲（`requests` / `BeautifulSoup` / `Playwright`），並尊重 robots.txt 與網站使用條款。
- 導入更嚴謹的異常偵測方法（例如移動平均、標準差門檻）取代單點比較。
- 系統化涵蓋所有競品的 Scenario Analysis，而非僅示範單一競品。

---

## 專案結構

```
pricing-project/
├── app.py                          # Streamlit dashboard
├── requirements.txt
├── .gitignore
├── src/
│   ├── demand_model.py             # 兩種需求模型（乘法型 + 競爭型線性）
│   ├── pricing_model.py            # Revenue/Cost/Profit + grid search optimizer
│   ├── visualize.py                # Plotly 畫圖函數
│   ├── competitor_analysis.py      # 比價表 + Price Alert
│   ├── strategy_simulator.py       # 策略比較（競爭型模型）
│   └── scenario_analysis.py        # 成本/彈性/競品情境分析
├── scripts/
│   └── generate_competitor_data.py # 模擬競品資料產生器
├── data/
│   └── competitor_prices.csv
└── notebooks/
    ├── 01_pricing_simulator.ipynb              # Phase 1：自身定價模型
    └── 02_competitive_strategy_analysis.ipynb  # Phase 3-6：競爭感知模型
```

---

## 作者說明

本專案為求職作品集，展示將經濟學需求理論（需求彈性、邊際分析）應用於商業定價決策的能力。開發過程採 AI 協作（Claude）進行 pair-programming 與程式除錯，方法論設計、假設驗證與商業解讀均為作者主導。

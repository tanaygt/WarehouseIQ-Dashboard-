# 📦 WarehouseIQ — Warehouse Intelligence Dashboard

> **A production-ready, industry-level supply chain analytics dashboard**  
> Built with Streamlit, Plotly, and pure Python.  
> **By Tanay Shrivastava · AI • Data • Supply Chain**

---

## 🖼 Screenshots

| Dark Mode | Light Mode |
|-----------|------------|
| Premium dark corporate UI | Clean white corporate UI |
| Accessible via sidebar toggle | Accessible via sidebar toggle |

---

## ✨ Features

### 📊 Analytics Dashboard
- **8 interactive Plotly charts** across 2 rows
- Monthly Orders & Revenue dual-axis trend
- Returns vs Orders scatter (coloured by return rate)
- Fulfillment delay bar chart with 3-hr SLA target line
- Year-on-year demand area overlay
- Side-by-side YoY comparison bars (4 metrics)
- Revenue per order trend line
- Return rate % trend with 5% benchmark
- Orders heatmap by Month × Year

### 🎛 KPI Cards
- **Total Orders** with trend vs prior year
- **Total Revenue** with trend vs prior year
- **Avg Delay** with trend direction (lower = better)
- **Total Returns** with return rate %

### 🎨 UI / UX
- **Light / Dark mode** toggle (sidebar)
- Premium corporate palette: **black, white, warm brown & gold**
- Glassmorphism-lite cards with hover lift & glow
- Custom CSS with `Playfair Display` + `DM Sans` typography
- Animated hover effects on all cards and buttons
- Responsive 4-column KPI + 2-column chart layout

### 🎛 Sidebar Filters
- **Year** multi-select (2024, 2025, 2026)
- **Month** optional multi-select filter
- All charts & KPIs update reactively
- Quick stats panel in sidebar

### 📥 Export
- Download filtered data as **timestamped CSV**

### 🧠 Smart Insights Engine
- Click **Generate Insights** to run AI analysis
- 6 auto-generated data insights with business commentary
- Year-over-year metric comparison table
- 5 strategic recommendations (Demand, Delays, Returns, Revenue, Workforce)

### 🤖 AI Assistant (Rule-Based, No API Key)
- Fully offline chatbot powered by Python logic
- Answers questions about: orders, revenue, delays, returns, trends, summary
- 4 quick-prompt buttons for one-click queries
- Persistent chat history within session
- Clear chat button

### ⚡ Performance
- `@st.cache_data` for instant data reload
- Lightweight — 4 dependencies only

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/warehouseiq-dashboard.git
cd warehouseiq-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**

---

## 📁 Project Structure

```
warehouseiq-dashboard/
├── app.py              ← Single-file full application
├── requirements.txt    ← 4 lightweight dependencies
└── README.md           ← This file
```

---

## 🛠 Tech Stack

| Layer       | Technology                  |
|-------------|-----------------------------|
| Framework   | Streamlit ≥ 1.32            |
| Charts      | Plotly ≥ 5.18               |
| Data        | Pandas ≥ 2.0 + NumPy ≥ 1.24 |
| Styling     | Custom CSS + Google Fonts   |
| AI Bot      | Rule-based Python (no API)  |

---

## 📊 Data Model

Synthetic data generated with `np.random.seed(42)` for reproducibility:

| Column           | Description                          |
|------------------|--------------------------------------|
| Year             | 2024, 2025, 2026                     |
| Month            | 1–12                                 |
| Orders           | Monthly order volume (with seasonal) |
| Revenue ($)      | Monthly revenue                      |
| Avg_Delay_Hours  | Average fulfillment delay            |
| Returns          | Units returned                       |
| Return_Rate (%)  | Returns / Orders × 100               |
| Rev_Per_Order    | Revenue / Orders                     |

---

## 💡 Chatbot Sample Questions

```
total orders summary
revenue in 2025
delay trend
return rate
year over year
best month
average delay
highest returns
full report
```

---

## 👨‍💻 Author

**Tanay Shrivastava**  
AI · Data · Supply Chain

---

## 📄 License

MIT — free to use for portfolio, interviews, and commercial projects.

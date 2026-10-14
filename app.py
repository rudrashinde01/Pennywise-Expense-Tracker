import sqlite3
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import streamlit as st
import plotly.express as px

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "expenses.db"

st.set_page_config(
    page_title="Pennywise | Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0b1120; color: #e5e7eb; }
[data-testid="stSidebar"] { background: #101a2d; border-right: 1px solid #26334b; }
[data-testid="stSidebar"] * { color: #e5e7eb; }
.block-container { padding-top: 1.7rem; padding-bottom: 2rem; max-width: 1500px; }
h1, h2, h3 { color: #f8fafc !important; }
p, label, .stMarkdown { color: #cbd5e1; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #17243a, #111c30);
    border: 1px solid #293952; border-radius: 16px;
    padding: 18px 20px; box-shadow: 0 8px 24px rgba(0,0,0,.15);
}
div[data-testid="stMetricLabel"] { color: #a9b8cc !important; }
div[data-testid="stMetricValue"] { color: #f8fafc !important; font-weight: 800; }
div[data-testid="stMetricDelta"] { color: #34d399 !important; }
.stButton > button, .stDownloadButton > button {
    border-radius: 10px; border: 1px solid #334155; font-weight: 600;
}
.stButton > button[kind="primary"] { background: #6366f1; border-color: #6366f1; color: white; }
input, textarea, [data-baseweb="select"] > div {
    background-color: #111c30 !important; color: #f8fafc !important;
}
hr { border-color: #26334b; }
.small-muted { color: #94a3b8; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Database ----------
def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the transactions table without inserting demo data."""
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                kind TEXT NOT NULL CHECK(kind IN ('Income','Expense')),
                category TEXT NOT NULL,
                txn_date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

def load_transactions():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM transactions ORDER BY txn_date DESC, id DESC").fetchall()
    return pd.DataFrame([dict(r) for r in rows])

def add_transaction(title, amount, kind, category, txn_date, notes):
    with connect() as conn:
        conn.execute("""
            INSERT INTO transactions(title, amount, kind, category, txn_date, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title.strip(), float(amount), kind, category, txn_date.isoformat(), notes.strip(),
              datetime.now().isoformat(timespec="seconds")))
        conn.commit()

def delete_transaction(transaction_id):
    with connect() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (int(transaction_id),))
        conn.commit()

init_db()
df = load_transactions()

# ---------- Helpers ----------
def money(value):
    return f"₹{value:,.2f}"

def filtered_data(data, search="", kind="All types", category="All categories", month="All months"):
    out = data.copy()
    if search.strip():
        term = search.strip().lower()
        out = out[
            out["title"].fillna("").str.lower().str.contains(term, regex=False)
            | out["category"].fillna("").str.lower().str.contains(term, regex=False)
            | out["notes"].fillna("").str.lower().str.contains(term, regex=False)
        ]
    if kind != "All types":
        out = out[out["kind"] == kind]
    if category != "All categories":
        out = out[out["category"] == category]
    if month != "All months":
        out = out[out["txn_date"].str.slice(0, 7) == month]
    return out

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 💸 Pennywise")
    st.caption("PERSONAL FINANCE")
    st.markdown("---")
    page = st.radio(
        "NAVIGATION",
        ["🏠  Dashboard", "➕  Add Transaction", "📋  Transactions", "📊  Analytics"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("### Quick overview")
    total_income = float(df.loc[df["kind"] == "Income", "amount"].sum()) if not df.empty else 0
    total_expense = float(df.loc[df["kind"] == "Expense", "amount"].sum()) if not df.empty else 0
    st.markdown(f"<p style='color:#34d399;margin-bottom:2px'>↗ Total income</p><h3 style='margin-top:0'>{money(total_income)}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#fb7185;margin-bottom:2px'>↘ Total expenses</p><h3 style='margin-top:0'>{money(total_expense)}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Your money, made clearer.")

# ---------- Dashboard ----------
if page == "🏠  Dashboard":
    st.markdown("# Good to see you 👋")
    st.markdown("<p class='small-muted'>Here’s your personal finance snapshot.</p>", unsafe_allow_html=True)

    today_month = date.today().strftime("%Y-%m")
    month_df = df[df["txn_date"].str.slice(0, 7) == today_month] if not df.empty else df
    income = float(df.loc[df["kind"] == "Income", "amount"].sum()) if not df.empty else 0
    expense = float(df.loc[df["kind"] == "Expense", "amount"].sum()) if not df.empty else 0
    month_expense = float(month_df.loc[month_df["kind"] == "Expense", "amount"].sum()) if not month_df.empty else 0
    balance = income - expense

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Balance", money(balance), "Income − expenses")
    c2.metric("🟢 Total Income", money(income))
    c3.metric("🔴 Total Expenses", money(expense))
    c4.metric("📅 This Month", money(month_expense), "Expenses")

    st.write("")
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("### Expense breakdown")
        expenses = df[df["kind"] == "Expense"] if not df.empty else df
        if not expenses.empty:
            cat = expenses.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
            fig = px.pie(cat, names="category", values="amount", hole=0.66,
                         color_discrete_sequence=["#818cf8", "#34d399", "#fb7185", "#fbbf24", "#38bdf8", "#c084fc", "#f97316"])
            fig.update_traces(textposition="outside", textinfo="percent+label", hovertemplate="%{label}<br>₹%{value:,.2f}<extra></extra>")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dbeafe", margin=dict(t=10,b=10,l=10,r=10),
                legend=dict(font=dict(color="#cbd5e1")), showlegend=True,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add an expense to see your category breakdown.")
    with right:
        st.markdown("### Recent transactions")
        if not df.empty:
            recent = df.head(6)
            for _, row in recent.iterrows():
                color = "#34d399" if row["kind"] == "Income" else "#fb7185"
                sign = "+" if row["kind"] == "Income" else "−"
                st.markdown(
                    f"""<div style="display:flex;justify-content:space-between;gap:10px;align-items:center;
                    background:#111c30;border:1px solid #26334b;border-radius:12px;padding:12px 14px;margin-bottom:9px">
                    <div><div style="font-weight:600;color:#f1f5f9">{row['title']}</div>
                    <div style="font-size:12px;color:#94a3b8">{row['category']} · {row['txn_date']}</div></div>
                    <div style="font-weight:700;color:{color};white-space:nowrap">{sign}{money(float(row['amount']))}</div>
                    </div>""", unsafe_allow_html=True
                )
        else:
            st.info("No transactions yet. Add your first transaction.")
    st.write("")
    st.markdown("### Monthly spending")
    if not df.empty:
        expenses = df[df["kind"] == "Expense"].copy()
        if not expenses.empty:
            expenses["month"] = expenses["txn_date"].str.slice(0, 7)
            monthly = expenses.groupby("month", as_index=False)["amount"].sum().sort_values("month")
            fig2 = px.bar(monthly, x="month", y="amount", labels={"month":"Month", "amount":"Expenses (₹)"},
                          color_discrete_sequence=["#818cf8"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#cbd5e1", margin=dict(t=15,b=15,l=10,r=10),
                               xaxis=dict(gridcolor="#26334b"), yaxis=dict(gridcolor="#26334b"))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.caption("Your monthly spending chart will appear after you add expenses.")

# ---------- Add transaction ----------
elif page == "➕  Add Transaction":
    st.markdown("# Add a transaction")
    st.markdown("<p class='small-muted'>Record money coming in or going out.</p>", unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("add_transaction_form", clear_on_submit=True):
            a, b = st.columns(2)
            with a:
                title = st.text_input("Transaction title *", placeholder="e.g. Lunch, monthly allowance")
                kind = st.selectbox("Transaction type *", ["Expense", "Income"])
                amount = st.number_input("Amount (₹) *", min_value=0.0, value=100.0, step=50.0, format="%.2f")
            with b:
                categories = ["Food", "Transport", "Shopping", "Education", "Entertainment", "Bills", "Health", "Allowance", "Freelance", "Salary", "Other"]
                category = st.selectbox("Category *", categories)
                txn_date = st.date_input("Date", value=date.today())
                notes = st.text_input("Notes (optional)", placeholder="Add a short note")
            submitted = st.form_submit_button("➕ Save transaction", type="primary", use_container_width=True)
            if submitted:
                if not title.strip():
                    st.error("Please enter a transaction title.")
                elif amount <= 0:
                    st.error("Amount must be greater than zero.")
                else:
                    add_transaction(title, amount, kind, category, txn_date, notes)
                    st.success("Transaction saved successfully!")
                    st.rerun()
    st.caption("Transactions are stored locally in an SQLite database on this computer.")

# ---------- Transactions ----------
elif page == "📋  Transactions":
    st.markdown("# Transactions")
    st.markdown("<p class='small-muted'>Search, filter, review, and export your records.</p>", unsafe_allow_html=True)
    all_categories = ["All categories"] + sorted(df["category"].dropna().unique().tolist()) if not df.empty else ["All categories"]
    months = sorted(df["txn_date"].str.slice(0, 7).dropna().unique().tolist(), reverse=True) if not df.empty else []
    months = ["All months"] + months
    f1, f2, f3, f4 = st.columns([2, 1, 1.3, 1.1])
    search = f1.text_input("🔎 Search", placeholder="Title, category or notes")
    kind_filter = f2.selectbox("Type", ["All types", "Income", "Expense"])
    category_filter = f3.selectbox("Category", all_categories)
    month_filter = f4.selectbox("Month", months)
    view = filtered_data(df, search, kind_filter, category_filter, month_filter) if not df.empty else df
    st.caption(f"{len(view)} transaction(s)")
    if not view.empty:
        display = view[["id", "txn_date", "title", "category", "kind", "amount", "notes"]].copy()
        display["amount"] = display.apply(lambda r: ("+" if r["kind"] == "Income" else "−") + money(float(r["amount"])), axis=1)
        display = display.rename(columns={"id":"ID", "txn_date":"Date", "title":"Title", "category":"Category", "kind":"Type", "amount":"Amount", "notes":"Notes"})
        st.dataframe(display, use_container_width=True, hide_index=True)
        csv = view[["id", "txn_date", "title", "category", "kind", "amount", "notes"]].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export filtered transactions (CSV)", csv, file_name="pennywise_transactions.csv", mime="text/csv")
        st.markdown("### Delete a transaction")
        delete_id = st.selectbox("Select transaction ID", view["id"].astype(int).tolist())
        if st.button("🗑️ Delete selected transaction", type="secondary"):
            delete_transaction(delete_id)
            st.success(f"Transaction #{delete_id} deleted.")
            st.rerun()
    else:
        st.info("No transactions match these filters.")

# ---------- Analytics ----------
elif page == "📊  Analytics":
    st.markdown("# Analytics")
    st.markdown("<p class='small-muted'>Understand where your money goes.</p>", unsafe_allow_html=True)
    if df.empty:
        st.info("Add transactions to unlock analytics.")
    else:
        expenses = df[df["kind"] == "Expense"].copy()
        income_df = df[df["kind"] == "Income"].copy()
        a, b = st.columns(2)
        with a:
            st.markdown("### Spending by category")
            if not expenses.empty:
                cat = expenses.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
                fig = px.bar(cat, x="category", y="amount", color="amount",
                             color_continuous_scale=["#818cf8", "#6366f1", "#4338ca"],
                             labels={"category":"Category", "amount":"Amount (₹)"})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font_color="#cbd5e1", coloraxis_showscale=False,
                                  margin=dict(t=10,b=10,l=10,r=10),
                                  xaxis=dict(gridcolor="#26334b"), yaxis=dict(gridcolor="#26334b"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No expenses recorded yet.")
        with b:
            st.markdown("### Income vs expenses")
            comparison = pd.DataFrame([
                {"Type":"Income", "Amount":float(income_df["amount"].sum())},
                {"Type":"Expenses", "Amount":float(expenses["amount"].sum())},
            ])
            fig2 = px.bar(comparison, x="Type", y="Amount", color="Type",
                          color_discrete_map={"Income":"#34d399", "Expenses":"#fb7185"},
                          labels={"Amount":"Amount (₹)"})
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#cbd5e1", showlegend=False,
                               margin=dict(t=10,b=10,l=10,r=10),
                               xaxis=dict(gridcolor="#26334b"), yaxis=dict(gridcolor="#26334b"))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown("### Category summary")
        if not expenses.empty:
            summary = expenses.groupby("category", as_index=False).agg(Total=("amount","sum"), Transactions=("id","count"))
            summary["Share"] = (summary["Total"] / summary["Total"].sum() * 100).round(1).astype(str) + "%"
            summary = summary.sort_values("Total", ascending=False)
            st.dataframe(summary, use_container_width=True, hide_index=True)

st.markdown("<div style='text-align:center;color:#64748b;font-size:12px;padding-top:28px'>Pennywise · Personal Expense Tracker · Built with Python and Streamlit</div>", unsafe_allow_html=True)

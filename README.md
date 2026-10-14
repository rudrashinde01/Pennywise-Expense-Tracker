# 💸 Pennywise — Personal Expense Tracker

A dark-themed personal finance web application built with Python and Streamlit. Pennywise helps users record income and expenses, manage transactions, and visualize spending through interactive charts.

## ✨ Features

* **Dashboard:** View total balance, total income, total expenses, and current-month expenses.
* **Transaction Management:** Add income and expense transactions with titles, amounts, categories, dates, and notes.
* **Transaction History:** Browse and review recorded transactions.
* **Search and Filters:** Filter transactions by title, category, transaction type, and month.
* **Expense Visualization:** View category-wise spending using an interactive doughnut chart.
* **Monthly Spending:** Visualize monthly expenses using a bar chart.
* **Analytics:** Compare income and expenses and review category-wise spending.
* **Delete Transactions:** Remove selected transaction records.
* **CSV Export:** Export filtered transactions for further analysis.
* **SQLite Database:** Store transaction records locally.
* **Dark UI:** A modern dark navy interface with interactive charts and financial summary cards.

## 🛠️ Technologies Used

* Python 3.10+
* Streamlit
* Pandas
* Plotly
* SQLite

## 📋 Requirements

* Python 3.10 or newer
* pip
* Internet connection to install the required packages

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Pennywise-Expense-Tracker.git
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Open the project directory

```bash
cd Pennywise-Expense-Tracker
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

### 5. Open in your browser

Streamlit normally opens the application automatically.

If it does not, visit:

http://localhost:8501

If that port is already in use, Streamlit may select another available port. Use the URL displayed in your terminal.

## 💾 Data Storage

Pennywise uses SQLite to store transactions in a local database named `expenses.db`.

* The database is created automatically when the application initializes.
* No sample transactions are inserted automatically.
* The dashboard starts with zero income and expenses when the database is empty.
* Transactions are stored locally in the database file.

**Note:** The local SQLite database is excluded from the Git repository. Each installation maintains its own local transaction records.

## 📁 Project Structure

```text
Pennywise-Expense-Tracker/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── expenses.db
```

The database file is created locally when the application runs and should not be uploaded to a public repository.

## 🔒 Privacy

Transaction records are stored in the local SQLite database. Avoid committing personal financial information, database files, credentials, or secrets to GitHub.

## 👨‍💻 Project Information

**Project:** Pennywise — Personal Expense Tracker
**Language:** Python
**Framework:** Streamlit
**Database:** SQLite

---

Built with Python and Streamlit.

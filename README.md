# 🩺 Data Doctor – Clean & Analyze Your Data Instantly

**Data Doctor** is an interactive Streamlit web app that lets you upload messy CSVs, clean the data, and generate a full Exploratory Data Analysis (EDA) report — all without writing a single line of code.

---

## 🚀 Features

- 📂 Upload CSV files
- 🧼 Clean data:
  - Remove duplicate rows
  - Fill missing values (mode/median)
  - Convert date-like columns
  - Optionally remove outliers (IQR method)
- 🔍 Visualize missing data (heatmap + summary)
- 📊 Generate automated EDA reports using `ydata-profiling`
- 📥 Download the cleaned dataset

---

## 🧰 Tech Stack

- Python
- Streamlit
- Pandas
- Seaborn
- Matplotlib
- ydata-profiling

---

## 💻 Run Locally

```bash
# Clone the repo
git clone https://github.com/princee14/princee14-data-doctor.git
cd princee14-data-doctor

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

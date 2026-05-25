# 🚀 Delivery Optimization Platform

> Enterprise-grade data engineering platform for delivery operations intelligence — built with AWS S3, dbt, Apache Airflow, and XGBoost ML models.

---

## 📊 Live Dashboard
> Built with Streamlit — runs locally after setup

---

## 🏗️ Architecture

```
Data Generation (Python + Faker)
        ↓
AWS S3 Data Lake (Bronze Layer)
        ↓
dbt Transformations (Silver + Gold)
        ↓
ML Models (XGBoost)
        ↓
Airflow Orchestration (Docker)
        ↓
Streamlit Dashboard
```

---

## ⚡ What This Platform Does

| Feature | Description |
|---|---|
| 🔮 Delay Prediction | XGBoost model predicts order delays with 79.3% accuracy |
| 📈 Demand Forecasting | Forecasts order volume per zone with 98.1% accuracy |
| 🗺️ Zone Intelligence | Identifies high-risk areas in real-time |
| 👨‍✈️ Captain Analytics | Tracks and ranks captain performance |
| ⚙️ Auto Pipeline | Airflow DAG runs the full pipeline daily |

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Data Generation | Python, Faker, Pandas |
| Cloud Storage | AWS S3 |
| Data Warehouse | DuckDB |
| Transformations | dbt-core |
| Orchestration | Apache Airflow, Docker |
| Machine Learning | XGBoost, Scikit-learn |
| Dashboard | Streamlit, Plotly |
| Version Control | Git, GitHub |

---

## 📁 Project Structure

```
delivery-optimization/
├── src/
│   ├── generator.py          # Generates 50,000 realistic orders
│   ├── analysis.py           # Operational analysis queries
│   ├── upload_to_s3.py       # Uploads data to AWS S3
│   ├── ml_model.py           # Delay prediction model (XGBoost)
│   ├── ml_demand.py          # Demand forecasting model
│   └── dashboard.py          # Streamlit dashboard
├── delivery_dbt/
│   ├── models/staging/       # Staging models (Bronze → Silver)
│   └── models/marts/         # Mart models (Silver → Gold)
├── airflow_project/
│   └── dags/                 # Airflow DAGs
├── models/                   # Saved ML models (.pkl)
├── data/
│   ├── raw/                  # CSV files
│   └── delivery.db           # DuckDB database
└── docker-compose.yml        # Airflow + Docker setup
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/meshal-ahmad/delivery-optimization-platform.git
cd delivery-optimization-platform

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install faker pandas duckdb pyarrow boto3 python-dotenv
pip install dbt-core dbt-duckdb
pip install scikit-learn xgboost joblib
pip install streamlit plotly

# 4. Generate data
python src/generator.py

# 5. Run dbt transformations
cd delivery_dbt
dbt run
dbt test

# 6. Train ML models
cd ..
python src/ml_model.py
python src/ml_demand.py

# 7. Launch dashboard
streamlit run src/dashboard.py
```

---

## 📈 ML Model Results

| Model | Metric | Score |
|---|---|---|
| Delay Prediction | Accuracy | 79.3% |
| Delay Prediction | F1 Score | 80.0% |
| Demand Forecasting | MAPE | 1.9% |

### Key Findings
- **Prep time** is the #1 delay factor (41.2% importance)
- **Stormy weather** increases delay rate to 67.2%
- **Peak hours** (19:00–21:00) show highest delay risk

---

## 🔄 Airflow Pipeline

```
generate_data → run_analysis → run_ml_model
```

Runs daily at 01:00 UTC via Apache Airflow on Docker.

---

## 👤 Author

**Meshal Ahmad**  
Data Engineer

[![GitHub](https://img.shields.io/badge/GitHub-meshal--ahmad-blue)](https://github.com/meshal-ahmad)

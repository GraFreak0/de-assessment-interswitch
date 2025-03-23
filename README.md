# Apache Airflow Data Pipeline

## Overview
This project implements an Apache Airflow data pipeline for fetching trip metrics from ClickHouse, processing the data, and storing it in an SQLite database. The pipeline is orchestrated using Airflow DAGs and consists of two main tasks:

1. **Fetch Trip Metrics**: Retrieves data from ClickHouse via an HTTP API.
2. **Load Data into SQLite**: Processes and stores the data in an SQLite database.

## Pipeline Workflow
1. **Extract**: Fetch trip metrics from ClickHouse.
2. **Transform**: Process the data and assign appropriate column names.
3. **Load**: Store the structured data in an SQLite database.

## Project Structure
```
root/
│── airflow/
│   │── dags/ 
│   │   └── trip_metrics_dag.py  # Airflow DAG script
│   │── db/
│   │   └── clickHouseQuery.sql  # Clickhouse Query
│   │── airflow.cfg               # Airflow configuration file
│   │── airflow.db               # Airflow db file
│   │── standalone_admin_password.txt    # Airflow admin password
│   │── trip_metrics.db       # Trip metrics SQLite DB
│   └── webserver_config.py   # Webserver Configuration File
│── docker-compose.yaml       # YAML File for Docker Compose
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation
└── Dockerfile                # Dockerfile for building the image
```

## Prerequisites
Before running the Airflow pipeline, ensure the following dependencies are installed:

- **Apache Airflow**
- **Python 3.9+**
- **SQLite**
- **ClickHouse (HTTP API Enabled)**
- **Docker Desktop**
- **VS Code** (install `Docker` extension for VS Code)
- **Required Python Packages** (see `requirements.txt`)

## Airflow Configuration

### Install Airflow & Dependencies
```bash
pip install apache-airflow
pip install pandas requests sqlite3
```

### Airflow Initialization & Setup
```bash
export AIRFLOW_HOME=~/airflow
airflow db init
airflow users create \
    --username admin \
    --password admin \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email admin@example.com
```

### Start Airflow Services
```bash
airflow scheduler &
airflow webserver --port 8080
```

### Airflow Configuration File (`airflow.cfg`)
Ensure the configuration file is set up with the appropriate executor and database settings.

## DAG Implementation

### `trip_metrics_dag.py`
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
import pandas as pd
import sqlite3
import requests
import io
import os
from datetime import datetime

# Database Path
SQLITE_DB_PATH = os.path.join(os.getcwd(), "trip_metrics.db")
COLUMN_NAMES = ["month", "sat_mean_trip_count", "sat_mean_fare_per_trip", "sat_mean_duration_per_trip",
                "sun_mean_trip_count", "sun_mean_fare_per_trip", "sun_mean_duration_per_trip"]

# ClickHouse Query
CLICKHOUSE_QUERY = """SQL QUERY HERE"""

def fetch_trip_metrics(**kwargs):
    conn = BaseHook.get_connection("clickhouse_default")
    url = f"{conn.host}:{conn.port}/?user={conn.login}&password={conn.password}&database={conn.schema}"
    response = requests.post(url, data=CLICKHOUSE_QUERY.encode("utf-8"), headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text), sep="\t")
        df.columns = COLUMN_NAMES
        ti = kwargs['ti']
        ti.xcom_push(key='trip_data', value=df.to_json(orient='records'))
    else:
        raise Exception("Failed to fetch data from ClickHouse")

def load_metrics_to_sqlite(**kwargs):
    ti = kwargs['ti']
    data_json = ti.xcom_pull(task_ids='fetch_trip_metrics', key='trip_data')
    df = pd.read_json(io.StringIO(data_json), orient="records")
    df.columns = COLUMN_NAMES
    conn = sqlite3.connect(SQLITE_DB_PATH)
    df.to_sql("trip_metrics", conn, if_exists="replace", index=False)
    conn.close()

# Define DAG
default_args = {"owner": "airflow", "start_date": datetime(2025, 3, 21), "catchup": False}
dag = DAG("trip_metrics_pipeline", default_args=default_args, schedule="@monthly", catchup=False)

fetch_data = PythonOperator(task_id="fetch_trip_metrics", python_callable=fetch_trip_metrics, dag=dag)
load_data = PythonOperator(task_id="load_metrics_to_sqlite", python_callable=load_metrics_to_sqlite, dag=dag)
fetch_data >> load_data
```

## Deployment
1. **Ensure Airflow is Running**
```bash
airflow scheduler &
airflow webserver --port 8080
```

2. **Deploy the DAG**
Copy the `trip_metrics_dag.py` file to the `dags/` directory:
```bash
cp trip_metrics_dag.py ~/airflow/dags/
```

3. **Trigger DAG Execution**
```bash
airflow dags list
airflow dags trigger trip_metrics_pipeline
```

## Monitoring & Logs
To check DAG execution logs:
```bash
airflow tasks logs trip_metrics_pipeline fetch_trip_metrics
```

## Conclusion
This pipeline automates data extraction from ClickHouse and storage in SQLite using Apache Airflow. It ensures a structured workflow for data processing and storage.
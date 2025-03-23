import io
import os
import requests
import pandas as pd
import sqlite3
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.models import Variable

# SQLITE_DB_PATH = "/airflow/db/trip_metrics.db"
SQLITE_DB_PATH = os.path.join(os.getcwd(), "trip_metrics.db")

COLUMN_NAMES = [
    "month",
    "sat_mean_trip_count",
    "sat_mean_fare_per_trip",
    "sat_mean_duration_per_trip",
    "sun_mean_trip_count",
    "sun_mean_fare_per_trip",
    "sun_mean_duration_per_trip"
]

CLICKHOUSE_QUERY = """
WITH trip_metrics AS (
    SELECT 
        DATE_FORMAT(pickup_datetime, '%Y-%m') AS month,
        DAYOFWEEK(pickup_datetime) AS day_of_week,
        COUNT(*) AS total_trips,
        AVG(fare_amount) AS avg_fare_per_trip,
        AVG(TIMESTAMPDIFF(MINUTE, pickup_datetime, dropoff_datetime)) AS avg_duration_per_trip
    FROM tripdata
    WHERE pickup_datetime BETWEEN '2014-01-01' AND '2016-12-31'
    GROUP BY month, day_of_week
)
SELECT 
    month,
    AVG(CASE WHEN day_of_week = 7 THEN total_trips END) AS sat_mean_trip_count,
    AVG(CASE WHEN day_of_week = 7 THEN avg_fare_per_trip END) AS sat_mean_fare_per_trip,
    AVG(CASE WHEN day_of_week = 7 THEN avg_duration_per_trip END) AS sat_mean_duration_per_trip,
    AVG(CASE WHEN day_of_week = 1 THEN total_trips END) AS sun_mean_trip_count,
    AVG(CASE WHEN day_of_week = 1 THEN avg_fare_per_trip END) AS sun_mean_fare_per_trip,
    AVG(CASE WHEN day_of_week = 1 THEN avg_duration_per_trip END) AS sun_mean_duration_per_trip
FROM trip_metrics
GROUP BY month
ORDER BY month;
"""

def fetch_trip_metrics(**kwargs):
    """Fetch trip metrics from ClickHouse and push data to XCom."""
    try:
        conn = BaseHook.get_connection("clickhouse_default")
        clickhouse_url = f"{conn.host}:{conn.port}/?user={conn.login}&password={conn.password}&database={conn.schema}"

        response = requests.post(
            url=clickhouse_url,
            data=CLICKHOUSE_QUERY.encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text), sep="\t")
            
            data_json = df.to_json()
            kwargs['ti'].xcom_push(key="trip_data", value=data_json)

            print("Data successfully fetched and pushed to XCom.")
        else:
            raise Exception(f"Failed to fetch data from ClickHouse: {response.text}")

    except Exception as e:
        print(f"⚠️ Error fetching data: {str(e)}")
        raise

def load_metrics_to_sqlite(**kwargs):
    """Load trip metrics data from XCom into SQLite with correct column names."""
    try:
        # Fetch data from XCom
        ti = kwargs['ti']
        data_json = ti.xcom_pull(task_ids='fetch_trip_metrics', key='trip_data')

        if not data_json:
            raise ValueError("No data received from XCom.")

        df = pd.read_json(io.StringIO(data_json), orient="records")

        df.columns = COLUMN_NAMES

        # Connect to SQLite and insert data
        conn = sqlite3.connect(SQLITE_DB_PATH)
        df.to_sql("trip_metrics", conn, if_exists="replace", index=False)
        conn.close()
        print(f"Data successfully loaded into SQLite at {SQLITE_DB_PATH}.")
    except Exception as e:
        print(f"Error loading data into SQLite: {str(e)}")
        raise

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 3, 21),
    "catchup": False
}

dag = DAG(
    "trip_metrics_pipeline",
    default_args=default_args,
    schedule="@daily",
    catchup=False
)

fetch_data = PythonOperator(
    task_id="fetch_trip_metrics",
    python_callable=fetch_trip_metrics,
    provide_context=True,
    dag=dag
)

load_data = PythonOperator(
    task_id="load_metrics_to_sqlite",
    python_callable=load_metrics_to_sqlite,
    provide_context=True,
    dag=dag
)

fetch_data >> load_data
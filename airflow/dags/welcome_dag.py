import requests
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.models import Variable

def print_welcome():
    print("Welcome to the Airflow platform!")

def print_date():
    print(f"Execution date is {datetime.now()}")

def print_random_quote():
    response = requests.get("https://api.quotable.io/random")
    quote = response.json()["content"]
    print('Quote of the day: "{}"'.fromat(quote))

dag = DAG(
    dag_id="welcome_dag",
    default_args = {'start_date': days_ago(1)},
    schedule_interval='0 23 * * *',
    catchup=False
)

print_welcome_task = PythonOperator(
    task_id="print_welcome",
    python_callable=print_welcome,
    dag=dag
)

print_date_task = PythonOperator(
    task_id="print_date",
    python_callable=print_date,
    dag=dag
)

print_random_quote_task = PythonOperator(
    task_id="print_random_quote",
    python_callable=print_random_quote,
    dag=dag
)

print_welcome_task >> print_date_task >> print_random_quote_task